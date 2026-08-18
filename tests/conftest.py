"""Shared test fixtures."""

from __future__ import annotations

import os

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


_WORKBENCH_ENV_KEYS = (
    "HEDRON_ROOT_PATH",
    "HEDRON_WORKBENCH_RESOLVED_PUBLIC_BASE",
    "HEDRON_WORKBENCH_RESOLVED_MOUNT",
    "HEDRON_WORKBENCH_RESOLVED_MODE",
    "HEDRON_WORKBENCH_RESOLVED_SOURCE",
    "HEDRON_WORKBENCH_MOUNT",
    "HEDRON_WORKBENCH_MODE",
    "HEDRON_WORKBENCH_PUBLIC_BASE_URL",
    "HEDRON_WORKBENCH_HOST",
    "HEDRON_WORKBENCH_PORT",
    "HEDRON_WORKBENCH_DEBUG",
    "HEDRON_WORKBENCH_RELOAD",
    "HEDRON_WORKBENCH_WORKERS",
    "HEDRON_WORKBENCH_OPEN_BROWSER",
    "HEDRON_WORKBENCH_FORWARDED_ALLOW_IPS",
    "HEDRON_WORKBENCH_ALLOW_EXTERNAL_BIND",
    "HEDRON_WORKBENCH_FORCE",
    "HEDRON_WORKBENCH_TOPOLOGY",
    "HEDRON_WORKBENCH_JOB",
    "HEDRON_WORKBENCH_RSERVER_URL",
    "HEDRON_TRUSTED_PROXIES",
    "FASTAPI_WORKBENCH_ROOT_PATH",
    "FASTAPI_WORKBENCH_RESOLVED_PUBLIC_BASE",
    "FASTAPI_WORKBENCH_RESOLVED_MOUNT",
    "FASTAPI_WORKBENCH_RESOLVED_MODE",
    "FASTAPI_WORKBENCH_RESOLVED_SOURCE",
    "FASTAPI_WORKBENCH_MOUNT",
    "FASTAPI_WORKBENCH_MODE",
    "FASTAPI_WORKBENCH_PUBLIC_BASE_URL",
    "FASTAPI_WORKBENCH_HOST",
    "FASTAPI_WORKBENCH_PORT",
    "FASTAPI_WORKBENCH_DEBUG",
    "FASTAPI_WORKBENCH_RELOAD",
    "FASTAPI_WORKBENCH_WORKERS",
    "FASTAPI_WORKBENCH_OPEN_BROWSER",
    "FASTAPI_WORKBENCH_FORWARDED_ALLOW_IPS",
    "FASTAPI_WORKBENCH_ALLOW_EXTERNAL_BIND",
    "FASTAPI_WORKBENCH_FORCE",
    "FASTAPI_WORKBENCH_TOPOLOGY",
    "FASTAPI_WORKBENCH_JOB",
    "FASTAPI_WORKBENCH_RSERVER_URL",
    "FASTAPI_WORKBENCH_TRUSTED_PROXIES",
    "RS_SERVER_URL",
    "WORKBENCH_FORCE",
    "WORKBENCH_DEBUG",
    "RELOAD",
    "BASE_PATH",
    "PUBLIC_BASE_URL",
    "HOST",
    "PORT",
    "FORWARDED_ALLOW_IPS",
)


@pytest.fixture(autouse=True)
def _isolate_workbench_environ() -> None:
    """Prevent Workbench launcher env from leaking into unrelated Hedron tests."""
    snapshot = {key: os.environ.get(key) for key in _WORKBENCH_ENV_KEYS}
    try:
        yield
    finally:
        for key, value in snapshot.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@pytest.fixture(autouse=True)
def _reset_hedron_registry() -> None:
    _reset_process_state()
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield
    _reset_process_state()


def _browser_suite_enabled() -> bool:
    return os.environ.get("HEDRON_BROWSER", "").strip() in {"1", "true", "yes"}


def pytest_configure(config: pytest.Config) -> None:
    """Reuse one Playwright driver when the opt-in browser suite is running."""
    del config
    if not _browser_suite_enabled():
        return
    from tests.browser._playwright import install_reuse_patches

    install_reuse_patches()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    del session, exitstatus
    if not _browser_suite_enabled():
        return
    from tests.browser._playwright import uninstall_reuse_patches

    uninstall_reuse_patches()
