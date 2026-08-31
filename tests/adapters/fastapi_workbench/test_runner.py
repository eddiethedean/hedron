"""fastapi-workbench launcher discovery guard (issue #144)."""

from __future__ import annotations

import os

import pytest

from fastapi_workbench.config import ResolvedDeployment, WorkbenchConfig, WorkbenchMode
from fastapi_workbench.resolve import (
    RESOLVED_MODE_ENV,
    RESOLVED_MOUNT_ENV,
    RESOLVED_PUBLIC_BASE_ENV,
    explicit_mount_hint,
    resolve_deployment,
)
from fastapi_workbench.runner import run_target


def test_run_target_exports_process_environ_before_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """REALWB-030: the default os._Environ receives resolved launcher state."""
    for name in (RESOLVED_MODE_ENV, RESOLVED_MOUNT_ENV, RESOLVED_PUBLIC_BASE_ENV):
        monkeypatch.delenv(name, raising=False)

    class FakeSock:
        def getsockname(self) -> tuple[str, int]:
            return ("127.0.0.1", 18051)

        def close(self) -> None:
            return None

    served: list[ResolvedDeployment] = []

    def fake_bind(_host: str, _port: int) -> FakeSock:
        return FakeSock()

    def fake_serve(
        _app: object, resolved: ResolvedDeployment, *, sock: object | None = None
    ) -> None:
        del sock
        served.append(resolved)

    monkeypatch.setattr("fastapi_workbench.runner.bind_loopback", fake_bind)
    monkeypatch.setattr(
        "fastapi_workbench.runner.serve",
        fake_serve,
    )

    run_target(
        "tests.integration._workbench_sample:app",
        config=WorkbenchConfig(mode=WorkbenchMode.ON, mount="/s/cli/p/8051"),
    )

    assert os.environ[RESOLVED_MODE_ENV] == "on"
    assert os.environ[RESOLVED_MOUNT_ENV] == "/s/cli/p/8051"
    assert os.environ[RESOLVED_PUBLIC_BASE_ENV].endswith("/s/cli/p/8051")
    assert len(served) == 1


def test_explicit_mount_hint_includes_uvicorn_root_path_on_workbench() -> None:
    env = {
        "RS_SERVER_URL": "https://wb.example/",
        "UVICORN_ROOT_PATH": "/s/session/p/12345",
    }
    assert explicit_mount_hint(WorkbenchConfig(), env) == "/s/session/p/12345"


def test_explicit_mount_hint_extracts_uvicorn_root_path_from_full_url() -> None:
    env = {
        "RS_SERVER_URL": "https://wb.example/s/session/",
        "UVICORN_ROOT_PATH": "https://wb.example/s/session/p/8000/",
    }
    assert explicit_mount_hint(WorkbenchConfig(), env) == "/s/session/p/8000"


def test_explicit_mount_hint_includes_resolved_mount_env() -> None:
    env = {
        "RS_SERVER_URL": "https://wb.example/",
        "FASTAPI_WORKBENCH_RESOLVED_MOUNT": "/s/launcher/p/1",
    }
    assert explicit_mount_hint(WorkbenchConfig(), env) == "/s/launcher/p/1"


def test_explicit_mount_hint_ignores_uvicorn_root_path_without_rs_server_url() -> None:
    env = {"UVICORN_ROOT_PATH": "/generic"}
    assert explicit_mount_hint(WorkbenchConfig(), env) is None


def test_resolve_deployment_uses_uvicorn_root_path_without_discovery() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(),
        environ={
            "RS_SERVER_URL": "https://wb.example/",
            "UVICORN_ROOT_PATH": "/s/session/p/12345",
        },
    )
    assert resolved.browser_mount == "/s/session/p/12345"
    assert resolved.discovered is False


def test_run_target_skips_discovery_when_uvicorn_root_path_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    discover_calls: list[object] = []

    def boom(**kwargs: object) -> str:
        discover_calls.append(kwargs)
        raise AssertionError("discover_rserver_url should not be called")

    monkeypatch.setattr("fastapi_workbench.runner.discover_rserver_url", boom)

    class FakeSock:
        def getsockname(self) -> tuple[str, int]:
            return ("127.0.0.1", 12345)

        def close(self) -> None:
            return None

        def fileno(self) -> int:
            return 3

    monkeypatch.setattr("fastapi_workbench.runner.bind_loopback", lambda _h, _p: FakeSock())

    served: list[ResolvedDeployment] = []

    def fake_prepare_app(**kwargs: object) -> tuple[object, object]:
        resolved = resolve_deployment(
            kwargs["config"],  # type: ignore[arg-type]
            environ=kwargs["environ"],  # type: ignore[arg-type]
            bound_port=kwargs["bound_port"],  # type: ignore[arg-type]
            discovered_raw=kwargs["discovered_raw"],  # type: ignore[arg-type]
        )
        return object(), resolved

    monkeypatch.setattr("fastapi_workbench.runner.prepare_app", fake_prepare_app)
    monkeypatch.setattr(
        "fastapi_workbench.runner.serve",
        lambda _app, resolved, sock=None: served.append(resolved),
    )

    env = {
        "RS_SERVER_URL": "https://wb.example/",
        "UVICORN_ROOT_PATH": "/s/session/p/12345",
    }
    run_target(
        "tests.integration._workbench_sample:app",
        config=WorkbenchConfig(mode=WorkbenchMode.ON),
        environ=env,
    )

    assert discover_calls == []
    assert len(served) == 1
    assert served[0].browser_mount == "/s/session/p/12345"


def test_run_target_skips_discovery_when_resolved_mount_env_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    discover_calls: list[object] = []

    def boom(**kwargs: object) -> str:
        discover_calls.append(kwargs)
        raise AssertionError("discover_rserver_url should not be called")

    monkeypatch.setattr("fastapi_workbench.runner.discover_rserver_url", boom)

    class FakeSock:
        def getsockname(self) -> tuple[str, int]:
            return ("127.0.0.1", 54321)

        def close(self) -> None:
            return None

        def fileno(self) -> int:
            return 3

    env = {
        "RS_SERVER_URL": "https://wb.example/",
        RESOLVED_MOUNT_ENV: "/s/resolved/p/9",
    }

    monkeypatch.setattr("fastapi_workbench.runner.bind_loopback", lambda _h, _p: FakeSock())
    monkeypatch.setattr(
        "fastapi_workbench.runner.prepare_app",
        lambda **kwargs: (
            object(),
            resolve_deployment(
                kwargs["config"],  # type: ignore[arg-type]
                environ=kwargs["environ"],  # type: ignore[arg-type]
                bound_port=kwargs["bound_port"],  # type: ignore[arg-type]
                discovered_raw=kwargs["discovered_raw"],  # type: ignore[arg-type]
            ),
        ),
    )
    monkeypatch.setattr("fastapi_workbench.runner.serve", lambda *_a, **_k: None)

    run_target("tests.integration._workbench_sample:app", environ=env)

    assert discover_calls == []
