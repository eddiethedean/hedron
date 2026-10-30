"""Unit coverage for the optional managed UI-testing host."""

from __future__ import annotations

import json
import time
from types import SimpleNamespace
from typing import Protocol

import httpx
import pytest

from hedron.testing._ui_testing.host import (
    ManagedASGIHost,
    ManagedHostCleanupError,
    ManagedHostError,
    validate_factory_config,
    validate_factory_ref,
    validate_loopback_url,
    validate_origin,
    validate_root_path,
)
from hedron.testing._ui_testing.scenario import BrowserScenario, UIEvent


class _RecordProperty(Protocol):
    def __call__(self, name: str, value: object) -> None: ...


def test_managed_host_owns_child_app_and_root_path() -> None:
    host = ManagedASGIHost(
        "hedron.testing.examples.profile_app:create_app",
        config={"title": "Managed profile", "root_path": "/demo"},
        root_path="/demo",
        startup_timeout=20,
    )
    base_url = host.start()
    try:
        readiness = httpx.get(f"{base_url}/_ui-testing/ready", timeout=5)
        response = httpx.get(f"{base_url}/", timeout=5)
        assert readiness.status_code == 200
        assert readiness.json() == {"ready": True}
        assert response.status_code == 200
        assert "Managed profile" in response.text
        assert "/demo/" in response.url.path
        assert "/demo/hedron-static/htmx.min.js" in response.text
        asset = httpx.get(f"{host.origin}/demo/hedron-static/htmx.min.js", timeout=5)
        assert asset.status_code == 200
        assert "htmx" in asset.text
        assert host.cleanup_error is None
    finally:
        host.close()


def test_managed_host_resource_budget(record_property: _RecordProperty) -> None:
    startup_ms: list[float] = []
    shutdown_ms: list[float] = []
    child_counts: list[int] = []
    for _ in range(5):
        host = ManagedASGIHost(
            "hedron.testing.examples.profile_app:create_app",
            config={"title": "Host resource budget"},
        )
        started = time.perf_counter()
        _ = host.start()
        startup_ms.append((time.perf_counter() - started) * 1000)
        child_counts.append(int(host._process is not None and host._process.is_alive()))
        stopped = time.perf_counter()
        host.close()
        shutdown_ms.append((time.perf_counter() - stopped) * 1000)
    record_property("host_startup_ms", json.dumps(startup_ms))
    record_property("host_shutdown_ms", json.dumps(shutdown_ms))
    record_property("host_child_processes", json.dumps(child_counts))
    assert max(startup_ms) <= 15_000
    assert max(shutdown_ms) <= 7_000
    assert max(child_counts) == 1


def test_managed_host_reports_factory_startup_failure_without_leaking_child() -> None:
    host = ManagedASGIHost(
        "hedron.testing.examples.profile_app:create_app",
        config={"title": ""},
        startup_timeout=20,
    )
    with pytest.raises(ManagedHostError, match=r"startup failed \(ValueError\)"):
        host.start()
    host.close()


def test_shutdown_uses_confirmation_received_after_child_exits() -> None:
    alive_states = iter((True, False, False, False))
    pending = [{"kind": "stopped", "lifespan_complete": True}]
    host = ManagedASGIHost("example:factory")
    host._started = True
    host._process = SimpleNamespace(
        is_alive=lambda: next(alive_states, False),
        exitcode=0,
        close=lambda: None,
    )
    host._connection = SimpleNamespace(
        send=lambda _message: None,
        poll=lambda _timeout: bool(pending),
        recv=lambda: pending.pop(0),
        close=lambda: None,
    )

    host.close()

    assert host.cleanup_error is None


def test_shutdown_rejects_failed_lifespan_confirmation() -> None:
    alive_states = iter((True, False, False, False))
    pending = [{"kind": "stopped", "lifespan_complete": False}]
    host = ManagedASGIHost("example:factory")
    host._started = True
    host._process = SimpleNamespace(
        is_alive=lambda: next(alive_states, False),
        exitcode=0,
        close=lambda: None,
    )
    host._connection = SimpleNamespace(
        send=lambda _message: None,
        poll=lambda _timeout: bool(pending),
        recv=lambda: pending.pop(0),
        close=lambda: None,
    )

    with pytest.raises(ManagedHostCleanupError, match="without confirmed lifespan"):
        host.close()


@pytest.mark.parametrize(
    ("config", "error"),
    [
        ({"not-json": object()}, TypeError),
        ({"not-finite": float("nan")}, TypeError),
        ({"too-large": "x" * (64 * 1024)}, ValueError),
    ],
)
def test_factory_config_is_json_compatible_and_bounded(
    config: dict[str, object], error: type[Exception]
) -> None:
    with pytest.raises(error):
        validate_factory_config(config)


@pytest.mark.parametrize(
    "value",
    [
        "relative",
        "/../private",
        "/a/%2e%2e/private",
        "/a//b",
        "/safe?secret=value",
        "/x#f",
        "/カタカナ",
    ],
)
def test_root_path_rejects_non_mount_paths(value: str) -> None:
    with pytest.raises(ValueError):
        validate_root_path(value)


def test_loopback_url_and_origin_normalization() -> None:
    assert validate_loopback_url("http://127.0.0.1:8080/mount/") == (
        "http://127.0.0.1:8080",
        "/mount",
    )
    assert validate_origin("HTTP://[::1]:80/") == "http://[::1]"
    with pytest.raises(ValueError):
        validate_loopback_url("https://example.test")
    with pytest.raises(ValueError):
        validate_origin("https://example.test/path")
    with pytest.raises(ValueError, match="literal loopback"):
        validate_origin("https://example.test")
    with pytest.raises(ValueError):
        validate_loopback_url("http://127.0.0.1:8080/a/%2e%2e/private")


def test_factory_reference_must_be_importable_attribute_syntax() -> None:
    assert validate_factory_ref("package.module:create_app") == ("package.module", "create_app")
    with pytest.raises(ValueError):
        validate_factory_ref("package.module:create-app")


def test_public_browser_scenario_import_has_no_optional_runner_imports() -> None:
    import subprocess
    import sys

    source = (
        "import sys; import hedron.testing.browser_scenario; "
        "assert not {'pytest', 'playwright', 'uvicorn'} & set(sys.modules)"
    )
    subprocess.run([sys.executable, "-c", source], check=True, capture_output=True, text=True)


def test_structured_failure_snapshot_omits_target_identifiers() -> None:
    from collections import deque
    from types import SimpleNamespace

    scenario = BrowserScenario.__new__(BrowserScenario)
    scenario._source = "managed"
    scenario._navigation_epoch = 1
    scenario._event_capacity = 16
    scenario._events = deque(
        [
            UIEvent(
                sequence=1,
                navigation_epoch=1,
                kind="request_start",
                target="private-user-canary",
            )
        ],
        maxlen=16,
    )
    scenario._categories = deque(maxlen=16)
    scenario._owner = SimpleNamespace(_capture_profile="structured")
    scenario._synthetic = False
    scenario._context = SimpleNamespace(browser=None)
    scenario._capabilities = {"observer": True}

    snapshot = scenario._safe_snapshot()

    assert snapshot["events"][0]["kind"] == "request_start"
    assert "private-user-canary" not in str(snapshot)
