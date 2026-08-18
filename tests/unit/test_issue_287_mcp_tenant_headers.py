"""#287: MCP HTTP must ignore client tenant and scope headers."""

from __future__ import annotations

from typing import Any

from starlette.applications import Starlette
from starlette.testclient import TestClient

from hedron_mcp import McpProjection, McpTool, mount_mcp


def test_client_tenant_and_scope_headers_are_ignored() -> None:
    seen: dict[str, Any] = {}

    def authz_hook(
        *,
        principal: str | None,
        action: str,
        resource: str | None = None,
        scopes: object = None,
        tenant_id: str | None = None,
    ) -> None:
        del principal, action, resource
        seen["tenant_id"] = tenant_id
        seen["scopes"] = scopes

    app = Starlette()
    projection = McpProjection(
        enabled=True,
        principal_resolver=lambda _r: "alice",
        authz_hook=authz_hook,
    )
    projection.register_tool(
        McpTool(name="ping", schema={"type": "object"}, mutate=False, handler=lambda: "pong")
    )
    mount_mcp(app, projection)
    client = TestClient(app)
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "ping", "arguments": {}, "tenant_id": "evil"},
        },
        headers={
            "x-hedron-tenant": "evil",
            "x-hedron-scopes": '{"principal": "admin"}',
        },
    )
    assert response.status_code == 200
    assert seen["tenant_id"] is None
    assert seen["scopes"] is None
