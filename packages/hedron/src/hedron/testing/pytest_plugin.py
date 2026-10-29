"""Explicit pytest plugin for Hedron's optional UI scenarios.

Load with ``pytest_plugins = ["hedron.testing.pytest_plugin"]`` or
``pytest -p hedron.testing.pytest_plugin``. It deliberately has no pytest11
entry point, so installing the testing extra does not change project-wide test
collection or base-package imports.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib
import importlib.metadata

# The repository's typings/json.pyi provides the precise object-returning JSON API.
import json  # pyright: ignore[reportMissingModuleSource]
import os
import platform
import re
import stat
import sys
import uuid
from collections.abc import Callable, Generator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol, cast

import pytest

from hedron.testing._ui_testing.contribution import (
    UITestingContribution,
    validate_ui_testing_contribution,
)
from hedron.testing._ui_testing.host import validate_factory_ref
from hedron.testing._ui_testing.scenario import BrowserScenarioFactory

_RUN_ID = pytest.StashKey[str]()
_REPORTS = pytest.StashKey[set[str]]()
_CONTRIBUTIONS = pytest.StashKey[tuple[UITestingContribution, ...]]()
_FACTORIES = pytest.StashKey[list[BrowserScenarioFactory]]()
_ATTEMPTS: dict[str, int] = {}


@dataclass
class _ArtifactBudget:
    bytes_written: int = 0
    artifacts_written: int = 0


_ARTIFACT_BUDGET = _ArtifactBudget()
_WORKER_RE = re.compile(r"[A-Za-z0-9_-]{1,32}\Z")
_MAX_MANIFEST_BYTES = 512 * 1024
_MAX_ARTIFACT_BYTES_PER_WORKER = 64 * 1024 * 1024
_MAX_ARTIFACTS_PER_WORKER = 128


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("hedron-ui", "Hedron browser-scenario settings")
    group.addoption(
        "--hedron-ui-artifacts",
        default=None,
        metavar="DIR",
        help="private directory for structured Hedron UI failure manifests",
    )
    group.addoption(
        "--hedron-ui-startup-timeout",
        type=float,
        default=15.0,
        metavar="SECONDS",
        help="deadline for a managed ASGI factory to complete lifespan startup",
    )
    group.addoption(
        "--hedron-ui-shutdown-timeout",
        type=float,
        default=5.0,
        metavar="SECONDS",
        help="grace period before a managed ASGI child is forcibly stopped",
    )
    group.addoption(
        "--hedron-ui-event-capacity",
        type=int,
        default=256,
        metavar="COUNT",
        help="maximum lifecycle events retained per browser page",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "hedron_capture(profile, data): explicitly opt a synthetic UI test into raw "
        + "browser capture",
    )
    config.addinivalue_line(
        "markers",
        "hedron_ui_contribution(reference): explicitly load versioned test metadata from a "
        + "trusted package module",
    )
    config.stash[_RUN_ID] = uuid.uuid4().hex
    if not config.pluginmanager.has_plugin("playwright"):
        raise pytest.UsageError(
            "Hedron UI testing requires pytest-playwright; install hedron[testing] "
            + "and keep its 'playwright' pytest plugin enabled"
        )
    if config.pluginmanager.has_plugin("pytest_playwright_asyncio.pytest_playwright"):
        raise pytest.UsageError(
            "Hedron UI testing supports sync pytest-playwright only; remove "
            + "pytest-playwright-asyncio"
        )
    if _float_option(config, "--hedron-ui-startup-timeout", 15.0) <= 0:
        raise pytest.UsageError("--hedron-ui-startup-timeout must be positive")
    if _float_option(config, "--hedron-ui-shutdown-timeout", 5.0) <= 0:
        raise pytest.UsageError("--hedron-ui-shutdown-timeout must be positive")
    if not 16 <= _int_option(config, "--hedron-ui-event-capacity", 256) <= 4096:
        raise pytest.UsageError("--hedron-ui-event-capacity must be between 16 and 4096")


def pytest_sessionstart(session: pytest.Session) -> None:
    """Start a fresh per-process artifact budget for this pytest worker."""
    del session
    _ARTIFACT_BUDGET.bytes_written = 0
    _ARTIFACT_BUDGET.artifacts_written = 0


@pytest.fixture
def browser_context_args(
    request: pytest.FixtureRequest,
    browser_context_args: Mapping[str, object],
) -> dict[str, object]:
    """Block Service Workers only for Hedron scenarios using route enforcement."""
    options = dict(browser_context_args)
    service_workers = options.get("service_workers", "block")
    if "hedron_ui" not in request.fixturenames:
        return options
    if service_workers != "block":
        raise pytest.UsageError(
            "Hedron UI tests require service_workers='block' for request-origin enforcement"
        )
    options["service_workers"] = "block"
    return options


@pytest.fixture
def hedron_ui(
    request: pytest.FixtureRequest,
    pytestconfig: pytest.Config,
) -> Generator[BrowserScenarioFactory, None, None]:
    """Create the function-scoped Hedron scenario factory.

    The upstream ``new_context`` factory remains the only context owner and
    finalizer. Context creation is lazy: requesting ``hedron_ui`` alone does
    not start a browser or an application process.
    """
    item = cast(pytest.Item, request.node)
    _validate_context_markers(item)
    capture_profile, synthetic_declared = _capture_declaration(request)
    _validate_capture_options(
        pytestconfig,
        (capture_profile, synthetic_declared),
    )
    writer = _artifact_writer(request, pytestconfig)
    if _CONTRIBUTIONS in item.stash:
        contributions = item.stash[_CONTRIBUTIONS]
    else:
        # A dynamically requested fixture was absent from collection's static
        # fixture closure, so load and validate its explicit contribution marks.
        contributions = _load_ui_contributions(item)
        item.stash[_CONTRIBUTIONS] = contributions

    def acquire_context() -> object:
        context_args = cast(Mapping[str, object], _fixture_value(request, "browser_context_args"))
        effective_context_args = dict(context_args)
        context_marker = next(item.iter_markers("browser_context_args"), None)
        if context_marker is not None:
            effective_context_args.update(context_marker.kwargs)
        if effective_context_args.get("service_workers") != "block":
            raise pytest.UsageError(
                "Hedron UI tests require service_workers='block' for request-origin enforcement"
            )
        _validate_capture_context_args(context_args)
        new_context = cast(CallableContextFactory, _fixture_value(request, "new_context"))
        return new_context()

    factory = BrowserScenarioFactory(
        new_context=acquire_context,
        artifact_writer=writer,
        startup_timeout=_float_option(pytestconfig, "--hedron-ui-startup-timeout", 15.0),
        shutdown_timeout=_float_option(pytestconfig, "--hedron-ui-shutdown-timeout", 5.0),
        event_capacity=_int_option(pytestconfig, "--hedron-ui-event-capacity", 256),
        capture_profile=capture_profile,
        synthetic_data_declared=synthetic_declared,
        contributions=contributions,
    )
    factories = item.stash.get(_FACTORIES, list[BrowserScenarioFactory]())
    factories.append(factory)
    item.stash[_FACTORIES] = factories
    try:
        yield factory
    finally:
        reports: set[str] = item.stash.get(_REPORTS, set[str]())
        factory.close_all(test_failed=bool(reports), failure_phases=tuple(reports))
        if "manifest_write_failed" in factory.errors:
            item.add_report_section(
                "teardown",
                "Hedron UI artifact failure",
                "The bounded structured failure manifest could not be written.",
            )


class CallableContextFactory(Protocol):
    """Small typing protocol used without importing pytest-playwright internals."""

    def __call__(self, **kwargs: object) -> object: ...


class _HookOutcome(Protocol):
    def get_result(self) -> pytest.TestReport: ...


class _Mark(Protocol):
    @property
    def args(self) -> tuple[object, ...]: ...

    @property
    def kwargs(self) -> Mapping[str, object]: ...


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[object],
) -> Generator[None, object, None]:
    del call
    outcome_value = yield
    outcome = cast(_HookOutcome, outcome_value)
    report = outcome.get_result()
    if report.failed:
        failed_phases: set[str] = item.stash.get(_REPORTS, set[str]())
        failed_phases.add(report.when)
        item.stash[_REPORTS] = failed_phases
        if report.when == "teardown":
            for factory in item.stash.get(_FACTORIES, list[BrowserScenarioFactory]()):
                try:
                    factory.write_pytest_teardown_failure(tuple(failed_phases))
                except Exception as exc:  # noqa: BLE001 — report evidence failure in teardown.
                    report.sections.append(
                        (
                            "Hedron UI artifact failure during teardown",
                            "The bounded failure manifest could not be updated "
                            + f"({type(exc).__name__}).",
                        )
                    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Resolve contribution metadata before setup, including for selectively skipped tests."""
    del config
    for item in items:
        if "hedron_ui" not in _fixture_names(item):
            continue
        contributions = _load_ui_contributions(item)
        item.stash[_CONTRIBUTIONS] = contributions


def _validate_capture_options(
    config: pytest.Config,
    capture: tuple[Literal["structured", "synthetic"], bool],
) -> None:
    """Reject upstream raw capture settings for tests without synthetic consent."""
    tracing = _get_option(config, "--tracing", "off")
    screenshot = _get_option(config, "--screenshot", "off")
    video = _get_option(config, "--video", "off")
    full_page = bool(_get_option(config, "--full-page-screenshot", False))
    raw_enabled = tracing != "off" or screenshot != "off" or video != "off" or full_page
    if raw_enabled and capture != ("synthetic", True):
        raise pytest.UsageError(
            "raw Playwright capture is restricted to tests marked "
            + "@pytest.mark.hedron_capture(profile='synthetic', data='synthetic')"
        )
    if capture == ("synthetic", True):
        if tracing != "retain-on-failure":
            raise pytest.UsageError(
                "synthetic UI capture requires pytest-playwright --tracing=retain-on-failure"
            )
        if screenshot not in {"off", "only-on-failure"} or video != "off" or full_page:
            raise pytest.UsageError(
                "synthetic UI capture permits failure-only viewport screenshots; "
                + "video and full-page capture are not admitted"
            )


def _validate_context_markers(item: pytest.Item) -> None:
    for marker in item.iter_markers("browser_context_args"):
        marker_args = cast(Mapping[str, object], marker.kwargs)
        if marker_args.get("service_workers", "block") != "block":
            raise pytest.UsageError(
                "Hedron UI tests require service_workers='block' in browser_context_args markers"
            )
        _validate_capture_context_args(marker_args)


def _validate_capture_context_args(options: Mapping[str, object]) -> None:
    """Reject pytest-playwright context options that persist raw browser data."""
    raw_options = ("record_har_path", "record_video_dir")
    if any(options.get(name) is not None for name in raw_options):
        raise pytest.UsageError(
            "Hedron UI tests do not permit HAR or video recording through browser_context_args"
        )


def _load_ui_contributions(item: pytest.Item) -> tuple[UITestingContribution, ...]:
    """Load only explicitly named, bounded contribution metadata and check conflicts."""
    markers = tuple(item.iter_markers("hedron_ui_contribution"))
    if len(markers) > 8:
        raise pytest.UsageError("at most eight Hedron UI testing contributions may be loaded")
    loaded: list[UITestingContribution] = []
    try:
        hedron_version = importlib.metadata.version("hedron")
    except importlib.metadata.PackageNotFoundError as exc:
        raise pytest.UsageError(
            "Hedron package metadata is unavailable for contribution checks"
        ) from exc
    for marker in markers:
        marker_args = cast(tuple[object, ...], marker.args)
        if len(marker_args) != 1 or marker.kwargs:
            raise pytest.UsageError(
                "hedron_ui_contribution requires one import reference and no keyword arguments"
            )
        reference = marker_args[0]
        try:
            module_name, attribute = validate_factory_ref(reference)
            module = importlib.import_module(module_name)
            raw_contribution = cast(object, getattr(module, attribute))
            contribution = validate_ui_testing_contribution(
                raw_contribution,
                hedron_version=hedron_version,
            )
        except Exception as exc:
            raise pytest.UsageError(
                f"invalid or unavailable Hedron UI contribution ({type(exc).__name__})"
            ) from exc
        missing_resources = set(contribution.fixture_resources).difference(_fixture_names(item))
        if missing_resources:
            raise pytest.UsageError(
                "loaded Hedron UI contribution is missing one or more declared fixture resources"
            )
        loaded.append(contribution)

    package_ids = [item.package_id for item in loaded]
    capabilities = [capability for item in loaded for capability in item.capabilities]
    resources = [resource for item in loaded for resource in item.fixture_resources]
    if len(set(package_ids)) != len(package_ids):
        raise pytest.UsageError("duplicate Hedron UI contribution package id")
    if len(set(capabilities)) != len(capabilities):
        raise pytest.UsageError("conflicting Hedron UI contribution capability")
    if len(set(resources)) != len(resources):
        raise pytest.UsageError("conflicting Hedron UI contribution fixture resource")
    return tuple(loaded)


def _capture_declaration(
    request: pytest.FixtureRequest,
) -> tuple[Literal["structured", "synthetic"], bool]:
    return _capture_declaration_for_item(cast(pytest.Item, request.node))


def _capture_declaration_for_item(
    item: pytest.Item,
) -> tuple[Literal["structured", "synthetic"], bool]:
    marker = cast(_Mark | None, item.get_closest_marker("hedron_capture"))
    if marker is None:
        return "structured", False
    profile = _mark_value(marker, "profile")
    data = _mark_value(marker, "data")
    if profile != "synthetic" or data != "synthetic":
        raise pytest.UsageError("hedron_capture requires profile='synthetic' and data='synthetic'")
    return "synthetic", True


def _artifact_writer(
    request: pytest.FixtureRequest,
    config: pytest.Config,
) -> Callable[[Mapping[str, object]], None]:
    item = cast(pytest.Item, request.node)
    nodeid = item.nodeid
    attempt = _ATTEMPTS.get(nodeid, 0) + 1
    _ATTEMPTS[nodeid] = attempt
    worker = os.environ.get("PYTEST_XDIST_WORKER", "master")
    worker = worker if _WORKER_RE.fullmatch(worker) else "worker"
    node_key = hashlib.sha256(nodeid.encode("utf-8", errors="replace")).hexdigest()[:24]
    run_id = config.stash[_RUN_ID]
    configured = _get_option(config, "--hedron-ui-artifacts", None)
    if configured is not None and not isinstance(configured, str):
        raise pytest.UsageError("--hedron-ui-artifacts must name a directory")
    root = (
        Path(configured).expanduser()
        if configured
        else Path(config.rootpath) / ".pytest_cache" / "hedron-ui"
    )
    if root.is_symlink():
        raise pytest.UsageError("Hedron UI artifact root must not be a symlink")
    root = root.resolve()
    if root == Path(root.anchor) or root == Path.home().resolve():
        raise pytest.UsageError("Hedron UI artifact root must be a dedicated directory")
    destination_dir = root / run_id / worker / node_key / f"attempt-{attempt:04d}"
    destination = destination_dir / "manifest.json"

    def write(manifest: Mapping[str, object]) -> None:
        payload = json.dumps(
            {
                "run_id": run_id,
                "worker": worker,
                "test_key": node_key,
                "runtime": _runtime_provenance(),
                **manifest,
            },
            ensure_ascii=True,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        if len(payload) > _MAX_MANIFEST_BYTES:
            raise OSError("structured Hedron UI failure manifest exceeded its fixed size limit")
        if _ARTIFACT_BUDGET.artifacts_written >= _MAX_ARTIFACTS_PER_WORKER:
            raise OSError("structured Hedron UI artifact count exceeded its per-worker budget")
        if _ARTIFACT_BUDGET.bytes_written + len(payload) > _MAX_ARTIFACT_BYTES_PER_WORKER:
            raise OSError("structured Hedron UI artifact bytes exceeded its per-worker budget")
        _make_private_tree(root, destination_dir)
        temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
        descriptor = os.open(
            temporary,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        try:
            with os.fdopen(descriptor, "wb") as stream:
                _ = stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            _ = temporary.replace(destination)
            _ARTIFACT_BUDGET.bytes_written += len(payload)
            _ARTIFACT_BUDGET.artifacts_written += 1
        except (Exception, KeyboardInterrupt, SystemExit):
            with contextlib.suppress(OSError):
                temporary.unlink(missing_ok=True)
            raise

    return write


def _make_private_tree(root: Path, destination: Path) -> None:
    """Create/check only per-run descendants; never chmod the caller's root."""
    try:
        root.mkdir(mode=0o700, parents=True, exist_ok=True)
    except OSError as exc:
        raise OSError("Hedron UI artifact root could not be created") from exc
    if root.is_symlink() or not root.is_dir():
        raise OSError("Hedron UI artifact root is not a regular directory")
    try:
        relative = destination.relative_to(root)
    except ValueError as exc:
        raise OSError("Hedron UI artifact path escaped its selected root") from exc
    current = root
    for part in relative.parts:
        current = current / part
        with contextlib.suppress(FileExistsError):
            current.mkdir(mode=0o700)
        if current.is_symlink() or not current.is_dir():
            raise OSError("Hedron UI artifact path contains a non-directory or symlink")
        info = current.stat(follow_symlinks=False)
        if hasattr(os, "getuid") and info.st_uid != os.getuid():
            raise OSError("Hedron UI artifact directory is not owned by the current user")
        if os.name == "posix":
            current.chmod(stat.S_IRWXU)


def _runtime_provenance() -> dict[str, str | None]:
    """Record bounded package/runtime versions without environment or path values."""
    versions: dict[str, str | None] = {}
    for distribution in ("hedron", "pytest", "pytest-playwright", "playwright", "uvicorn"):
        try:
            version = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            version = None
        if version is not None and not re.fullmatch(r"[A-Za-z0-9.+!-]{1,64}", version):
            version = "unavailable"
        versions[distribution.replace("-", "_")] = version
    return {
        "python": platform.python_version(),
        "platform": sys.platform,
        **versions,
    }


def _get_option(config: pytest.Config, name: str, default: object) -> object:
    try:
        value: object = config.getoption(name)
        return value
    except (ValueError, AttributeError):
        return default


def _float_option(config: pytest.Config, name: str, default: float) -> float:
    value = _get_option(config, name, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise pytest.UsageError(f"{name} must be numeric")
    return float(value)


def _int_option(config: pytest.Config, name: str, default: int) -> int:
    value = _get_option(config, name, default)
    if type(value) is not int:
        raise pytest.UsageError(f"{name} must be an integer")
    return value


def _fixture_value(request: pytest.FixtureRequest, name: str) -> object:
    return cast(object, request.getfixturevalue(name))


def _fixture_names(item: pytest.Item) -> tuple[str, ...]:
    value: object = getattr(item, "fixturenames", ())
    if not isinstance(value, (list, tuple)):
        return ()
    names: list[str] = []
    for candidate in cast(list[object] | tuple[object, ...], value):
        if isinstance(candidate, str):
            names.append(candidate)
    return tuple(names)


def _mark_value(marker: _Mark, name: str, default: object = None) -> object:
    return marker.kwargs.get(name, default)
