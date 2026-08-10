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
)


def test_nav_link_renders_htmx_attrs() -> None:
    """Attr emit only — ``select_oob`` is valid markup by itself.

    Pairing the same id with a server ``OobUpdate`` is the #57 conflict; see
    ``test_issue57_select_oob_conflict`` / ``hedron check`` (HED-HTMX-0002).
    """
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


def test_nav_link_select_oob_without_oobupdate_is_attr_only() -> None:
    """Emitting select_oob alone must not be treated as an OobUpdate conflict."""
    from hedron_core.interaction import conflicting_select_oob_targets

    html = render(
        HtmxLink("Profile", "/profile", target="#main-panel", select_oob="#side-nav")
    ).html
    assert 'hx-select-oob="#side-nav"' in html
    assert conflicting_select_oob_targets("#side-nav", oob=()) == frozenset()


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


def test_attr_host_accepts_a11y_attrs() -> None:
    html = render(
        AttrHost(
            "busy",
            id="attr-root",
            aria={"busy": "true", "label": "Status host"},
            title="Status",
            tabindex=-1,
            data={"tone": "info"},
        )
    ).html
    assert 'aria-busy="true"' in html
    assert 'aria-label="Status host"' in html
    assert 'title="Status"' in html
    assert 'tabindex="-1"' in html
    assert 'data-tone="info"' in html


def test_main_panel_accepts_landmark_a11y_attrs() -> None:
    html = render(
        MainPanel(
            "Profile",
            tabindex=-1,
            aria={"label": "Main content"},
            lang="en",
            data={"panel": "profile"},
        )
    ).html
    assert "<main" in html
    assert 'tabindex="-1"' in html
    assert 'aria-label="Main content"' in html
    assert 'lang="en"' in html
    assert 'data-panel="profile"' in html
    assert "data-hedron-main-panel=" in html


def test_main_panel_rejects_hostile_roles_and_unknown_attrs() -> None:
    with pytest.raises(TypeError, match=r"role='presentation' is not allowed on landmark"):
        MainPanel("x", role="presentation")
    with pytest.raises(TypeError, match="Unsupported landmark"):
        MainPanel("x", onclick="alert(1)")  # type: ignore[call-arg]


def test_oob_host_accepts_live_region_attrs() -> None:
    html = render(
        OobHost(
            "Saved",
            id="toast-host",
            aria={"live": "polite", "atomic": "true"},
            title="Status",
            tabindex=-1,
            data={"tone": "success"},
        )
    ).html
    assert 'id="toast-host"' in html
    assert 'aria-live="polite"' in html
    assert 'aria-atomic="true"' in html
    assert 'title="Status"' in html
    assert 'tabindex="-1"' in html
    assert 'data-tone="success"' in html
    assert "data-hedron-oob-host=" in html


def test_oob_host_rejects_role_and_unknown_attrs() -> None:
    with pytest.raises(TypeError, match=r"role='status' is not allowed on OobHost"):
        OobHost("x", id="toast", role="status")
    with pytest.raises(TypeError, match="Unsupported OobHost"):
        OobHost("x", id="toast", onclick="alert(1)")  # type: ignore[call-arg]


def test_app_shell_and_main_panel() -> None:
    shell = AppShell(nav=HtmxLink("Home", "/"), body="Body")
    html = render(shell).html
    assert "hedron-app-shell" in html
    assert 'id="main-panel"' in html
    assert 'aria-label="Primary"' in html
    frag = render(shell.as_fragment()).html
    assert "hedron-main-panel" in frag
    assert "hedron-app-shell-nav" not in frag


def test_app_shell_does_not_nest_nav_landmark() -> None:
    from hedron_core import Nav, NavLink

    html = render(AppShell(nav=Nav(NavLink("Home", "/")), body="Body")).html
    assert html.count("<nav") == 1
    assert "hedron-app-shell-nav" in html


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
    request = _request(headers={"HX-Request": "true", "HX-Target": "#main-panel"})
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
