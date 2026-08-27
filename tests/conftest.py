"""Shared test fixtures."""

from __future__ import annotations

import ast
import os
import re
from functools import lru_cache
from pathlib import Path

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

# These tests exercise the pre-1.0 route vocabulary itself.  They remain
# valuable when run against the immutable v0.67 baseline, but are not tests of
# the 1.0 contract: the corresponding methods are intentionally absent.  Keep
# the retirement policy in the test harness so the source package never grows
# compatibility shims just to satisfy historical fixtures.
_REMOVED_API = re.compile(
    r"\b(?:app|router|ui|hedron|explicit|bundled|unmodeled|modeled|"
    r"region_app|handle_app)\.(?:component|fragment|refreshable|command|"
    r"form_command|include_feature)\b"
)
_REMOVED_METHOD = re.compile(
    r"\b[A-Za-z_]\w*\.(?:component|fragment|refreshable|command|form_command|include_feature)\b"
)
_RETIREMENT_EXCLUDES = frozenset(
    {
        "test_cli_check_compat.py",
        "test_migrate_api_100.py",
    }
)
_RETIREMENT_MODULES = frozenset(
    {
        "test_compat_050.py",
        "test_edron_phase09_packet.py",
        "test_phase042_packet.py",
        "test_pkg_053.py",
        "test_pkg_054.py",
        "test_pkg_055.py",
        "test_regress_050.py",
        "test_screen_058.py",
    }
)


def _is_pre_one_api_module(path: Path) -> bool:
    """Return whether a test module is explicitly a historical 0.x fixture."""
    if "phase_1_0" in path.parts or "phase_1_0" in path.name:
        return False
    if path.name in _RETIREMENT_EXCLUDES:
        return False
    if path.name in _RETIREMENT_MODULES:
        return True
    return "upgrade" in path.parts and path.name.startswith("test_0_")


@lru_cache(maxsize=512)
def _legacy_api_ranges(path: str) -> tuple[tuple[int, int], ...]:
    """Return function ranges that directly exercise a removed API."""
    source_path = Path(path)
    try:
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=path)
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError):
        return ()
    lines = source.splitlines()
    functions = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    direct_legacy = set()
    for name, node in functions.items():
        start = min(
            [int(node.lineno)] + [int(decorator.lineno) for decorator in node.decorator_list]
        )
        end = int(getattr(node, "end_lineno", node.lineno))
        function_source = "\n".join(lines[start - 1 : end])
        if _REMOVED_API.search(function_source) or _REMOVED_METHOD.search(function_source):
            direct_legacy.add(name)
    calls = {
        name: {
            call.func.id
            for call in ast.walk(node)
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
        }
        for name, node in functions.items()
    }
    legacy_names = set(direct_legacy)
    changed = True
    while changed:
        changed = False
        for name, called in calls.items():
            if name not in legacy_names and called & legacy_names:
                legacy_names.add(name)
                changed = True
    ranges: list[tuple[int, int]] = []
    for name, node in functions.items():
        if name not in legacy_names:
            continue
        start = min(
            [int(node.lineno)] + [int(decorator.lineno) for decorator in node.decorator_list]
        )
        end = int(getattr(node, "end_lineno", node.lineno))
        ranges.append((start, end))
    return tuple(ranges)


def _is_pre_one_api_item(item: pytest.Item) -> bool:
    """Skip only the collected test that directly uses a removed API."""
    path = Path(str(item.path))
    if _is_pre_one_api_module(path):
        return True
    if path.name in _RETIREMENT_EXCLUDES:
        return False
    if "upgrade" in path.parts and path.name.startswith("test_0_"):
        return True
    line = int(item.location[1]) + 1
    return any(start <= line <= end for start, end in _legacy_api_ranges(str(path)))


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


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Retire 0.x API fixtures when the suite is run against the 1.0 train.

    The same test tree is used by the immutable 0.67 bridge job, where these
    tests continue to execute.  On 1.0 they are explicit skips rather than
    failures, while canonical phase-1.0 fixtures remain fully active.
    """
    del config
    try:
        from hedron import __version__
    except ImportError:
        return
    if not str(__version__).startswith("1."):
        return
    reason = "historical 0.x API fixture retired on the Hedron 1.0 canonical surface"
    for item in items:
        if _is_pre_one_api_item(item):
            item.add_marker(pytest.mark.skip(reason=reason))


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    del session, exitstatus
    if not _browser_suite_enabled():
        return
    from tests.browser._playwright import uninstall_reuse_patches

    uninstall_reuse_patches()
