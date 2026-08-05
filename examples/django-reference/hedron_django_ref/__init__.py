"""Manage-less Django reference slice (settings + urls + views)."""

from __future__ import annotations

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import HttpRequest
from django.urls import path

from hedron_core import Heading, Page, Text
from hedron_core.interaction import InteractionResult
from hedron_django import HedronDjango, hedron_view

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="hedron-django-reference-secret",
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=["*"],
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
        ],
        # Accept Hedron portable X-CSRF-Token (see docs/guides/security.md / upgrade.md).
        CSRF_HEADER_NAME="HTTP_X_CSRF_TOKEN",
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "hedron_django.apps.HedronDjangoConfig",
        ],
        USE_TZ=True,
    )

hedron = HedronDjango()


@hedron_view
def home(request: HttpRequest):
    return hedron.respond(
        Page(
            Heading("Hedron Django Reference", level=1),
            Text("Native Django URLconf with Hedron components."),
            title="Django Reference",
        ),
        request,
    )


@hedron_view
def fragment(request: HttpRequest):
    return InteractionResult(content=Text("HTMX fragment refreshed"), explanation="demo fragment")


urlpatterns = [
    path("", home, name="home"),
    path("fragment/", fragment, name="fragment"),
]

application = get_wsgi_application()

try:
    from django.core.asgi import get_asgi_application

    asgi_application = get_asgi_application()
except Exception:  # noqa: BLE001 — ASGI optional for the WSGI-first slice
    asgi_application = None
