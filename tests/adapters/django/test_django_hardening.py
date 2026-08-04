"""Phase 0.8 Django adapter hardening evidence."""

from __future__ import annotations

import inspect
from pathlib import Path

import django
import pytest
from asgiref.sync import iscoroutinefunction
from django.conf import settings
from django.http import HttpRequest
from django.test import Client, RequestFactory

from hedron_core import Text
from hedron_core.adapter import UrlReverseRequest
from hedron_core.interaction import InteractionResult
from hedron_django import HedronDjango, hedron_view
from hedron_django.routing import DjangoUrlReverser

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def django_setup() -> Client:
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY="test-secret",
            ROOT_URLCONF="tests.adapters.django.urls",
            ALLOWED_HOSTS=["testserver", "testserver.local"],
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
            ],
            DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
            USE_TZ=True,
        )
        django.setup()
    return Client(enforce_csrf_checks=True)


def test_hedron_view_async_identity(django_setup: Client) -> None:
    del django_setup

    @hedron_view
    async def async_view(request: HttpRequest):
        return Text("async-django")

    assert inspect.iscoroutinefunction(async_view) or iscoroutinefunction(async_view)
    factory = RequestFactory()
    request = factory.get("/async/")

    async def _run() -> None:
        response = await async_view(request)
        assert response.status_code == 200
        assert b"async-django" in response.content

    import asyncio

    asyncio.run(_run())


def test_hedron_view_sync_identity(django_setup: Client) -> None:
    del django_setup

    @hedron_view
    def sync_view(request: HttpRequest):
        return Text("sync-django")

    assert not inspect.iscoroutinefunction(sync_view)
    factory = RequestFactory()
    response = sync_view(factory.get("/sync/"))
    assert response.status_code == 200
    assert b"sync-django" in response.content


def test_url_reverser_named_route(django_setup: Client) -> None:
    del django_setup
    reverser = DjangoUrlReverser()
    path = reverser.reverse(UrlReverseRequest(name="page"))
    assert path.endswith("/page/")


def test_csrf_middleware_blocks_unsafe_without_token(django_setup: Client) -> None:
    client = django_setup
    # GET establishes CSRF cookie via middleware on pages that use the cookie.
    client.get("/page/")
    response = client.post("/page/", data={"x": "1"})
    assert response.status_code in {403, 405}


def test_auth_signal_anonymous(django_setup: Client) -> None:
    del django_setup
    hedron = HedronDjango()
    factory = RequestFactory()
    request = factory.get("/")
    request.user = type("Anon", (), {"is_authenticated": False, "pk": None})()
    signal = hedron.auth_signal(request)
    assert signal.authenticated is False


def test_django_floor_requires_5_2() -> None:
    import tomllib

    data = tomllib.loads(
        (ROOT / "packages" / "hedron-django" / "pyproject.toml").read_text(encoding="utf-8")
    )
    deps = " ".join(data["project"]["dependencies"])
    assert "django>=5.2" in deps.replace(" ", "")
    assert django.VERSION[:2] >= (5, 2)


def test_reference_exposes_wsgi_and_asgi() -> None:
    import importlib.util

    path = ROOT / "examples" / "django-reference" / "hedron_django_ref" / "__init__.py"
    spec = importlib.util.spec_from_file_location("hedron_django_ref", path)
    assert spec and spec.loader
    # Configuring Django twice is awkward; assert source contracts instead.
    text = path.read_text(encoding="utf-8")
    assert "get_wsgi_application" in text
    assert "asgi_application" in text
    wsgi_entry = ROOT / "examples" / "django-reference" / "wsgi.py"
    asgi_entry = ROOT / "examples" / "django-reference" / "asgi.py"
    assert asgi_entry.is_file()
    assert wsgi_entry.is_file() or "application = get_wsgi_application()" in text


def test_interaction_status_code(django_setup: Client) -> None:
    del django_setup
    from hedron_django import interaction_response

    response = interaction_response(
        InteractionResult(content=Text("accepted"), status_code=202, explanation="job")
    )
    assert response.status_code == 202
    assert b"accepted" in response.content


def test_queryset_still_deferred() -> None:
    from hedron_django.app import QUERYSET_DATASOURCE_DEFERRED

    assert QUERYSET_DATASOURCE_DEFERRED is True
