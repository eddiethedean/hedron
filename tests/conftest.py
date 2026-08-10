"""Shared test fixtures."""

from __future__ import annotations

import django
import pytest
from django.conf import settings

from hedron.concurrency import reset_concurrency_for_tests
from hedron.tracing import reset_tracing_for_tests
from hedron_core import reset_cache_for_tests, reset_registry_for_tests
from hedron_core.audit import reset_security_audit_for_tests
from hedron_core.icons import clear_icons_for_tests
from hedron_core.jobs import reset_jobs_for_tests
from hedron_core.plugins import reset_explorer_panels_for_tests
from hedron_core.prepare import reset_prepare_for_tests


@pytest.fixture(scope="session", autouse=True)
def _configure_django_once() -> None:
    """Establish one complete Django configuration before any test module runs.

    Django settings and the app registry are process-global and cannot be safely
    reconfigured by individual test modules.  Keeping the supported adapter
    configuration here makes test collection order irrelevant.
    """
    if settings.configured:
        return
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


def _reset_process_state() -> None:
    """Reset mutable singleton state so tests remain order-independent."""
    reset_cache_for_tests()
    reset_jobs_for_tests()
    reset_security_audit_for_tests()
    reset_prepare_for_tests()
    clear_icons_for_tests()
    reset_explorer_panels_for_tests()
    reset_concurrency_for_tests()
    reset_tracing_for_tests()
    try:
        from hedron_explorer.router import reset_explorer_runtime_for_tests
    except ImportError:
        # Explorer is an optional package outside the workspace test environment.
        pass
    else:
        reset_explorer_runtime_for_tests()


@pytest.fixture(autouse=True)
def _reset_hedron_registry() -> None:
    _reset_process_state()
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield
    _reset_process_state()
