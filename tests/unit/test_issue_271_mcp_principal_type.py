"""#271: MCP resolve_principal must ignore non-string session values."""

from __future__ import annotations

from types import SimpleNamespace

from hedron_mcp import McpProjection


def test_non_string_session_values_are_not_principals() -> None:
    projection = McpProjection(enabled=True)
    request = SimpleNamespace(scope={"session": {}}, session={"user": True})
    assert projection.resolve_principal(request) is None

    numbered = SimpleNamespace(scope={"session": {}}, session={"user": 1})
    assert projection.resolve_principal(numbered) is None

    named = SimpleNamespace(scope={"session": {}}, session={"user": "alice"})
    assert projection.resolve_principal(named) == "alice"
