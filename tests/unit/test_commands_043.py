"""COMMAND-043: @app.command, ActionHandle, Form, fallback."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from tests.unit._helpers_043 import csrf_headers, make_app, reset_043

from hedron import ActionHandle, Form, Page, Text, patches, refresh
from hedron_core.codes import HED_CMD_0001, HED_CMD_0002
from hedron_core.diagnostics import HedronError
from hedron_core.rendering import render


def setup_function() -> None:
    reset_043()


def test_command_returns_handle_not_function_and_action_unchanged() -> None:
    app = make_app(security="standard")

    @app.refreshable
    def status():
        return Text("idle")

    @app.command(fallback="/")
    def ping():
        return refresh(status).toast("pong")

    @app.action("/legacy-action")
    def legacy_action():
        return Text("legacy")

    @app.page("/")
    def home():
        return Page(status(), ping.button("Ping"), title="Home")

    assert isinstance(ping, ActionHandle)
    assert ping.path == "/_hedron/commands/ping"
    assert ping.method == "POST"
    form_fn = getattr(ping, "form", None)
    if callable(form_fn):
        with pytest.raises(HedronError):
            form_fn()
    assert callable(legacy_action) and not isinstance(legacy_action, ActionHandle)
    client = TestClient(app, follow_redirects=False)
    headers = csrf_headers(client)
    response = client.post(ping.path, headers=headers)
    assert response.status_code == 200
    assert "HX-Trigger" in response.headers
    assert "hedron:refresh-h-view-status" in response.headers["HX-Trigger"]
    assert response.headers.get("HX-Refresh") in {None, ""}
    pe = client.post(ping.path, headers={"X-CSRF-Token": headers["X-CSRF-Token"]})
    assert pe.status_code in {303, 307}
    assert pe.headers.get("location") == "/"


def test_command_button_embeds_csrf_headers_on_page() -> None:
    app = make_app(security="standard")

    @app.refreshable
    def status():
        return Text("idle")

    @app.command(fallback="/")
    def ping():
        return refresh(status).toast("pong")

    @app.page("/")
    def home():
        return Page(status(), ping.button("Ping"), title="Home")

    client = TestClient(app)
    page = client.get("/")
    token = page.cookies.get("hedron_csrf")
    assert token
    assert "hx-headers" in page.text
    assert token in page.text
    response = client.post(
        ping.path,
        headers={"HX-Request": "true", "X-CSRF-Token": token},
    )
    assert response.status_code == 200


def test_command_rejects_safe_method() -> None:
    app = make_app()

    with pytest.raises(HedronError) as err:

        @app.command(method="GET")
        def nope():
            return Text("x")

    assert err.value.diagnostic.code == HED_CMD_0001


def test_command_without_fallback_fails_plain_http() -> None:
    app = make_app(security="standard")

    @app.refreshable
    def status():
        return Text("x")

    @app.command
    def poke():
        return refresh(status)

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    client = TestClient(app)
    token = csrf_headers(client, htmx=False)["X-CSRF-Token"]
    response = client.post(poke.path, headers={"X-CSRF-Token": token})
    assert response.status_code == 400
    assert HED_CMD_0002 in response.text


def test_form_action_handle_and_explicit_fields() -> None:
    app = make_app()

    @app.command(fallback="/")
    def save():
        return Text("saved")

    markup = render(Form(action=save, children=(Text("name"),))).html
    assert 'action="/_hedron/commands/save"' in markup or "commands/save" in markup
    assert 'data-hedron-command="save"' in markup
    assert 'hx-post="' in markup
    button = render(save.button("Save")).html
    assert "hx-post" in button
    assert "hx-swap" in button


def test_refresh_button_and_replace_update() -> None:
    app = make_app(security="standard")

    @app.refreshable
    def status():
        return Text("alpha")

    @app.command(fallback="/")
    def rewrite():
        return patches(status.replace(Text("beta")))

    @app.page("/")
    def home():
        return Page(
            status(), status.refresh_button("Refresh"), rewrite.button("Rewrite"), title="Home"
        )

    client = TestClient(app)
    page = client.get("/")
    assert 'hx-get="/_hedron/views/status"' in page.text
    headers = csrf_headers(client)
    patched = client.post(rewrite.path, headers=headers)
    assert patched.status_code == 200
    assert "beta" in patched.text
    assert patched.headers.get("HX-Retarget") == "#h-view-status"


def test_command_generic_arity() -> None:
    assert len(ActionHandle.__parameters__) == 2


@pytest.mark.parametrize(
    "bad", ["mailto:attacker@evil.com", "/ok%0aSet-Cookie:x=1", "//evil.example"]
)
def test_command_fallback_rejects_non_local_paths(bad: str) -> None:
    """#593: fallback must use is_local_path (same as redirect_local), not SafeUrl alone."""
    app = make_app(security="development")

    @app.refreshable
    def status():
        return Text("idle")

    with pytest.raises(HedronError, match="HED-SEC-0001"):

        @app.command(fallback=bad)
        def ping():
            return refresh(status)


def test_command_fallback_redirect_uses_local_path() -> None:
    app = make_app(security="development")

    @app.refreshable
    def status():
        return Text("idle")

    @app.command("/cmd", fallback="/home")
    def ping():
        return refresh(status)

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    client = TestClient(app, follow_redirects=False)
    client.get("/")
    headers = csrf_headers(client)
    # Non-HTMX progressive enhancement redirect
    response = client.post(
        "/cmd", headers={k: v for k, v in headers.items() if k.lower() != "hx-request"}
    )
    assert response.status_code == 303
    assert response.headers.get("location") == "/home"
