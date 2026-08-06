"""Phase 0.17 shell primitives and public render_interaction (SHELL-017)."""

from __future__ import annotations

import pytest
from starlette.requests import Request
from starlette.responses import Response

from hedron.responses import render_interaction
from hedron.security.policy import SecurityPolicy
from hedron_core import AppShell, AttrHost, HtmxLink, MainPanel, NavLink, OobHost, render
from hedron_core.interaction import (
    FragmentRegion,
    InteractionPolicy,
    InteractionResult,
    OobUpdate,
)


def test_nav_link_renders_htmx_attrs() -> None:
    html = render(
        HtmxLink(
            "Profile",
            "/profile",
            target="#main-panel",
            swap="outerHTML",
            select="#main-panel",
            select_oob="#side-nav",
            push_url=True,
            active=True,
            class_="nav-link",
        )
    ).html
    assert 'href="/profile"' in html
    assert 'hx-get="/profile"' in html
    assert 'hx-target="#main-panel"' in html
    assert 'hx-select-oob="#side-nav"' in html
    assert 'hx-push-url="true"' in html
    assert "hedron-nav-link" in html
    assert NavLink is HtmxLink


def test_nav_link_rejects_unsafe_target() -> None:
    with pytest.raises(ValueError, match="Unsafe"):
        HtmxLink("X", "/x", target="<script>")


def test_oob_host_and_attr_host_require_id() -> None:
    with pytest.raises(ValueError, match="id"):
        OobHost("x", id="")  # type: ignore[arg-type]
    html = render(OobHost("hello", id="side-nav")).html
    assert 'id="side-nav"' in html
    assert "hedron-oob-host" in html
    html2 = render(AttrHost("y", id="attr-root")).html
    assert "hedron-attr-host" in html2


def test_app_shell_and_main_panel() -> None:
    shell = AppShell(nav=HtmxLink("Home", "/"), body="Body")
    html = render(shell).html
    assert "hedron-app-shell" in html
    assert 'id="main-panel"' in html
    frag = render(shell.as_fragment()).html
    assert "hedron-main-panel" in frag
    assert "hedron-app-shell-nav" not in frag


def test_link_accepts_class_() -> None:
    from hedron_core import Link

    html = render(Link("Go", "/go", class_="extra")).html
    assert "extra" in html


def _request(*, path: str = "/", headers: dict[str, str] | None = None) -> Request:
    from types import SimpleNamespace

    hdrs = [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()]
    app = SimpleNamespace(state=SimpleNamespace(hedron_production=False, hedron_security=None))
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": hdrs,
        "client": ("127.0.0.1", 123),
        "server": ("test", 80),
        "app": app,
    }

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    return Request(scope, receive)


@pytest.mark.anyio
async def test_render_interaction_public_api() -> None:
    request = _request(headers={"HX-Request": "true", "HX-Target": "main-panel"})
    request.app.state.hedron_security = SecurityPolicy.from_name("standard")  # type: ignore[attr-defined]
    result = InteractionResult(
        content=MainPanel("ok"),
        policy=InteractionPolicy(
            declared_regions=(FragmentRegion(id="main-panel", selector="#main-panel"),),
            allow_undeclared_targets=False,
        ),
        region_id="main-panel",
    )
    response = await render_interaction(
        request,
        result,
        policy=SecurityPolicy(csrf_enabled=False),
        authenticated=True,
    )
    assert isinstance(response, Response)
    assert response.status_code == 200
    assert b"main-panel" in response.body or b"hedron-main-panel" in response.body


@pytest.mark.anyio
async def test_render_interaction_rejects_undeclared_target() -> None:
    from fastapi import HTTPException

    request = _request(headers={"HX-Request": "true", "HX-Target": "evil"})
    result = InteractionResult(
        content="x",
        policy=InteractionPolicy(
            declared_regions=(FragmentRegion(id="main-panel", selector="#main-panel"),),
            allow_undeclared_targets=False,
        ),
    )
    with pytest.raises(HTTPException) as exc:
        await render_interaction(request, result, policy=SecurityPolicy(csrf_enabled=False))
    assert exc.value.status_code == 403
