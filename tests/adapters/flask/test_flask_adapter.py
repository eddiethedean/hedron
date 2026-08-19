"""Adapter tests for hedron-flask."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest
from flask.testing import FlaskClient

from hedron_core import Heading, Page, Text
from hedron_core.interaction import InteractionResult
from hedron_core.rendering import RenderMode
from hedron_flask import HedronFlask, component_response, interaction_response
from hedron_flask.htmx import render_mode_for_request

ROOT = Path(__file__).resolve().parents[3]
FLASK_SRC = ROOT / "packages" / "hedron-flask" / "src" / "hedron_flask"
FORBIDDEN = frozenset({"fastapi", "starlette", "hedron"})


@pytest.fixture
def client() -> FlaskClient:
    app = HedronFlask(__name__).flask

    @app.get("/page")
    def page():
        return component_response(
            Page(Heading("Hello", level=1), title="Test"),
            mode=RenderMode.PAGE,
        )

    @app.get("/fragment")
    def fragment():
        return component_response(Text("Fragment body"), mode=RenderMode.FRAGMENT)

    @app.get("/interaction")
    def interaction():
        return interaction_response(
            InteractionResult(
                content=Text("Updated"),
                trigger="refreshed",
                explanation="test",
            )
        )

    return app.test_client()


def test_page_render(client: FlaskClient) -> None:
    response = client.get("/page")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "<h1" in body
    assert "<html" in body
    assert "htmx.min.js" in body
    assert "/hedron-static/ext/head-support.js" in body
    assert body.index("htmx.min.js") < body.index("/hedron-static/ext/head-support.js")


def test_hedron_static_mount(client: FlaskClient) -> None:
    response = client.get("/hedron-static/htmx.min.js")
    assert response.status_code == 200
    payload = response.get_data(as_text=True)
    assert "htmx" in payload.lower() or len(payload) > 1000


def test_page_static_href_honors_script_root() -> None:
    app = HedronFlask(__name__).flask

    @app.get("/page")
    def page():
        return component_response(
            Page(Heading("Hello", level=1), title="Test"),
            mode=RenderMode.PAGE,
        )

    client = app.test_client()
    response = client.get("/page", environ_overrides={"SCRIPT_NAME": "/app"})
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "/app/hedron-static/htmx.min.js" in body
    assert 'src="/hedron-static/htmx.min.js"' not in body


def test_fragment_render(client: FlaskClient) -> None:
    response = client.get("/fragment", headers={"HX-Request": "true"})
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Fragment body" in body
    assert "<html" not in body


def test_interaction_headers(client: FlaskClient) -> None:
    response = client.get("/interaction")
    assert response.status_code == 200
    assert response.headers.get("HX-Trigger") == "refreshed"
    assert "Updated" in response.get_data(as_text=True)


def test_component_vary_header(client: FlaskClient) -> None:
    response = client.get("/fragment", headers={"HX-Request": "true"})
    vary = response.headers.get("Vary", "")
    assert "HX-Request" in vary


def test_auth_signal_uses_flask_session(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "flask_login", None)
    hedron = HedronFlask(__name__)
    hedron.flask.secret_key = "test"
    with hedron.flask.test_request_context("/"):
        from flask import session

        session["user_id"] = "u1"
        session["scopes"] = ["read"]
        session["tenant_id"] = "t1"
        signal = hedron.auth_signal()
    assert signal.authenticated is True
    assert signal.subject_id == "u1"
    assert signal.scopes == ("read",)
    assert signal.tenant_id == "t1"


def test_oob_authorization() -> None:
    from hedron_core.interaction import FragmentRegion, InteractionPolicy, OobUpdate

    hedron = HedronFlask(__name__)
    ok = InteractionResult(
        content=Text("main"),
        oob=(OobUpdate(content=Text("side"), element_id="side"),),
        policy=InteractionPolicy(declared_regions=(FragmentRegion(id="side", selector="#side"),)),
    )
    with hedron.flask.test_request_context("/"):
        response = interaction_response(ok)
    assert response.status_code == 200
    assert "hx-swap-oob" in response.get_data(as_text=True)

    bad = InteractionResult(
        content=Text("main"),
        oob=(OobUpdate(content=Text("evil"), element_id="evil"),),
        policy=InteractionPolicy(declared_regions=(FragmentRegion(id="side", selector="#side"),)),
    )
    with hedron.flask.test_request_context("/"):
        denied = interaction_response(bad)
    assert denied.status_code == 403


def test_csrf_cookie_on_get() -> None:
    hedron = HedronFlask(__name__)
    hedron.flask.secret_key = "test"

    @hedron.flask.get("/safe")
    def safe():
        return "ok"

    client = hedron.flask.test_client()
    response = client.get("/safe")
    assert response.status_code == 200
    set_cookie = response.headers.getlist("Set-Cookie")
    assert any("hedron_csrf=" in c for c in set_cookie)


def test_render_mode_for_request() -> None:
    assert render_mode_for_request({}) is RenderMode.PAGE
    assert render_mode_for_request({"HX-Request": "true"}) is RenderMode.FRAGMENT
    assert (
        render_mode_for_request({"HX-Request": "true", "HX-History-Restore-Request": "true"})
        is RenderMode.PAGE
    )


def test_no_fastapi_imports_in_source() -> None:
    found: list[str] = []
    for path in FLASK_SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if root in FORBIDDEN:
                        found.append(f"{path.name}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".", 1)[0]
                if root in FORBIDDEN:
                    found.append(f"{path.name}: from {node.module}")
    assert found == []
