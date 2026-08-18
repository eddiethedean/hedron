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
            CSRF_HEADER_NAME="HTTP_X_CSRF_TOKEN",
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
    # GET establishes CSRF cookie via hedron_view seeding.
    seeded = client.get("/action/")
    assert seeded.status_code == 200
    assert "csrftoken" in seeded.cookies
    denied = client.post("/action/", data={"x": "1"})
    assert denied.status_code == 403


def test_csrf_post_succeeds_with_form_token(django_setup: Client) -> None:
    client = django_setup
    get = client.get("/action/")
    token = get.cookies["csrftoken"].value
    ok = client.post("/action/", data={"csrfmiddlewaretoken": token, "name": "Ada"})
    assert ok.status_code == 200
    assert b"saved" in ok.content


def test_csrf_post_succeeds_with_portable_header(django_setup: Client) -> None:
    client = django_setup
    get = client.get("/action/")
    token = get.cookies["csrftoken"].value
    ok = client.post(
        "/action/",
        data={"name": "Ada"},
        HTTP_X_CSRF_TOKEN=token,
    )
    assert ok.status_code == 200
    assert b"saved" in ok.content


def test_csrf_cookie_seeded_on_respond_get(django_setup: Client) -> None:
    client = django_setup
    from hedron_django.csrf import (
        DJANGO_CSRF_HEADER,
        PORTABLE_CSRF_HEADER,
        csrf_header_name,
        seed_csrf_cookie,
    )

    assert csrf_header_name() in {PORTABLE_CSRF_HEADER, DJANGO_CSRF_HEADER}
    response = client.get("/page/")
    assert response.status_code == 200
    assert "csrftoken" in response.cookies

    # Offline seed + respond path still returns a token for templates/helpers.
    hedron = HedronDjango()
    factory = RequestFactory()
    request = factory.get("/seed/")
    token = seed_csrf_cookie(request)
    assert token
    offline = hedron.respond(Text("seeded"), request)
    assert offline.status_code == 200
    assert b"seeded" in offline.content


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
    import importlib
    import sys

    root = str(ROOT / "examples" / "django-reference")
    if root not in sys.path:
        sys.path.insert(0, root)
    # Importing the package configures Django once for this process.
    mod = importlib.import_module("hedron_django_ref")
    assert callable(mod.application)
    assert mod.asgi_application is not None
    # Load asgi.py entry the same way a server would (module path on sys.path).
    asgi_path = ROOT / "examples" / "django-reference" / "asgi.py"
    text = asgi_path.read_text(encoding="utf-8")
    assert "asgi_application as application" in text
    assert mod.asgi_application is not None


def test_interaction_status_code(django_setup: Client) -> None:
    del django_setup
    from hedron_django import interaction_response

    response = interaction_response(
        InteractionResult(content=Text("accepted"), status_code=202, explanation="job")
    )
    assert response.status_code == 202
    assert b"accepted" in response.content


def test_undeclared_hx_target_is_forbidden(django_setup: Client) -> None:
    del django_setup
    from django.test import RequestFactory

    from hedron_django import interaction_response

    request = RequestFactory().get("/", HTTP_HX_REQUEST="true", HTTP_HX_TARGET="#panel")
    response = interaction_response(InteractionResult(content=Text("body")), request=request)
    assert response.status_code == 403


def test_hedron_view_csrf_rejects_before_handler(django_setup: Client) -> None:
    del django_setup
    from django.test import RequestFactory

    ran = {"n": 0}

    @hedron_view
    def mutating(request: HttpRequest):
        ran["n"] += 1
        return Text("mutated")

    response = mutating(RequestFactory().post("/x/", data={"name": "Ada"}))
    assert response.status_code == 403
    assert ran["n"] == 0


def test_hedron_view_async_csrf_rejects_before_handler(django_setup: Client) -> None:
    del django_setup
    import asyncio

    from django.test import RequestFactory

    ran = {"n": 0}

    @hedron_view
    async def mutating(request: HttpRequest):
        ran["n"] += 1
        return Text("mutated")

    async def _run() -> None:
        response = await mutating(RequestFactory().post("/x/", data={"name": "Ada"}))
        assert response.status_code == 403
        assert ran["n"] == 0

    asyncio.run(_run())


def test_401_hedron_django_production_gate(django_setup: Client, monkeypatch: pytest.MonkeyPatch) -> None:
    del django_setup
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv("HEDRON_SECURITY_RISK_ACCEPTANCE", raising=False)
    with pytest.raises(RuntimeError, match="InMemoryJobBackend|Production security|weak-session-secret"):
        HedronDjango()
