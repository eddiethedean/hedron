"""Shared Django settings for adapter tests (configure once)."""

from __future__ import annotations

import django
import pytest
from django.conf import settings
from django.test import Client


@pytest.fixture(scope="session", autouse=True)
def _configure_django() -> None:
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
        # Accept Hedron portable X-CSRF-Token (matches reference app).
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


@pytest.fixture
def django_client() -> Client:
    return Client()


@pytest.fixture
def django_csrf_client() -> Client:
    return Client(enforce_csrf_checks=True)
