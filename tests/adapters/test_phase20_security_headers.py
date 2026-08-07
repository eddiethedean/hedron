"""CSP-020: Flask and Django emit portable SecurityPolicy response headers."""

from __future__ import annotations

import ast
from pathlib import Path

import django
import pytest
from django.conf import settings
from django.test import Client
from flask.testing import FlaskClient

from hedron_core import Heading, Page
from hedron_core.rendering import RenderMode
from hedron_core.security_policy import SecurityPolicy
from hedron_flask import HedronFlask
from hedron_flask.responses import component_response

ROOT = Path(__file__).resolve().parents[2]
FLASK_SRC = ROOT / "packages" / "hedron-flask" / "src" / "hedron_flask"
DJANGO_SRC = ROOT / "packages" / "hedron-django" / "src" / "hedron_django"
FORBIDDEN = frozenset({"fastapi", "starlette", "hedron"})


def _assert_standard_headers(headers: object) -> None:
    expected = SecurityPolicy.from_name("standard").response_headers(authenticated=False)
    assert headers.get("Content-Security-Policy") == expected["Content-Security-Policy"]
    assert headers.get("X-Frame-Options") == expected["X-Frame-Options"]
    assert headers.get("X-Content-Type-Options") == expected["X-Content-Type-Options"]
    assert headers.get("Referrer-Policy") == expected["Referrer-Policy"]


@pytest.fixture(scope="module")
def _django_ready() -> None:
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
            "hedron_django.middleware.HedronSecurityHeadersMiddleware",
        ],
        CSRF_HEADER_NAME="HTTP_X_CSRF_TOKEN",
        HEDRON_SECURITY_PROFILE="standard",
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


@pytest.fixture
def flask_client() -> FlaskClient:
    hedron = HedronFlask(__name__, security="standard")
    app = hedron.flask
    assert app is not None
    app.secret_key = "test"

    @app.get("/page")
    def page():
        return component_response(
            Page(Heading("Hello", level=1), title="Test"),
            mode=RenderMode.PAGE,
        )

    return app.test_client()


def test_flask_standard_emits_csp_and_frame_options(flask_client: FlaskClient) -> None:
    response = flask_client.get("/page")
    assert response.status_code == 200
    _assert_standard_headers(response.headers)


def test_flask_security_policy_from_core() -> None:
    hedron = HedronFlask(__name__, security=SecurityPolicy.from_name("strict"))
    assert hedron.security_policy.profile.value == "strict"
    assert hedron.security_policy.content_security_policy is not None
    assert "frame-ancestors" in hedron.security_policy.content_security_policy


def test_django_standard_emits_csp_and_frame_options(_django_ready: None) -> None:
    response = Client().get("/page/")
    assert response.status_code == 200
    _assert_standard_headers(response.headers)


def test_adapters_do_not_import_fastapi() -> None:
    found: list[str] = []
    for src in (FLASK_SRC, DJANGO_SRC):
        for path in src.rglob("*.py"):
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
