"""HTMX authoring primitives for 0.50 (#496–#500, #502, #503)."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from fastapi.testclient import TestClient
from pydantic import BaseModel
from tests.unit._helpers_050 import csrf_headers, make_app, reset_050

from hedron import Control, ErrorState, FormBody, Lazy, Page, Text, Toast
from hedron.htmx import render_mode_for_request
from hedron.routing.reverse import ComponentRef
from hedron.testing import render_html
from hedron_core.builtins import Select, ToastHost
from hedron_core.builtins._base import dom_id_part
from hedron_core.htmx.attrs import Hx
from hedron_core.interaction import InteractionPolicy, InteractionResult
from hedron_core.rendering import RenderMode
from hedron_core.security_policy import SecurityPolicy


def setup_function() -> None:
    reset_050()


def test_hx_trigger_include_validate_and_rejects_js_vals() -> None:
    attrs = Hx(
        trigger="change",
        include="#field-country",
        validate="native",
        vals='{"ok":1}',
        headers='{"X-Demo":"1"}',
    ).as_html_attrs()
    assert attrs["hx-trigger"] == "change"
    assert attrs["hx-include"] == "#field-country"
    assert attrs["hx-validate"] == "true"
    assert attrs["data-hedron-validity"] == "native"
    try:
        Hx(vals="js:window.x").as_html_attrs()
    except ValueError:
        pass
    else:
        raise AssertionError("js: vals must be rejected")
    try:
        Hx(headers="js:alert(1)").as_html_attrs()
    except ValueError:
        pass
    else:
        raise AssertionError("js: headers must be rejected")


def test_select_depends_on_compiles_htmx_get() -> None:
    html = render_html(
        Select(
            "city",
            [("x", "X")],
            depends_on="country",
            source="/cities",
        )
    )
    assert "hx-get" in html
    assert f"change from:#field-{dom_id_part('country')}" in html
    assert f"#field-{dom_id_part('country')}" in html
    spaced = render_html(Select("city", [("x", "X")], depends_on="parent field", source="/cities"))
    assert f"#field-{dom_id_part('parent field')}" in spaced


def test_toast_ttl_and_host() -> None:
    info = render_html(Toast("Saved", ttl_ms=2500))
    assert "data-hedron-ttl" in info
    assert "2500" in info
    danger = render_html(Toast("Boom", tone="danger"))
    assert "data-hedron-ttl" not in danger
    assert "data-hedron-toast-dismiss" in danger
    host = render_html(ToastHost())
    assert 'id="hedron-toast"' in host


def test_lazy_error_slot_without_hx_on() -> None:
    html = render_html(
        Lazy(
            ref=ComponentRef(logical_id="x", path="/frag"),
            error=ErrorState("failed"),
        )
    )
    assert "data-hedron-error-slot" in html
    assert "data-hedron-error-template" in html
    assert "-body" in html
    assert "hx-on" not in html
    assert "</template>" in html
    assert html.index("</template>") < html.rindex("-body")
    ui = (
        __import__("pathlib")
        .Path("packages/hedron-core/src/hedron_core/static/hedron-ui.mjs")
        .read_text(encoding="utf-8")
    )
    assert "htmx:responseError" in ui
    assert "htmx:sendError" in ui


def test_history_restore_policy_and_htmx_config() -> None:
    policy = InteractionPolicy(history_restore="oob")
    assert policy.history_restore == "oob"
    config = SecurityPolicy.from_name("standard").htmx_config_json()
    assert '"historyRestoreAsHxRequest":false' in config
    assert '"reportValidityOfForms":true' in config
    app = make_app(security="standard")

    @app.page("/")
    def home():
        return Page(Text("h"), title="H")

    app.state.hedron_interaction_policy = policy
    with TestClient(app) as client:
        restored = client.get(
            "/",
            headers={"HX-Request": "true", "HX-History-Restore-Request": "true"},
        )
        assert restored.status_code == 200
    from starlette.requests import Request

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [
            (b"hx-request", b"true"),
            (b"hx-history-restore-request", b"true"),
        ],
        "client": ("test", 50000),
        "server": ("test", 80),
    }
    request = Request(scope)
    request.scope["app"] = app
    assert render_mode_for_request(request, policy=policy) is RenderMode.FRAGMENT
    assert (
        render_mode_for_request(request, policy=InteractionPolicy(history_restore="page"))
        is RenderMode.PAGE
    )


def test_action_handle_effect_after_and_dependent_control() -> None:
    app = make_app(security="standard")

    class Body(BaseModel):
        city: Literal["a", "b"] = "a"

    @app.command(fallback="/")
    def save(data: Annotated[Body, FormBody()]):
        return InteractionResult(content=Text("ok"))

    @app.page("/")
    def home():
        return Page(Text("h"), title="H")

    chained = save.effect(InteractionResult(trigger="saved")).after(load="/next", delay_ms=250)
    assert chained is not save
    assert save._effect is None
    button = render_html(chained.button("Go"))
    assert "hx-post" in button
    assert "delay:250ms" in button
    assert "data-hedron-after-load" in button
    assert "hx-swap" in button
    form = render_html(
        chained.form(
            controls={"city": Control(kind="select", depends_on="country", source="/cities")}
        )
    )
    assert "hx-swap" in form
    assert "change from:#field-country" in form
    assert home is not None
    with TestClient(app) as client:
        headers = csrf_headers(client)
        headers["HX-Request"] = "true"
        response = client.post(save.path, data={"city": "a"}, headers=headers)
        assert response.status_code == 200
        assert response.headers.get("HX-Trigger-After-Swap") == "/next"
        trigger = response.headers.get("HX-Trigger") or ""
        assert "saved" in trigger


def test_hedron_ui_mjs_copies_are_byte_identical() -> None:
    core = Path("packages/hedron-core/src/hedron_core/static/hedron-ui.mjs").read_bytes()
    host = Path("packages/hedron/src/hedron/static/hedron-ui.mjs").read_bytes()
    assert core == host
    text = core.decode("utf-8")
    assert "data-hedron-toast-dismiss" in text
    assert "data-hedron-after-load" in text
    assert "data-hedron-error-template" in text
    assert "htmx:responseError" in text
