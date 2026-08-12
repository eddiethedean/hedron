"""RUNNER-029: pre-bind, env export before import, fake rserver-url."""

from __future__ import annotations

import os
import stat
from dataclasses import replace
from pathlib import Path

import pytest

from hedron_core.diagnostics import HedronError
from hedron_workbench.config import WorkbenchConfig
from hedron_workbench.middleware import WorkbenchPathMiddleware
from hedron_workbench.resolve import RESOLVED_MODE_ENV, RESOLVED_MOUNT_ENV, resolve_deployment
from hedron_workbench.runner import (
    HEDRON_PUBLIC_BASE,
    bind_loopback,
    discover_rserver_url,
    export_hedron_state,
    load_app,
    prepare_app,
    serve,
)


def test_bind_port_zero() -> None:
    sock = bind_loopback("127.0.0.1", 0)
    try:
        port = int(sock.getsockname()[1])
        assert port > 0
    finally:
        sock.close()


def test_discover_requires_absolute_binary() -> None:
    with pytest.raises(HedronError) as exc:
        discover_rserver_url(binary="rserver-url", port=8000)
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
