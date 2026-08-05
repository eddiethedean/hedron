"""Portable adapter harness scenarios (phase 0.11)."""

from __future__ import annotations

import django
from django.conf import settings
from django.test import Client
from fastapi import FastAPI
from flask import Flask, request

from hedron import Heading, Hedron, Page, Text
from hedron.testing.adapters import (
    assert_fragment_body,
    assert_htmx_trigger,
    assert_page_document,
    django_fixture,
    fastapi_fixture,
    flask_fixture,
)
from hedron_core.interaction import InteractionResult
from hedron_flask import HedronBlueprint, HedronFlask


def _ensure_django() -> None:
    if settings.configured:
        return
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-secret",
        ROOT_URLCONF="tests.adapters.django.urls",
        ALLOWED_HOSTS=["testserver"],
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ],
        CSRF_HEADER_NAME="HTTP_X_CSRF_TOKEN",
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django.contrib.sessions",
            "hedron_django.apps.HedronDjangoConfig",
        ],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        USE_TZ=True,
    )
    django.setup()


def _fastapi_app() -> FastAPI:
    app = Hedron(
        title="harness",
        security="standard",
        session_secret="harness-secret",
        explorer="off",
    )

    @app.page("/")
    def home() -> Page:
        return Page(Heading("FastAPI Home", level=1), title="Home")

    @app.component("/fragment")
    def fragment() -> InteractionResult:
        return InteractionResult(
            content=Text("FastAPI fragment"),
            trigger="harness-refreshed",
            explanation="harness",
        )

    @app.action("/act")
    def act() -> InteractionResult:
        return InteractionResult(
            content=Text("FastAPI saved"),
            trigger="harness-saved",
            explanation="action",
        )

    return app


def _flask_app() -> Flask:
    hedron = HedronFlask()
    ui = HedronBlueprint("ui", __name__)

    @ui.page("/")
    def home():
        return Page(Heading("Flask Home", level=1), title="Home")

    @ui.component("/fragment")
    def fragment():
        return InteractionResult(
            content=Text("Flask fragment"),
            trigger="harness-refreshed",
            explanation="harness",
        )

    @ui.action("/act", methods=["POST"])
    def act():
        return InteractionResult(
            content=Text("Flask saved"),
            trigger="harness-saved",
            explanation="action",
        )

    @ui.page("/cookie-echo")
    def cookie_echo():
        seen = request.cookies.get("harness_token", "")
        return Page(Text(f"cookie:{seen}"), title="Cookie")

    app = Flask(__name__)
    app.secret_key = "test"
    hedron.init_app(app)
    app.register_blueprint(ui)
    return app


def test_portable_page_fastapi() -> None:
    fixture = fastapi_fixture(_fastapi_app())
    response = fixture.get("/")
    assert_page_document(response)
    assert "FastAPI Home" in response.body
    assert "hedron_csrf" in response.cookies


def test_portable_fragment_fastapi() -> None:
    fixture = fastapi_fixture(_fastapi_app())
    response = fixture.get("/fragment", headers={"HX-Request": "true"})
    assert_fragment_body(response, contains="FastAPI fragment")
    assert_htmx_trigger(response, "harness-refreshed")


def test_portable_post_csrf_fastapi() -> None:
    fixture = fastapi_fixture(_fastapi_app())
    seeded = fixture.get("/")
    token = seeded.cookies["hedron_csrf"]
    denied = fixture.post("/act", data={"x": "1"}, cookies={"hedron_csrf": token})
    assert denied.status_code == 403
    ok = fixture.post(
        "/act",
        data={"csrf_token": token},
        cookies={"hedron_csrf": token},
    )
    assert ok.status_code == 200
    assert "FastAPI saved" in ok.body
    assert_htmx_trigger(ok, "harness-saved")


def test_portable_page_flask() -> None:
    fixture = flask_fixture(_flask_app())
    response = fixture.get("/")
    assert_page_document(response)
    assert "Flask Home" in response.body
    assert "hedron_csrf" in response.cookies


def test_portable_fragment_flask() -> None:
    fixture = flask_fixture(_flask_app())
    response = fixture.get("/fragment", headers={"HX-Request": "true"})
    assert_fragment_body(response, contains="Flask fragment")
    assert_htmx_trigger(response, "harness-refreshed")


def test_portable_post_csrf_flask() -> None:
    fixture = flask_fixture(_flask_app())
    seeded = fixture.get("/")
    token = seeded.cookies["hedron_csrf"]
    denied = fixture.post("/act", cookies={"hedron_csrf": token})
    assert denied.status_code == 403
    ok = fixture.post(
        "/act",
        data={"csrf_token": token},
        cookies={"hedron_csrf": token},
    )
    assert ok.status_code == 200
    assert "Flask saved" in ok.body
    assert_htmx_trigger(ok, "harness-saved")


def test_flask_fixture_cookies_visible_on_request() -> None:
    fixture = flask_fixture(_flask_app())
    response = fixture.get("/cookie-echo", cookies={"harness_token": "abc123"})
    assert_page_document(response)
    assert "cookie:abc123" in response.body


def test_portable_page_django() -> None:
    _ensure_django()
    fixture = django_fixture(Client(enforce_csrf_checks=True))
    response = fixture.get("/page/")
    assert_page_document(response)
    assert "Hello" in response.body
    assert "csrftoken" in response.cookies


def test_portable_fragment_django() -> None:
    _ensure_django()
    fixture = django_fixture(Client())
    response = fixture.get("/fragment/", headers={"HX-Request": "true"})
    assert_fragment_body(response, contains="Fragment body")


def test_portable_htmx_trigger_django() -> None:
    _ensure_django()
    fixture = django_fixture(Client())
    response = fixture.get("/interaction/", headers={"HX-Request": "true"})
    assert_fragment_body(response, contains="Updated")
    assert_htmx_trigger(response, "refreshed")


def test_portable_post_csrf_django() -> None:
    _ensure_django()
    fixture = django_fixture(Client(enforce_csrf_checks=True))
    seeded = fixture.get("/action/")
    token = seeded.cookies["csrftoken"]
    denied = fixture.post("/action/", data={"name": "Ada"}, cookies={"csrftoken": token})
    assert denied.status_code == 403
    ok_form = fixture.post(
        "/action/",
        data={"csrfmiddlewaretoken": token, "name": "Ada"},
        cookies={"csrftoken": token},
    )
    assert ok_form.status_code == 200
    assert "saved" in ok_form.body
    ok_header = fixture.post(
        "/action/",
        data={"name": "Ada"},
        headers={"X-CSRF-Token": token},
        cookies={"csrftoken": token},
    )
    assert ok_header.status_code == 200
    assert "saved" in ok_header.body
