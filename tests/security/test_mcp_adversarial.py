"""Adversarial MCP suites for AUTHZ-032 / REVIEW-032."""

from __future__ import annotations

import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient

from hedron_mcp import AuthorizationError, McpProjection, McpResource, McpTool, mount_mcp


def test_confused_deputy_cannot_widen_principal() -> None:
    projection = McpProjection(enabled=True)
    with pytest.raises(AuthorizationError, match="never exceeds"):
        projection.check_authz(
            principal="alice",
            action="tools/call",
            scopes={"principal": "admin"},
        )


def test_cross_tenant_observation_denied() -> None:
    def tenant_hook(**kwargs: object) -> None:
        if kwargs.get("tenant_id") != "tenant-a":
            raise AuthorizationError("cross-tenant denied")

    projection = McpProjection(enabled=True, tenant_hook=tenant_hook)
    projection.authorize(
        principal="alice",
        action="resources/read",
        resource="hedron://page/a",
        tenant_id="tenant-a",
    )
    with pytest.raises(AuthorizationError, match="cross-tenant"):
        projection.authorize(
            principal="alice",
            action="resources/read",
            resource="hedron://page/b",
            tenant_id="tenant-b",
        )


def test_identifier_enumeration_fails_closed_for_unknown_resource() -> None:
    app = Starlette()
    projection = McpProjection(
        enabled=True,
        principal_resolver=lambda _r: "alice",
    )
    projection.register_resource(McpResource(uri="hedron://page/home", name="home"))
    mount_mcp(app, projection)
    client = TestClient(app)
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/read",
            "params": {"uri": "hedron://page/missing"},
        },
        headers={"x-hedron-principal": "alice"},
    )
    assert response.status_code == 404


def test_file_and_http_uri_schemes_rejected() -> None:
    projection = McpProjection(enabled=True)
    with pytest.raises(AuthorizationError, match="excluded"):
        projection.register_resource(McpResource(uri="file:///etc/passwd", name="passwd"))
    with pytest.raises(AuthorizationError, match="excluded"):
        projection.register_resource(McpResource(uri="https://evil.example/x", name="remote"))


def test_origin_allowlist_blocks_exfiltration_origin() -> None:
    app = Starlette()
    projection = McpProjection(
        enabled=True,
        principal_resolver=lambda _r: "alice",
        allowed_origins=frozenset({"https://app.example"}),
    )
    mount_mcp(app, projection)
    client = TestClient(app)
    blocked = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        headers={"x-hedron-principal": "alice", "origin": "https://evil.example"},
    )
    assert blocked.status_code == 403


def test_mutating_tool_without_flag_is_not_ambient_authority() -> None:
    projection = McpProjection(enabled=True, allow_mutations=False)
    projection.register_tool(
        McpTool(
            name="wipe",
            schema={"type": "object", "properties": {}},
            mutate=True,
            handler=lambda: "nope",
        )
    )
    with pytest.raises(AuthorizationError, match="allow_mutations"):
        projection.call_tool("wipe", {}, principal="alice")


def test_default_resolver_rejects_forgeable_principal_headers() -> None:
    """Default identity must not invent principal from client-controlled headers (#168)."""
    from starlette.middleware.sessions import SessionMiddleware

    app = Starlette()
    app.add_middleware(SessionMiddleware, secret_key="test")
    projection = McpProjection(enabled=True)  # no principal_resolver
    projection.register_tool(
        McpTool(
            name="ping",
            schema={"type": "object"},
            mutate=False,
            handler=lambda: "pong",
        )
    )
    mount_mcp(app, projection)
    client = TestClient(app)
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "ping", "arguments": {}},
    }
    anonymous = client.post("/mcp", json=payload)
    forged = client.post(
        "/mcp",
        json=payload,
        headers={"x-hedron-principal": "attacker"},
    )
    forged_x_user = client.post(
        "/mcp",
        json=payload,
        headers={"x-user": "attacker"},
    )
    assert anonymous.status_code == 403
    assert forged.status_code == 403
    assert forged_x_user.status_code == 403


def test_default_resolver_accepts_authenticated_session_subject() -> None:
    from starlette.middleware.sessions import SessionMiddleware
    from starlette.requests import Request
    from starlette.responses import JSONResponse

    app = Starlette()
    app.add_middleware(SessionMiddleware, secret_key="test")

    async def login(request: Request) -> JSONResponse:
        request.session["user"] = "alice"
        return JSONResponse({"ok": True})

    app.add_route("/login", login, methods=["POST"])
    projection = McpProjection(enabled=True)
    projection.register_tool(
        McpTool(
            name="ping",
            schema={"type": "object"},
            mutate=False,
            handler=lambda: "pong",
        )
    )
    mount_mcp(app, projection)
    client = TestClient(app)
    assert client.post("/login").status_code == 200
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "ping", "arguments": {}},
        },
    )
    assert response.status_code == 200
