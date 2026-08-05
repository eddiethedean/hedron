"""Phase 0.8 Flask adapter hardening evidence."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from hedron_core import Text
from hedron_core.adapter import UrlReverseRequest
from hedron_core.interaction import InteractionResult
from hedron_flask import HedronFlask, hedron_route
from hedron_flask.routing import FlaskUrlReverser

ROOT = Path(__file__).resolve().parents[3]


def test_create_app_factory_returns_wsgi_app() -> None:
    import importlib.util

    path = ROOT / "examples" / "flask-reference" / "app.py"
    spec = importlib.util.spec_from_file_location("flask_ref_app", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    wsgi = mod.create_app()
    assert hasattr(wsgi, "wsgi_app")
    client = wsgi.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "Flask Reference" in response.get_data(as_text=True)


def test_auth_signal_without_session_is_anonymous() -> None:
    hedron = HedronFlask(__name__)
    hedron.flask.secret_key = "test"
    with hedron.flask.test_request_context("/"):
        signal = hedron.auth_signal()
    assert signal.authenticated is False
    assert signal.subject_id is None


def test_csrf_token_round_trip() -> None:
    hedron = HedronFlask(__name__)
    hedron.flask.secret_key = "test"
    client = hedron.flask.test_client()

    @hedron.flask.get("/token")
    def token_view():
        from flask import request

        return hedron.csrf_token(request)

    response = client.get("/token")
    assert response.status_code == 200
    token = response.get_data(as_text=True)
    assert len(token) >= 16
    assert any("hedron_csrf=" in c for c in response.headers.getlist("Set-Cookie"))


def test_hedron_route_csrf_enforced_on_post() -> None:
    hedron = HedronFlask(__name__)
    hedron.flask.secret_key = "test"
    app = hedron.flask

    @hedron.flask.get("/seed")
    def seed():
        return "ok"

    @hedron_route(app, "/post-route", endpoint="post_route", methods=["POST"])
    def post_route():
        return Text("posted")

    client = app.test_client()
    denied = client.post("/post-route", data={"x": "1"})
    assert denied.status_code == 403

    seeded_resp = client.get("/seed")
    assert seeded_resp.status_code == 200
    cookie = None
    for item in seeded_resp.headers.getlist("Set-Cookie"):
        if item.startswith("hedron_csrf="):
            cookie = item.split(";", 1)[0].split("=", 1)[1]
            break
    assert cookie
    ok = client.post(
        "/post-route",
        data={"x": "1"},
        headers={"X-CSRF-Token": cookie},
    )
    assert ok.status_code == 200
    assert "posted" in ok.get_data(as_text=True)


def test_hedron_route_sync_component() -> None:
    hedron = HedronFlask(__name__)
    app = hedron.flask

    @hedron_route(app, "/via-route", endpoint="via_route")
    def via_route():
        return Text("route-ok")

    client = app.test_client()
    response = client.get("/via-route")
    assert response.status_code == 200
    assert "route-ok" in response.get_data(as_text=True)


def test_hedron_route_async_view_via_ensure_sync() -> None:
    pytest.importorskip("asgiref")
    from importlib.util import find_spec

    # Flask async views need the optional async extra (greenlet).
    if find_spec("greenlet") is None:
        pytest.skip("Flask async extra (greenlet) not installed — sync-only Supported surface")

    hedron = HedronFlask(__name__)
    app = hedron.flask

    @hedron_route(app, "/async-route", endpoint="async_route")
    async def async_route():
        await asyncio.sleep(0)
        return Text("async-ok")

    client = app.test_client()
    response = client.get("/async-route")
    assert response.status_code == 200
    assert "async-ok" in response.get_data(as_text=True)


def test_url_reverser_with_app_context() -> None:
    hedron = HedronFlask(__name__)
    hedron.flask.config["SERVER_NAME"] = "example.test"

    @hedron.flask.get("/named")
    def named():
        return "x"

    reverser = FlaskUrlReverser(hedron.flask)
    path = reverser.reverse(UrlReverseRequest(name="named"))
    assert path == "/named"

    mounted = reverser.reverse(UrlReverseRequest(name="named", root_path="/app"))
    assert mounted == "/app/named"
    assert "http" not in mounted


def test_interaction_status_and_existing_headers() -> None:
    from hedron_flask import interaction_response

    hedron = HedronFlask(__name__)
    with hedron.flask.test_request_context("/"):
        response = interaction_response(
            InteractionResult(content=Text("body"), status_code=202, explanation="accepted"),
            extra_headers={"Retry-After": "5"},
        )
    assert response.status_code == 202
    assert response.headers.get("Retry-After") == "5"
    assert "body" in response.get_data(as_text=True)


def test_extra_headers_cannot_overwrite_hx_redirect() -> None:
    from hedron_flask import interaction_response

    hedron = HedronFlask(__name__)
    with hedron.flask.test_request_context("/"):
        response = interaction_response(
            InteractionResult(content=Text("body"), redirect="/safe"),
            extra_headers={"HX-Redirect": "/evil"},
        )
    assert response.headers.get("HX-Redirect") == "/safe"


def test_flask_reference_import_boundary() -> None:
    """Reference slice must not import FastAPI flagship package."""
    path = ROOT / "examples" / "flask-reference" / "app.py"
    text = path.read_text(encoding="utf-8")
    assert "from hedron import" not in text
    assert "import hedron\n" not in text
    assert "from hedron_flask" in text


def test_undeclared_hx_target_is_forbidden() -> None:
    from hedron_flask import interaction_response

    hedron = HedronFlask(__name__)
    with hedron.flask.test_request_context(
        "/",
        headers={"HX-Request": "true", "HX-Target": "#panel"},
    ):
        response = interaction_response(InteractionResult(content=Text("body")))
    assert response.status_code == 403
