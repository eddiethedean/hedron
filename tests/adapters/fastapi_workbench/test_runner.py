"""fastapi-workbench launcher discovery guard (issue #144)."""

from __future__ import annotations

import os
from urllib.parse import quote

import pytest
from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse
from fastapi.testclient import TestClient

from fastapi_workbench.config import ResolvedDeployment, WorkbenchConfig, WorkbenchMode
from fastapi_workbench.middleware import WorkbenchPathMiddleware, workbenchify
from fastapi_workbench.resolve import (
    RESOLVED_MODE_ENV,
    RESOLVED_MOUNT_ENV,
    RESOLVED_PUBLIC_BASE_ENV,
    explicit_mount_hint,
    resolve_deployment,
)
from fastapi_workbench.runner import prepare_app, run_target


class _NullApp:
    async def __call__(self, scope: object, receive: object, send: object) -> None:
        return None


def test_prepare_app_updates_existing_wrapper_for_path_only_discovery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wrapped = workbenchify(_NullApp(), mode=WorkbenchMode.ON)
    assert isinstance(wrapped, WorkbenchPathMiddleware)
    monkeypatch.setattr("fastapi_workbench.runner.load_app", lambda *_args, **_kwargs: wrapped)

    prepared, resolved = prepare_app(
        target="sample:app",
        config=WorkbenchConfig(mode=WorkbenchMode.ON),
        environ={},
        bound_port=8000,
        discovered_raw="/s/session/p/proxy-token",
        apply_environ=False,
    )

    assert prepared is wrapped
    assert resolved.source == "rserver-url:path"
    assert wrapped.relative_redirects is True


def test_prepare_app_reconfigures_a_pre_wrapped_production_app(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Launcher discovery must reach wrappers created during application import."""
    mount = "/s/production-session/p/8123"
    inner = FastAPI()

    @inner.get("/health")
    def health(response: Response) -> dict[str, bool]:
        response.set_cookie("session", "opaque", path="/")
        return {"ok": True}

    @inner.get("/go")
    def go() -> RedirectResponse:
        return RedirectResponse("/health", status_code=303)

    # This is a documented application pattern: wrapping at import time before
    # the launcher has bound a port and discovered the Workbench session URL.
    wrapped = workbenchify(inner)
    assert isinstance(wrapped, WorkbenchPathMiddleware)
    monkeypatch.setattr("fastapi_workbench.runner.load_app", lambda *_args, **_kwargs: wrapped)

    prepared, _ = prepare_app(
        target="sample:app",
        config=WorkbenchConfig(
            mode=WorkbenchMode.ON,
            mount=mount,
            public_base_url=f"https://workbench.example{mount}",
        ),
        apply_environ=False,
        owned_cookie_names=("session",),
    )

    assert prepared is wrapped
    assert wrapped.mode is WorkbenchMode.ON
    assert wrapped.expected_mount == mount
    assert wrapped.expected_origins == frozenset({"https://workbench.example"})
    assert wrapped.owned_cookie_names == frozenset({"session"})

    client = TestClient(prepared)
    response = client.get(f"{mount}/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert f"Path={mount}" in response.headers["set-cookie"]

    redirect = client.get(f"{mount}/go", follow_redirects=False)
    assert redirect.status_code == 303
    assert redirect.headers["location"] == f"{mount}/health"


def test_prepare_app_hands_discovered_origin_to_a_pre_wrapped_app(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inner = FastAPI()
    wrapped = workbenchify(inner)
    assert isinstance(wrapped, WorkbenchPathMiddleware)
    monkeypatch.setattr("fastapi_workbench.runner.load_app", lambda *_args, **_kwargs: wrapped)

    prepared, _ = prepare_app(
        target="sample:app",
        config=WorkbenchConfig(mode=WorkbenchMode.ON),
        bound_port=8124,
        discovered_raw="https://workbench.example/s/discovered/p/8124/",
        apply_environ=False,
    )

    assert prepared is wrapped
    encoded = "/" + quote(
        "https://workbench.example/s/discovered/p/8124/health",
        safe="",
    )
    normalized = wrapped.normalize_scope(
        {
            "type": "http",
            "path": encoded,
            "raw_path": encoded.encode(),
            "root_path": "",
            "query_string": b"",
        }
    )
    assert normalized["path"] == "/s/discovered/p/8124/health"
    assert normalized["root_path"] == "/s/discovered/p/8124"


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


def test_run_target_explicitly_discovers_without_rs_server_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    discovery_calls: list[int] = []

    def discover(**kwargs: object) -> str:
        discovery_calls.append(int(kwargs["port"]))
        return "https://wb.example/s/session/p/8765/"

    class FakeSock:
        def getsockname(self) -> tuple[str, int]:
            return ("127.0.0.1", 8765)

        def close(self) -> None:
            return None

    monkeypatch.setattr("fastapi_workbench.runner.discover_rserver_url", discover)
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
    served: list[ResolvedDeployment] = []
    monkeypatch.setattr(
        "fastapi_workbench.runner.serve",
        lambda _app, resolved, sock=None: served.append(resolved),
    )

    run_target(
        "tests.integration._workbench_sample:app",
        config=WorkbenchConfig(),
        environ={},
        discover=True,
    )

    assert discovery_calls == [8765]
    assert len(served) == 1
    assert served[0].browser_mount == "/s/session/p/8765"
    assert served[0].discovered is True
