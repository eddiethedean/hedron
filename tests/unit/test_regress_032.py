"""REGRESS-032 deny-by-default and experimental mutation gating."""

from __future__ import annotations

import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient

from hedron_mcp import AuthorizationError, McpProjection, McpTool, mount_mcp


def test_disabled_mount_is_noop_and_install_grants_nothing() -> None:
    app = Starlette()
    projection = McpProjection(enabled=False)
    projection.register_tool(
        McpTool(
            name="status",
            schema={"type": "object", "properties": {}},
            mutate=False,
            handler=lambda: {"ok": True},
        )
    )
    mount_mcp(app, projection)
    assert projection.list_tools() == []
    client = TestClient(app)
    response = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert response.status_code == 404


def test_enabled_zero_registration_empty_surface() -> None:
    app = Starlette()
    projection = McpProjection(
        enabled=True,
        principal_resolver=lambda _r: "alice",
    )
    mount_mcp(app, projection)
    client = TestClient(app)
    listed = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        headers={"x-hedron-principal": "alice"},
    )
    assert listed.status_code == 200
    assert listed.json()["result"]["tools"] == []


def test_mutating_tool_requires_experimental_flag() -> None:
    projection = McpProjection(enabled=True, allow_mutations=False)
    projection.register_tool(
        McpTool(
            name="save",
            schema={"type": "object", "properties": {}},
            mutate=True,
            handler=lambda: None,
        )
    )
    with pytest.raises(AuthorizationError, match="allow_mutations"):
        projection.call_tool("save", {}, principal="alice")
    projection.allow_mutations = True
    assert projection.call_tool("save", {}, principal="alice") is None
