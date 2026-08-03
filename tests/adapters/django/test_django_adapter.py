"""Adapter tests for hedron-django."""

from __future__ import annotations

import ast
from pathlib import Path

import django
import pytest
from django.conf import settings
from django.test import Client

from hedron_core.rendering import RenderMode
from hedron_django import HedronDjango
from hedron_django.htmx import render_mode_for_request

ROOT = Path(__file__).resolve().parents[3]
DJANGO_SRC = ROOT / "packages" / "hedron-django" / "src" / "hedron_django"
FORBIDDEN = frozenset({"fastapi", "starlette", "hedron"})


@pytest.fixture(scope="module")
def django_client() -> Client:
    if not settings.configured:
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
            ],
            INSTALLED_APPS=[],
            USE_TZ=True,
        )
    django.setup()
    return Client()


def test_page_render(django_client: Client) -> None:
    response = django_client.get("/page/")
    assert response.status_code == 200
    content = response.content.decode()
    assert "<h1" in content
    assert "<html" in content


def test_fragment_render(django_client: Client) -> None:
    response = django_client.get("/fragment/", HTTP_HX_REQUEST="true")
    assert response.status_code == 200
    content = response.content.decode()
    assert "Fragment body" in content
    assert "<html" not in content


def test_interaction_headers(django_client: Client) -> None:
    response = django_client.get("/interaction/")
    assert response.status_code == 200
    assert response.headers.get("HX-Trigger") == "refreshed"
    assert "Updated" in response.content.decode()


def test_render_mode_for_request() -> None:
    assert render_mode_for_request({}) is RenderMode.PAGE
    assert render_mode_for_request({"HX-Request": "true"}) is RenderMode.FRAGMENT


def test_queryset_datasource_deferred() -> None:
    from hedron_django.app import QUERYSET_DATASOURCE_DEFERRED

    assert QUERYSET_DATASOURCE_DEFERRED is True
    caps = HedronDjango().capabilities
    qs = next(c for c in caps.capabilities if c.name == "queryset_datasource")
    assert qs.supported is False


def test_no_fastapi_imports_in_source() -> None:
    found: list[str] = []
    for path in DJANGO_SRC.rglob("*.py"):
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
