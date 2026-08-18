"""#288: unauthenticated MCP cancels must not share principal:anonymous."""

from __future__ import annotations

from starlette.applications import Starlette
from starlette.testclient import TestClient

from hedron_mcp import McpProjection, McpTool, mount_mcp
from hedron_mcp.transport import _cancel_owner


def test_cancel_owner_requires_session_or_principal() -> None:
    assert _cancel_owner(session_id=None, principal=None) is None
    assert _cancel_owner(session_id="abc", principal=None) == "session:abc"
    assert _cancel_owner(session_id=None, principal="alice") == "principal:alice"


def test_unauthenticated_cancel_is_rejected() -> None:
    app = Starlette()
    projection = McpProjection(enabled=True)
    projection.register_tool(
        McpTool(name="ping", schema={"type": "object"}, mutate=False, handler=lambda: "pong")
    )
    mount_mcp(app, projection)
    client = TestClient(app)
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "method": "notifications/cancelled",
            "params": {"requestId": 99},
        },
    )
    assert response.status_code == 403
    assert projection.bounds.is_cancelled("99", owner="principal:anonymous") is False
