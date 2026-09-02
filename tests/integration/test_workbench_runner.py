"""RUNNER-029: pre-bind, env export before import, fake rserver-url."""

from __future__ import annotations

import os
import signal
import socket
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import replace
from pathlib import Path

import pytest

from hedron_core.diagnostics import HedronError
from hedron_posit.config import WorkbenchConfig
from hedron_posit.detect import RESOLVED_ACTIVE_ENV
from hedron_posit.middleware import WorkbenchPathMiddleware
from hedron_posit.products import PositProduct
from hedron_posit.resolve import RESOLVED_MODE_ENV, RESOLVED_MOUNT_ENV, resolve_deployment
from hedron_posit.runner import (
    HEDRON_PUBLIC_BASE,
    bind_loopback,
    discover_rserver_url,
    export_hedron_state,
    load_app,
    prepare_app,
    run_target,
    serve,
    supervised_uvicorn_command,
)

ROOT = Path(__file__).resolve().parents[2]


def test_bind_port_zero() -> None:
    sock = bind_loopback("127.0.0.1", 0)
    try:
        port = int(sock.getsockname()[1])
        assert port > 0
    finally:
        sock.close()


def test_bind_explicit_port() -> None:
    probe = bind_loopback("127.0.0.1", 0)
    port = int(probe.getsockname()[1])
    probe.close()
    sock = bind_loopback("127.0.0.1", port)
    try:
        assert int(sock.getsockname()[1]) == port
    finally:
        sock.close()


def test_bind_failure_is_diagnostic() -> None:
    with pytest.raises(HedronError) as exc:
        bind_loopback("256.256.256.256", 8050)
    assert "HED-WB-0004" in str(exc.value)


def test_discover_requires_absolute_binary() -> None:
    with pytest.raises(HedronError) as exc:
        discover_rserver_url(binary="rserver-url", port=8000)
    assert "HED-WB-0003" in str(exc.value)


def test_discover_missing_binary() -> None:
    with pytest.raises(HedronError) as exc:
        discover_rserver_url(binary="/no/such/hedron-rserver-url", port=8000)
    assert "HED-WB-0003" in str(exc.value)


def test_discover_fake_binary(tmp_path: Path) -> None:
    script = tmp_path / "rserver-url"
    script.write_text("#!/bin/sh\necho https://wb.example/s/abc/p/$2/\n", encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    raw = discover_rserver_url(binary=str(script), port=8050)
    assert raw.startswith("https://wb.example/s/abc/p/")


def test_discover_bounds_stdout(tmp_path: Path) -> None:
    script = tmp_path / "rserver-url-large"
    script.write_text("#!/bin/sh\npython3 -c 'print(\"x\" * 10000)'\n", encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    with pytest.raises(HedronError) as exc:
        discover_rserver_url(binary=str(script), port=8050)
    assert "HED-WB-0002" in str(exc.value)


def test_discover_redacts_stderr(tmp_path: Path) -> None:
    script = tmp_path / "rserver-url-fail"
    script.write_text("#!/bin/sh\necho 'token=supersecret' >&2\nexit 2\n", encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    with pytest.raises(HedronError) as exc:
        discover_rserver_url(binary=str(script), port=8050)
    assert "supersecret" not in str(exc.value)


def test_discover_rejects_invalid_utf8(tmp_path: Path) -> None:
    script = tmp_path / "rserver-url-invalid-utf8"
    script.write_bytes(b"#!/bin/sh\nprintf '\\377'\n")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    with pytest.raises(HedronError, match="valid UTF-8"):
        discover_rserver_url(binary=str(script), port=8050)


def test_export_sets_hedron_root_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HEDRON_ROOT_PATH", raising=False)
    monkeypatch.delenv("HEDRON_WORKBENCH_RESOLVED_PUBLIC_BASE", raising=False)
    resolved = resolve_deployment(
        WorkbenchConfig(mount="/s/abc/p/1"),
        environ={},
    )
    export_hedron_state(resolved)
    assert os.environ["HEDRON_ROOT_PATH"] == "/s/abc/p/1"
    assert os.environ[RESOLVED_MOUNT_ENV] == "/s/abc/p/1"
    assert os.environ[RESOLVED_MODE_ENV] == "auto"
    assert os.environ[HEDRON_PUBLIC_BASE]
    assert os.environ["HEDRON_TRUSTED_PROXIES"] == resolved.forwarded_allow_ips


def test_export_clears_stale_handoff_for_inactive_app() -> None:
    env = {
        "HEDRON_ROOT_PATH": "/stale",
        RESOLVED_MOUNT_ENV: "/stale",
        RESOLVED_ACTIVE_ENV: "1",
        HEDRON_PUBLIC_BASE: "https://stale.example",
        "HEDRON_TRUSTED_PROXIES": "10.0.0.1",
    }
    resolved = resolve_deployment(WorkbenchConfig(), environ={})
    export_hedron_state(resolved, environ=env)
    assert "HEDRON_ROOT_PATH" not in env
    assert RESOLVED_MOUNT_ENV not in env
    assert RESOLVED_ACTIVE_ENV not in env
    assert HEDRON_PUBLIC_BASE not in env
    assert env["HEDRON_TRUSTED_PROXIES"] == resolved.forwarded_allow_ips


def test_prepare_app_exports_before_import(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HEDRON_ROOT_PATH", raising=False)
    wrapped, resolved = prepare_app(
        target="tests.integration._workbench_sample:create_app",
        config=WorkbenchConfig(mount="/s/prep/p/2", factory=True),
        wrap=True,
    )
    assert resolved.browser_mount == "/s/prep/p/2"
    inner = wrapped.app
    assert inner.state.hedron_mount_path == "/s/prep/p/2"
    assert inner.state.hedron_cookie_path == "/s/prep/p/2"


def test_prepare_app_exports_into_caller_environ(monkeypatch: pytest.MonkeyPatch) -> None:
    """#136: custom environ must receive handoff keys; os.environ must stay clean."""
    monkeypatch.delenv("HEDRON_ROOT_PATH", raising=False)
    monkeypatch.delenv(RESOLVED_MOUNT_ENV, raising=False)
    isolated: dict[str, str] = {}
    _app, resolved = prepare_app(
        target="tests.integration._workbench_sample:create_app",
        config=WorkbenchConfig(mount="/s/isolated/p/1", factory=True),
        environ=isolated,
        wrap=False,
    )
    assert resolved.browser_mount == "/s/isolated/p/1"
    assert isolated.get("HEDRON_ROOT_PATH") == "/s/isolated/p/1"
    assert isolated.get(RESOLVED_MOUNT_ENV) == "/s/isolated/p/1"
    assert os.environ.get("HEDRON_ROOT_PATH") != "/s/isolated/p/1"
    assert RESOLVED_MOUNT_ENV not in os.environ or os.environ.get(RESOLVED_MOUNT_ENV) != (
        "/s/isolated/p/1"
    )


def test_run_target_exports_process_environ_before_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """REALWB-030: CLI run (environ=None) must hand off mount via os.environ."""
    monkeypatch.delenv("HEDRON_ROOT_PATH", raising=False)
    monkeypatch.delenv(RESOLVED_MOUNT_ENV, raising=False)

    class FakeSock:
        def getsockname(self) -> tuple[str, int]:
            return ("127.0.0.1", 18050)

        def close(self) -> None:
            return None

    served: list[object] = []

    monkeypatch.setattr("hedron_posit.runner.bind_loopback", lambda _h, _p: FakeSock())
    monkeypatch.setattr(
        "hedron_posit.runner.serve",
        lambda app, resolved, sock=None: served.append((app, resolved)),
    )

    run_target(
        "tests.integration._workbench_sample:create_workbench_app",
        config=WorkbenchConfig(mount="/s/cli/p/8050", factory=True),
    )

    assert os.environ.get("HEDRON_ROOT_PATH") == "/s/cli/p/8050"
    assert len(served) == 1
    app, resolved = served[0]
    assert resolved.browser_mount == "/s/cli/p/8050"
    assert app.hedron_workbench.active is True
    assert app.state.hedron_mount_path == "/s/cli/p/8050"


def test_run_target_discovery_activates_hedron_posit_without_rserver_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """#881: validated discovery must identify Workbench before app construction."""
    for name in (
        "RS_SERVER_URL",
        "HEDRON_POSIT_PRODUCT",
        "HEDRON_WORKBENCH",
        "FASTAPI_WORKBENCH",
        RESOLVED_ACTIVE_ENV,
        RESOLVED_MOUNT_ENV,
    ):
        monkeypatch.delenv(name, raising=False)

    class FakeSock:
        def getsockname(self) -> tuple[str, int]:
            return ("127.0.0.1", 8765)

        def close(self) -> None:
            return None

    served: list[object] = []
    monkeypatch.setattr("hedron_posit.runner.bind_loopback", lambda _h, _p: FakeSock())
    monkeypatch.setattr(
        "hedron_posit.runner.discover_rserver_url",
        lambda *, binary, port: f"https://wb.example/s/session/p/{port}",
    )
    monkeypatch.setattr(
        "hedron_posit.runner.serve",
        lambda app, resolved, sock=None: served.append((app, resolved)),
    )

    run_target(
        "tests.integration._workbench_sample:create_workbench_app",
        config=WorkbenchConfig(factory=True),
        discover=True,
    )

    assert len(served) == 1
    app, resolved = served[0]
    assert resolved.browser_mount == "/s/session/p/8765"
    assert app.hedron_posit.product is PositProduct.WORKBENCH
    assert app.hedron_posit.evidence == "workbench_handoff"
    assert app.hedron_workbench.active is True
    assert app.state.hedron_cookie_path == "/s/session/p/8765"


def test_prepare_workbench_facade_is_not_double_wrapped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("HEDRON_ROOT_PATH", raising=False)
    app, resolved = prepare_app(
        target="tests.integration._workbench_sample:create_workbench_app",
        config=WorkbenchConfig(mount="/s/facade/p/4", factory=True),
    )
    assert not isinstance(app, WorkbenchPathMiddleware)
    assert app.state.hedron_mount_path == "/s/facade/p/4"
    assert app.hedron_workbench.browser_mount == resolved.browser_mount
    assert app.workbench_status()["normalizer_count"] == 1


def test_load_app_object() -> None:
    from tests.integration import _workbench_sample

    app = load_app("tests.integration._workbench_sample:app")
    assert app is _workbench_sample.app


def test_load_app_resolves_module_from_current_working_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module_name = "_local_workbench_app"
    (tmp_path / f"{module_name}.py").write_text("app = 'local-app'\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "path",
        [entry for entry in sys.path if entry not in {"", str(tmp_path)}],
    )
    sys.modules.pop(module_name, None)
    try:
        assert load_app(f"{module_name}:app") == "local-app"
    finally:
        sys.modules.pop(module_name, None)


def test_missing_module() -> None:
    with pytest.raises(HedronError) as exc:
        load_app("no.such.module:app")
    assert "HED-WB-0005" in str(exc.value)


def test_runner_rejects_reload_and_multi_worker() -> None:
    resolved = resolve_deployment(WorkbenchConfig(), environ={})
    with pytest.raises(HedronError) as reload_exc:
        serve(object(), replace(resolved, reload=True))
    assert "HED-WB-0009" in str(reload_exc.value)
    with pytest.raises(HedronError) as workers_exc:
        serve(object(), replace(resolved, workers=2))
    assert "HED-WB-0009" in str(workers_exc.value)


def test_supervised_command_reuses_bound_fd_for_reload_or_workers() -> None:
    resolved = resolve_deployment(WorkbenchConfig(reload=True), environ={})
    reload_command = supervised_uvicorn_command(resolved, fd=17)
    assert reload_command[:3] == [os.sys.executable, "-m", "uvicorn"]
    assert reload_command[reload_command.index("--fd") + 1] == "17"
    assert "--reload" in reload_command

    workers = replace(resolved, reload=False, workers=3)
    worker_command = supervised_uvicorn_command(workers, fd=18)
    assert worker_command[worker_command.index("--workers") + 1] == "3"


def test_open_browser_uses_docs_url(monkeypatch: pytest.MonkeyPatch) -> None:
    import uvicorn

    opened: list[str] = []
    monkeypatch.setattr("hedron_posit._workbench.runner.webbrowser.open", opened.append)
    monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: None)
    resolved = resolve_deployment(
        WorkbenchConfig(mount="/s/demo/p/9", open_browser=True, port=8050),
        environ={},
    )
    serve(object(), replace(resolved, open_browser=True, browser_mount="/s/demo/p/9"))
    assert opened == ["http://127.0.0.1:8050/s/demo/p/9/docs"]


def test_run_target_shuts_down_on_sigterm() -> None:
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.bind(("127.0.0.1", 0))
    port = int(probe.getsockname()[1])
    probe.close()
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "hedron_posit.cli",
            "run",
            "tests.integration._workbench_sample:app",
            "--mode",
            "off",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                stderr = (proc.stderr.read() if proc.stderr else b"").decode("utf-8", "replace")
                raise AssertionError(f"launcher exited {proc.returncode}: {stderr}")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=0.5) as response:
                    assert response.status == 200
                break
            except (TimeoutError, urllib.error.URLError, ConnectionError, OSError):
                time.sleep(0.1)
        else:
            raise AssertionError("launcher did not become reachable")
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=15)
        assert proc.returncode in {0, -signal.SIGTERM}
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)
