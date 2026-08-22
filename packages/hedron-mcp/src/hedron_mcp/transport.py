"""Streamable HTTP transport for deny-by-default MCP projection."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterable, Callable, Mapping
from typing import Protocol, cast

from typing_extensions import TypeIs

from hedron_core.typing_aliases import JsonObject, JsonValue
from hedron_mcp.bounds import BoundsError
from hedron_mcp.compat import (
    UNSUPPORTED_CAPABILITY_BEHAVIOR,
    negotiate_protocol_version,
)
from hedron_mcp.server import InvalidParamsError, McpProjection

PrincipalResolver = Callable[[object], str | None]


class McpHttpRequest(Protocol):
    """Starlette/FastAPI Request-like object used by the MCP transport."""

    @property
    def headers(self) -> Mapping[str, str]: ...

    @property
    def method(self) -> str: ...

    async def body(self) -> bytes: ...

    def stream(self) -> AsyncIterable[bytes]: ...


def _is_json_value(value: object) -> TypeIs[JsonValue]:
    if value is None or isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, list):
        return all(_is_json_value(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _is_json_value(item) for key, item in value.items())
    return False


def _rpc_id(value: object) -> JsonValue:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _as_json_object(value: object) -> JsonObject:
    if isinstance(value, dict) and all(
        isinstance(key, str) and _is_json_value(item) for key, item in value.items()
    ):
        return value
    if isinstance(value, Mapping):
        out: JsonObject = {}
        for key, item in value.items():
            out[str(key)] = item if _is_json_value(item) else str(item)
        return out
    return {}


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def _json_response(
    payload: Mapping[str, JsonValue],
    *,
    status_code: int = 200,
    headers: Mapping[str, str] | None = None,
) -> object:
    from starlette.responses import JSONResponse

    return JSONResponse(dict(payload), status_code=status_code, headers=dict(headers or {}))


def _error(req_id: object, code: int, message: str) -> JsonObject:
    return {
        "jsonrpc": "2.0",
        "id": _rpc_id(req_id),
        "error": {"code": code, "message": message},
    }


def _result(req_id: object, result: JsonValue) -> JsonObject:
    return {"jsonrpc": "2.0", "id": _rpc_id(req_id), "result": result}


def _cancel_key(req_id: object) -> str | None:
    """Normalize JSON-RPC ids to the cancel-registry key clients know about (#171)."""
    if req_id is None:
        return None
    return str(req_id)


def _cancel_owner(*, session_id: str | None, principal: str | None) -> str | None:
    """Scope cancel marks to a session or authenticated principal (#217, #288)."""
    if session_id:
        return f"session:{session_id}"
    if principal:
        return f"principal:{principal}"
    return None


def _raise_if_cancelled(
    projection: McpProjection,
    cancel_key: str | None,
    *,
    owner: str | None,
) -> None:
    if cancel_key and owner and projection.bounds.is_cancelled(cancel_key, owner=owner):
        raise BoundsError("MCP request cancelled")


def _origin_forbidden(request: McpHttpRequest, projection: McpProjection) -> bool:
    origin = request.headers.get("origin")
    if projection.allowed_origins is None:
        # Fail closed for browser-facing requests when no allowlist is configured (#232).
        return origin is not None
    return origin is None or origin not in projection.allowed_origins


async def _read_body_bounded(request: McpHttpRequest, max_bytes: int) -> bytes:
    """Read request body without buffering more than ``max_bytes`` (#233)."""
    chunks: list[bytes] = []
    total = 0
    stream = getattr(request, "stream", None)
    if callable(stream):
        # Protocol declares stream(); getattr keeps stubs without it working at runtime.
        chunk_stream = cast(Callable[[], AsyncIterable[bytes]], stream)
        async for chunk in chunk_stream():
            total += len(chunk)
            if total > max_bytes:
                raise BoundsError(f"MCP request exceeds max_request_bytes={max_bytes}")
            chunks.append(chunk)
        return b"".join(chunks)
    raw = await request.body()
    if len(raw) > max_bytes:
        raise BoundsError(f"MCP request exceeds max_request_bytes={max_bytes}")
    return raw


def _enforce_session_principal(
    projection: McpProjection,
    *,
    session_id: str | None,
    principal: str | None,
) -> None:
    """Reject silent principal switches on an existing MCP session (#173)."""
    if not session_id:
        return
    sess = projection.bounds.session(session_id)
    if sess is None:
        raise KeyError("MCP session not found")
    stored = str(sess.get("principal") or "")
    current = principal or ""
    if stored != current:
        raise PermissionError("MCP session principal mismatch")


async def _handle_session_delete(request: McpHttpRequest, projection: McpProjection) -> object:
    """Terminate the Streamable HTTP session identified by ``mcp-session-id``."""
    session_id = request.headers.get("mcp-session-id")
    if not session_id:
        return _json_response({"error": "mcp-session-id required"}, status_code=400)
    if _origin_forbidden(request, projection):
        return _json_response({"error": "origin not allowed"}, status_code=403)

    principal = projection.resolve_principal(request)
    try:
        projection.bounds.check_rate(principal or "anonymous")
        projection.bounds.acquire()
    except BoundsError as exc:
        return _json_response({"error": str(exc)}, status_code=429)

    try:
        _enforce_session_principal(projection, session_id=session_id, principal=principal)
        projection.bounds.close_session(session_id)
        projection.audit.emit(
            code="HED-MCP-SESSION-DELETE",
            kind="cancellation",
            principal=principal,
            detail={"session_id": session_id},
        )
        from starlette.responses import Response

        return Response(status_code=204)
    except PermissionError as exc:
        projection.audit.emit(
            code="HED-MCP-AUTHZ",
            kind="authorization",
            principal=principal,
            detail={"error": str(exc), "method": "DELETE"},
        )
        return _json_response({"error": str(exc)}, status_code=403)
    except KeyError as exc:
        return _json_response({"error": str(exc)}, status_code=404)
    finally:
        projection.bounds.release()


async def handle_mcp_http(request: McpHttpRequest, projection: McpProjection) -> object:
    """Handle one Streamable HTTP MCP JSON-RPC request."""
    if not projection.enabled:
        return _json_response({"error": "MCP projection disabled"}, status_code=404)

    if request.method == "DELETE":
        return await _handle_session_delete(request, projection)

    try:
        raw = await _read_body_bounded(request, projection.bounds.max_request_bytes)
        projection.bounds.check_size(raw)
    except BoundsError as exc:
        return _json_response({"error": str(exc)}, status_code=413)

    if _origin_forbidden(request, projection):
        return _json_response({"error": "origin not allowed"}, status_code=403)

    try:
        body = json.loads(raw.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _json_response(_error(None, -32700, "parse error"), status_code=400)

    if not isinstance(body, dict):
        return _json_response(_error(None, -32600, "invalid request"), status_code=400)

    body_obj = _as_json_object(body)
    req_id = body_obj.get("id")
    method = str(body_obj.get("method") or "")
    raw_params = body_obj.get("params")
    params: JsonObject = _as_json_object(raw_params) if isinstance(raw_params, dict) else {}

    principal = projection.resolve_principal(request)
    # Cancel keys are the client-visible JSON-RPC id, not a private server UUID (#171).
    cancel_key = _cancel_key(req_id)
    client_session_id = request.headers.get("mcp-session-id")
    origin = request.headers.get("origin")
    cancel_owner = _cancel_owner(session_id=client_session_id, principal=principal)

    try:
        projection.bounds.check_rate(principal or "anonymous")
        projection.bounds.acquire()
    except BoundsError as exc:
        projection.audit.emit(
            code="HED-MCP-BOUNDS",
            kind="failure",
            principal=principal,
            detail={"error": str(exc), "method": method},
        )
        return _json_response({"error": str(exc)}, status_code=429)

    try:
        if method not in {"notifications/cancelled"}:
            _raise_if_cancelled(projection, cancel_key, owner=cancel_owner)

        if method == "notifications/initialized":
            # This notification completes the existing initialize handshake; it
            # must never mint a replacement session or evict the active one.
            _enforce_session_principal(
                projection,
                session_id=client_session_id,
                principal=principal,
            )
            return _json_response({"ok": True})

        if method == "initialize":
            version = negotiate_protocol_version(_optional_str(params.get("protocolVersion")))
            caps = (
                params.get("capabilities") if isinstance(params.get("capabilities"), dict) else {}
            )
            # Ignore unsupported client capabilities (documented behavior).
            _ = caps
            # Server-minted session ids — never bind unbound client-chosen values (#173).
            session_id = uuid.uuid4().hex
            projection.bounds.open_session(session_id, principal=principal or "", origin=origin)
            projection.audit.emit(
                code="HED-MCP-INIT",
                kind="registration",
                principal=principal,
                detail={
                    "session_id": session_id,
                    "protocolVersion": version,
                    "unsupported_capability_behavior": UNSUPPORTED_CAPABILITY_BEHAVIOR,
                },
            )
            session_headers = {"mcp-session-id": session_id}
            if method == "notifications/initialized":
                return _json_response({"ok": True}, headers=session_headers)
            return _json_response(
                _result(
                    req_id,
                    {
                        "protocolVersion": version,
                        "capabilities": {"resources": {}, "tools": {}},
                        "serverInfo": {"name": "hedron-mcp", "version": projection.package_version},
                    },
                ),
                headers=session_headers,
            )

        # When a session header is present, enforce principal binding (#173).
        _enforce_session_principal(projection, session_id=client_session_id, principal=principal)

        # All subsequent methods require authz.
        projection.authorize(
            principal=principal,
            action=method,
            resource=_optional_str(params.get("uri") or params.get("name")),
            tenant_id=_tenant_from(request, params),
            scopes=_scopes_from(request),
        )

        if method == "resources/list":
            resources: list[JsonValue] = [
                {
                    "uri": item.uri,
                    "name": item.name,
                    "description": item.description,
                    "mimeType": item.mime_type,
                }
                for item in projection.list_resources()
            ]
            projection.audit.emit(
                code="HED-MCP-LIST-RESOURCES",
                kind="execution",
                principal=principal,
                detail={"count": len(resources)},
            )
            result_payload: JsonObject = {"resources": resources}
            return _json_response(_result(req_id, result_payload))

        if method == "resources/read":
            _raise_if_cancelled(projection, cancel_key, owner=cancel_owner)
            uri = str(params.get("uri") or "")
            content = projection.read_resource(uri, principal=principal)
            projection.audit.emit(
                code="HED-MCP-READ-RESOURCE",
                kind="execution",
                principal=principal,
                detail={"uri": uri},
            )
            if cancel_key and cancel_owner:
                projection.bounds.clear_cancel(cancel_key, owner=cancel_owner)
            return _json_response(
                _result(
                    req_id,
                    {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": str(content.get("mimeType", "application/json")),
                                "text": str(content.get("text", "")),
                            }
                        ]
                    },
                )
            )

        if method == "tools/list":
            tools: list[JsonValue] = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": _as_json_object(dict(tool.schema)),
                    "annotations": {"readOnlyHint": not tool.mutate},
                }
                for tool in projection.list_tools()
            ]
            projection.audit.emit(
                code="HED-MCP-LIST-TOOLS",
                kind="execution",
                principal=principal,
                detail={"count": len(tools)},
            )
            tools_payload: JsonObject = {"tools": tools}
            return _json_response(_result(req_id, tools_payload))

        if method == "tools/call":
            _raise_if_cancelled(projection, cancel_key, owner=cancel_owner)
            name = str(params.get("name") or "")
            raw_arguments = params.get("arguments")
            arguments = _as_json_object(raw_arguments) if isinstance(raw_arguments, dict) else {}
            result = projection.call_tool(name, arguments, principal=principal)
            projection.audit.emit(
                code="HED-MCP-CALL-TOOL",
                kind="execution",
                principal=principal,
                detail={"name": name},
            )
            if cancel_key and cancel_owner:
                projection.bounds.clear_cancel(cancel_key, owner=cancel_owner)
            return _json_response(
                _result(
                    req_id,
                    {
                        "content": [{"type": "text", "text": json.dumps(result)}],
                        "isError": False,
                    },
                )
            )

        if method == "notifications/cancelled":
            raw_cancel = params.get("requestId")
            if raw_cancel is None:
                return _json_response(
                    _error(req_id, -32602, "notifications/cancelled requires params.requestId"),
                    status_code=400,
                )
            if not cancel_owner:
                return _json_response(
                    _error(
                        req_id,
                        -32600,
                        "notifications/cancelled requires mcp-session-id or a principal",
                    ),
                    status_code=403,
                )
            cancel_id = str(raw_cancel)
            projection.bounds.request_cancel(cancel_id, owner=cancel_owner)
            projection.audit.emit(
                code="HED-MCP-CANCEL",
                kind="cancellation",
                principal=principal,
                detail={"request_id": cancel_id, "owner": cancel_owner},
            )
            # Cancel marks a request; it must not tear down the MCP session.
            return _json_response({"ok": True})

        if method == "shutdown":
            if client_session_id:
                projection.bounds.close_session(client_session_id)
            return _json_response(_result(req_id, {}))

        return _json_response(
            _error(req_id, -32601, f"method not found: {method}"), status_code=404
        )
    except BoundsError as exc:
        projection.audit.emit(
            code="HED-MCP-BOUNDS",
            kind="failure",
            principal=principal,
            detail={"error": str(exc), "method": method},
        )
        return _json_response(_error(req_id, -32000, str(exc)), status_code=429)
    except PermissionError as exc:
        projection.audit.emit(
            code="HED-MCP-AUTHZ",
            kind="authorization",
            principal=principal,
            detail={"error": str(exc), "method": method},
        )
        return _json_response(_error(req_id, -32001, str(exc)), status_code=403)
    except InvalidParamsError as exc:
        projection.audit.emit(
            code="HED-MCP-INVALID-PARAMS",
            kind="failure",
            principal=principal,
            detail={"error": str(exc), "method": method},
        )
        return _json_response(_error(req_id, -32602, str(exc)), status_code=400)
    except KeyError as exc:
        projection.audit.emit(
            code="HED-MCP-NOT-FOUND",
            kind="failure",
            principal=principal,
            detail={"error": str(exc), "method": method},
        )
        return _json_response(_error(req_id, -32002, str(exc)), status_code=404)
    except Exception as exc:  # noqa: BLE001 — map to JSON-RPC failure
        projection.audit.emit(
            code="HED-MCP-FAIL",
            kind="failure",
            principal=principal,
            detail={"error": str(exc), "method": method},
        )
        return _json_response(_error(req_id, -32000, "internal error"), status_code=500)
    finally:
        projection.bounds.release()


def _tenant_from(request: McpHttpRequest, params: Mapping[str, JsonValue]) -> str | None:
    """Ignore client tenant claims; tenant is derived server-side (#287)."""
    del request, params
    return None


def _scopes_from(request: McpHttpRequest) -> Mapping[str, JsonValue] | None:
    """Ignore client-supplied scope headers (#287)."""
    del request
    return None


def mount_streamable_http(
    app: object,
    projection: McpProjection,
    *,
    path: str = "/mcp",
) -> None:
    """Mount Streamable HTTP MCP routes on a Starlette/FastAPI app."""
    from starlette.requests import Request
    from starlette.routing import Route

    async def endpoint(request: Request) -> object:
        return await handle_mcp_http(request, projection)

    route = Route(path, endpoint=endpoint, methods=["POST", "DELETE"])
    # FastAPI / Starlette both expose .routes; prefer router include when present.
    router = getattr(app, "router", None)
    router_routes = getattr(router, "routes", None) if router is not None else None
    if isinstance(router_routes, list):
        router_routes.append(route)
        return
    app_routes = getattr(app, "routes", None)
    if isinstance(app_routes, list):
        app_routes.append(route)
        return
    raise TypeError("mount_mcp requires a Starlette/FastAPI-like application")
