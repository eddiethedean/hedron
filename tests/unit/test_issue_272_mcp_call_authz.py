"""#272: MCP call_tool and read_resource require check_authz."""

from __future__ import annotations

import pytest

from hedron_mcp import AuthorizationError, McpProjection, McpResource, McpTool


def _allow(**_kwargs: object) -> None:
    return None


def test_call_tool_rejects_missing_principal() -> None:
    projection = McpProjection(enabled=True, authz_hook=_allow)
    projection.register_tool(
        McpTool(name="t", schema={"type": "object"}, mutate=False, handler=lambda: {"ok": True})
    )
    with pytest.raises(AuthorizationError):
        projection.call_tool("t", {}, principal=None)
    assert projection.call_tool("t", {}, principal="alice") == {"ok": True}


def test_read_resource_rejects_missing_principal() -> None:
    projection = McpProjection(enabled=True, authz_hook=_allow)
    projection.register_resource(
        McpResource(uri="hedron://page/home", name="home", description="Home")
    )
    with pytest.raises(AuthorizationError):
        projection.read_resource("hedron://page/home", principal=None)
    payload = projection.read_resource("hedron://page/home", principal="alice")
    assert payload["mimeType"]
