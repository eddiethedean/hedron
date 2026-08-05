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
    app = Hedron(title="harness")

    @app.page("/")
    def home() -> Page:
        return Page(Heading("FastAPI Home", level=1), title="Home")

    @app.component("/fragment")
    def fragment() -> InteractionResult:
        return InteractionResult(content=Text("FastAPI fragment"), explanation="harness")

    return app


def _flask_app() -> Flask:
    hedron = HedronFlask()
    ui = HedronBlueprint("ui", __name__)

    @ui.page("/")
    def home():
        return Page(Heading("Flask Home", level=1), title="Home")

    @ui.component("/fragment")
    def fragment():
        return InteractionResult(content=Text("Flask fragment"), explanation="harness")

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


def test_portable_fragment_fastapi() -> None:
    fixture = fastapi_fixture(_fastapi_app())
    response = fixture.get("/fragment", headers={"HX-Request": "true"})
    assert_fragment_body(response, contains="FastAPI fragment")


def test_portable_page_flask() -> None:
    fixture = flask_fixture(_flask_app())
    response = fixture.get("/")
    assert_page_document(response)
    assert "Flask Home" in response.body


def test_portable_fragment_flask() -> None:
    fixture = flask_fixture(_flask_app())
    response = fixture.get("/fragment", headers={"HX-Request": "true"})
    assert_fragment_body(response, contains="Flask fragment")


def test_flask_fixture_cookies_visible_on_request() -> None:
    fixture = flask_fixture(_flask_app())
    response = fixture.get("/cookie-echo", cookies={"harness_token": "abc123"})
    assert_page_document(response)
    assert "cookie:abc123" in response.body


def test_portable_page_django() -> None:
    _ensure_django()
    fixture = django_fixture(Client())
    response = fixture.get("/page/")
    assert_page_document(response)
    assert "Hello" in response.body


def test_portable_fragment_django() -> None:
    _ensure_django()
    fixture = django_fixture(Client())
    response = fixture.get("/fragment/", headers={"HX-Request": "true"})
    assert_fragment_body(response, contains="Fragment body")
