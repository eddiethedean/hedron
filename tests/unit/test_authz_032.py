"""AUTHZ-032 unit coverage for host authn + hooks."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from hedron_mcp import AuthorizationError, McpProjection


def test_host_authn_resolver_and_hooks() -> None:
    seen: dict[str, object] = {}

    def resolver(request: object) -> str | None:
        return getattr(request, "user", None)

    def authz_hook(**kwargs: object) -> None:
        seen["authz"] = kwargs
        if kwargs.get("resource") == "secret":
            raise AuthorizationError("denied")

    def tenant_hook(**kwargs: object) -> None:
        seen["tenant"] = kwargs
        if kwargs.get("tenant_id") != "t1":
            raise AuthorizationError("tenant")

    projection = McpProjection(
        enabled=True,
        principal_resolver=resolver,
        authz_hook=authz_hook,
        tenant_hook=tenant_hook,
    )
    req = SimpleNamespace(user="alice", headers={}, session={})
    assert projection.resolve_principal(req) == "alice"
    projection.authorize(
        principal="alice",
        action="tools/call",
        resource="ok",
        tenant_id="t1",
    )
    assert seen["authz"]["principal"] == "alice"
    assert seen["tenant"]["tenant_id"] == "t1"
    with pytest.raises(AuthorizationError, match="denied"):
        projection.authorize(
            principal="alice",
            action="tools/call",
            resource="secret",
            tenant_id="t1",
        )
    with pytest.raises(AuthorizationError, match="tenant"):
        projection.authorize(
            principal="alice",
            action="tools/call",
            resource="ok",
            tenant_id="t2",
        )


def test_ui_filter_is_not_authorization() -> None:
    """UI option filtering must not grant MCP authority."""
    projection = McpProjection(enabled=True)
    with pytest.raises(AuthorizationError, match="principal"):
        projection.check_authz(
            principal=None,
            action="tools/call",
            scopes={"ui_options": ["admin"]},
        )
