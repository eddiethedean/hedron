"""Phase 0.15 M2 interaction ergonomics (RFC-0039)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from hedron import (
    Hedron,
    InteractionResult,
    OobUpdate,
    Page,
    RefreshButton,
    Text,
    html,
    redirect_htmx,
    retarget,
    swap,
    swap_oob,
)
from hedron.interaction import FragmentRegion
from hedron_core.codes import HED_HTMX_0001
from hedron_core.rendering import render


def test_region_defaults_selector() -> None:
    app = Hedron(title="t", security="standard", session_secret="test", explorer="off")
    region = app.region("service-status", description="Live panel")
    assert isinstance(region, FragmentRegion)
    assert region.id == "service-status"
    assert region.selector == "#service-status"
    assert region.description == "Live panel"
    custom = app.region("panel", selector="#custom-panel")
    assert custom.selector == "#custom-panel"


def test_swap_builders_return_interaction_result() -> None:
    body = Text("primary")
    toast_oob = OobUpdate(content=Text("toast"), element_id="hedron-toast")
    basic = swap(body)
    assert isinstance(basic, InteractionResult)
    assert basic.content is body
    assert basic.oob == ()

    with_toast = swap(body, toast="Saved")
    assert len(with_toast.oob) == 1
    assert with_toast.oob[0].element_id == "hedron-toast"

    oob = swap_oob(body, toast_oob)
    assert oob.content is body
    assert oob.oob == (toast_oob,)

    region = FragmentRegion(id="main", selector="#main")
    moved = retarget(body, region)
    assert moved.retarget == "#main"
    assert moved.region_id == "main"
    moved_sel = retarget(body, "#other")
    assert moved_sel.retarget == "#other"

    redirected = redirect_htmx("/next")
    assert redirected.redirect == "/next"
    assert redirected.content is None


def test_fragment_decorator_registers_regions() -> None:
    app = Hedron(title="t", security="standard", session_secret="test", explorer="off")
    status = app.region("service-status")

    @app.fragment("/status", region=status)
    def refresh() -> InteractionResult:
        return swap(html.div(Text("ok"), id=status.id))

    regions = getattr(refresh, "_hedron_fragment_regions", ())
    assert len(regions) == 1
    assert regions[0].id == "service-status"
    assert regions[0].selector == "#service-status"

    client = TestClient(app)
    ok = client.get(
        "/status",
        headers={"HX-Request": "true", "HX-Target": "#service-status"},
    )
    assert ok.status_code == 200
    assert "ok" in ok.text


def test_undeclared_target_still_403() -> None:
    app = Hedron(title="t", security="standard", session_secret="test", explorer="off")
    status = app.region("service-status")

    @app.fragment("/status", region=status)
    def refresh() -> InteractionResult:
        return swap(Text("ok"))

    client = TestClient(app)
    bad = client.get(
        "/status",
        headers={"HX-Request": "true", "HX-Target": "#evil"},
    )
    assert bad.status_code == 403
    assert HED_HTMX_0001 in bad.text
    assert "#evil" in bad.text
    assert "service-status" in bad.text


def test_production_undeclared_target_opaque() -> None:
    app = Hedron(
        title="t",
        security="standard",
        session_secret="test",
        explorer="off",
    )
    app.state.hedron_production = True
    status = app.region("service-status")

    @app.fragment("/status", region=status)
    def refresh() -> InteractionResult:
        return swap(Text("ok"))

    client = TestClient(app)
    bad = client.get(
        "/status",
        headers={"HX-Request": "true", "HX-Target": "#evil"},
    )
    assert bad.status_code == 403
    assert "HX-Target is not an authorized fragment region" in bad.text
    assert HED_HTMX_0001 not in bad.text
    assert "service-status" not in bad.text


def test_refresh_button_for_region() -> None:
    from hedron_core.rendering import RenderMode

    region = FragmentRegion(id="panel", selector="#panel")
    button = RefreshButton.for_region(region, href="/panel", label="Reload")
    assert button.target == "#panel"
    assert button.swap == "outerHTML"
    assert button.href == "/panel"
    markup = render(button, mode=RenderMode.FRAGMENT).html
    assert 'hx-target="#panel"' in markup
    assert 'hx-get="/panel"' in markup
    assert "hx-swap" in markup


def test_explorer_click_preview() -> None:
    app = Hedron(
        title="ex",
        security="standard",
        explorer="development",
        session_secret="secret",
    )
    status = app.region("service-status")

    @app.page("/")
    def home() -> Page:
        return Page(Text("hi"), title="T")

    @app.fragment("/status", region=status)
    def refresh_status() -> InteractionResult:
        return swap(Text("ok"))

    with TestClient(app) as client:
        home_resp = client.get("/")
        token = home_resp.cookies.get("hedron_csrf")
        assert token
        simulated = client.post(
            "/hedron-explorer/api/simulate",
            json={
                "route": "refresh_status",
                "allow_mutations": False,
                "target": "#service-status",
            },
            headers={"X-CSRF-Token": token},
        )
        assert simulated.status_code == 200
        payload = simulated.json()
        preview = payload["click_preview"]
        assert preview["method"] == "GET"
        assert preview["path"] == "/status"
        assert preview["target"] == "#service-status"
        assert preview["swap"]
        assert preview["csrf_required"] is False
        assert preview["declared_regions"][0]["id"] == "service-status"

        direct = client.get(
            "/hedron-explorer/api/click-preview",
            params={"route": "refresh_status", "target": "#service-status"},
        )
        assert direct.status_code == 200
        assert direct.json()["click_preview"]["path"] == "/status"


def test_check_detects_target_region_mismatch(tmp_path) -> None:
    from hedron.cli import _check_htmx_region_mismatches
    from hedron_core.registry import get_registry

    app = Hedron(title="t", security="standard", session_secret="test", explorer="off")
    status = app.region("service-status")

    @app.fragment("/status", region=status)
    def refresh_status() -> InteractionResult:
        return swap(Text("ok"))

    # Ensure registry has the route with regions (decorator already registered).
    routes = {r.name: r for r in get_registry().routes()}
    assert "refresh_status" in routes

    bad_file = tmp_path / "bad_ui.py"
    bad_file.write_text(
        'RefreshButton("x", href="/status", target="#wrong")\n',
        encoding="utf-8",
    )
    diags = _check_htmx_region_mismatches(tmp_path)
    assert any(d.code == HED_HTMX_0001 for d in diags)
    assert any("#wrong" in d.explanation for d in diags)
