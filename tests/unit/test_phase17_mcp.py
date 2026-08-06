"""Phase 0.17 deny-by-default MCP projection (MCP-017)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from hedron_mcp import (
    AuthorizationError,
    McpProjection,
    McpResource,
    McpTool,
    __version__,
    mount_mcp,
)


def test_package_version() -> None:
    assert __version__ == "0.1.0"


def test_deny_by_default_empty_when_disabled() -> None:
    projection = McpProjection()
    assert projection.enabled is False
    assert projection.tools == ()
    assert projection.resources == ()
    assert projection.list_tools() == []
    assert projection.list_resources() == []


def test_empty_tools_when_disabled_even_after_register() -> None:
    projection = McpProjection()

    def _handler() -> str:
        return "ok"

    projection.register_tool(
        McpTool(
            name="read_status",
            schema={"type": "object", "properties": {}},
            mutate=False,
            handler=_handler,
            description="Read status",
        )
    )
    projection.register_resource(
        McpResource(uri="hedron://page/home", name="home", description="Home page")
    )
    assert projection.enabled is False
    assert projection.list_tools() == []
    assert projection.list_resources() == []
    assert projection.tools == ()
    assert projection.resources == ()


def test_register_tool_with_mutate_flag_visible_when_enabled() -> None:
    projection = McpProjection(enabled=True)

    def _mutate() -> None:
        return None

    def _read() -> dict[str, str]:
        return {"ok": "yes"}

    projection.register_tool(
        McpTool(
            name="save_item",
            schema={"type": "object", "properties": {"id": {"type": "string"}}},
            mutate=True,
            handler=_mutate,
        )
    )
    projection.register_tool(
        McpTool(
            name="get_item",
            schema={"type": "object", "properties": {"id": {"type": "string"}}},
            mutate=False,
            handler=_read,
        )
    )
    tools = {tool.name: tool for tool in projection.list_tools()}
    assert tools["save_item"].mutate is True
    assert tools["get_item"].mutate is False
    assert len(projection.tools) == 2


def test_authz_requires_principal_and_never_exceeds() -> None:
    projection = McpProjection(enabled=True)
    with pytest.raises(AuthorizationError, match="principal"):
        projection.check_authz(principal=None, action="tools/call")
    projection.check_authz(principal="alice", action="tools/call")
    with pytest.raises(AuthorizationError, match="never exceeds"):
        projection.check_authz(
            principal="alice",
            action="tools/call",
            scopes={"principal": "bob"},
        )


def test_mount_mcp_noops_when_disabled() -> None:
    app = SimpleNamespace(state=SimpleNamespace())
    projection = McpProjection(enabled=False)
    mount_mcp(app, projection)
    assert not hasattr(app.state, "hedron_mcp")

    projection.enabled = True
    mount_mcp(app, projection)
    assert app.state.hedron_mcp is projection
