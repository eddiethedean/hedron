"""Streamable HTTP transport for deny-by-default MCP projection."""

from __future__ import annotations

import json
import uuid
from collections.abc import Callable, Mapping
from typing import Any

from hedron_mcp.bounds import BoundsError
from hedron_mcp.compat import (
    UNSUPPORTED_CAPABILITY_BEHAVIOR,
    negotiate_protocol_version,
)

PrincipalResolver = Callable[[Any], str | None]
# Starlette/FastAPI Request-like object.


def _json_response(payload: Mapping[str, Any], *, status_code: int = 200) -> Any:
    from starlette.responses import JSONResponse

    return JSONResponse(dict(payload), status_code=status_code)


def _error(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _result(req_id: Any, result: Mapping[str, Any] | list[Any] | None) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


async def handle_mcp_http(request: Any, projection: Any) -> Any:
    """Handle one Streamable HTTP MCP JSON-RPC request."""
    if not projection.enabled:
        return _json_response({"error": "MCP projection disabled"}, status_code=404)

    raw = await request.body()
    try:
        projection.bounds.check_size(raw)
    except BoundsError as exc:
        return _json_response({"error": str(exc)}, status_code=413)

    origin = request.headers.get("origin")
    if projection.allowed_origins is not None and (
        origin is None or origin not in projection.allowed_origins
    ):
        return _json_response({"error": "origin not allowed"}, status_code=403)

    try:
        body = json.loads(raw.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _json_response(_error(None, -32700, "parse error"), status_code=400)

    if not isinstance(body, dict):
        return _json_response(_error(None, -32600, "invalid request"), status_code=400)

    req_id = body.get("id")
    method = str(body.get("method") or "")
    raw_params = body.get("params")
    params: dict[str, Any] = raw_params if isinstance(raw_params, dict) else {}

    principal = projection.resolve_principal(request)
    request_id = projection.bounds.new_request_id()
    session_id = request.headers.get("mcp-session-id") or uuid.uuid4().hex

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
        if projection.bounds.is_cancelled(request_id):
            raise BoundsError("MCP request cancelled")

        if method in {"initialize", "notifications/initialized"}:
            version = negotiate_protocol_version(params.get("protocolVersion"))
            caps = (
                params.get("capabilities") if isinstance(params.get("capabilities"), dict) else {}
            )
            # Ignore unsupported client capabilities (documented behavior).
            _ = caps
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
            if method == "notifications/initialized":
                return _json_response({"ok": True})
            return _json_response(
                _result(
                    req_id,
                    {
                        "protocolVersion": version,
                        "capabilities": {"resources": {}, "tools": {}},
                        "serverInfo": {"name": "hedron-mcp", "version": projection.package_version},
                    },
                )
            )

        # All subsequent methods require authz.
        projection.authorize(
            principal=principal,
            action=method,
            resource=params.get("uri") or params.get("name"),
            tenant_id=_tenant_from(request, params),
            scopes=_scopes_from(request),
        )

        if method == "resources/list":
            resources = [
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
            return _json_response(_result(req_id, {"resources": resources}))

        if method == "resources/read":
            uri = str(params.get("uri") or "")
            content = projection.read_resource(uri, principal=principal)
            projection.audit.emit(
                code="HED-MCP-READ-RESOURCE",
                kind="execution",
                principal=principal,
                detail={"uri": uri},
            )
            return _json_response(
                _result(
                    req_id,
                    {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": content.get("mimeType", "application/json"),
                                "text": content.get("text", ""),
                            }
                        ]
                    },
                )
            )

        if method == "tools/list":
            tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": dict(tool.schema),
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
            return _json_response(_result(req_id, {"tools": tools}))

        if method == "tools/call":
            name = str(params.get("name") or "")
            arguments = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
            result = projection.call_tool(name, arguments, principal=principal)
            projection.audit.emit(
                code="HED-MCP-CALL-TOOL",
                kind="execution",
                principal=principal,
                detail={"name": name},
            )
            return _json_response(
                _result(
                    req_id,
                    {"content": [{"type": "text", "text": json.dumps(result)}], "isError": False},
                )
            )

        if method in {"shutdown", "notifications/cancelled"}:
            if method == "notifications/cancelled":
                cancel_id = str(params.get("requestId") or request_id)
                projection.bounds.request_cancel(cancel_id)
                projection.audit.emit(
                    code="HED-MCP-CANCEL",
                    kind="cancellation",
                    principal=principal,
                    detail={"request_id": cancel_id},
                )
            projection.bounds.close_session(session_id)
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


def _tenant_from(request: Any, params: Mapping[str, Any]) -> str | None:
    header = request.headers.get("x-hedron-tenant")
    if header:
        return header
    tenant = params.get("tenant_id")
    return str(tenant) if tenant is not None else None


def _scopes_from(request: Any) -> Mapping[str, Any] | None:
    raw = request.headers.get("x-hedron-scopes")
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def mount_streamable_http(
    app: Any,
    projection: Any,
    *,
    path: str = "/mcp",
) -> None:
    """Mount Streamable HTTP MCP routes on a Starlette/FastAPI app."""
    from starlette.requests import Request
    from starlette.routing import Route

    async def endpoint(request: Request) -> Any:
        return await handle_mcp_http(request, projection)

    route = Route(path, endpoint=endpoint, methods=["POST", "DELETE"])
    # FastAPI / Starlette both expose .routes; prefer router include when present.
    router = getattr(app, "router", None)
    if router is not None and hasattr(router, "routes"):
        router.routes.append(route)
    elif hasattr(app, "routes"):
        app.routes.append(route)
    else:
        raise TypeError("mount_mcp requires a Starlette/FastAPI-like application")
