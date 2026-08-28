"""Regression coverage for Posit Workbench issues #747 and #748."""

from __future__ import annotations

import os

import pytest

from hedron_posit.config import WorkbenchConfig
from hedron_posit.resolve import resolve_deployment
from hedron_posit.runner import _exec_supervised


def test_full_uvicorn_root_path_preserves_workbench_origin() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(),
        environ={
            "RS_SERVER_URL": "http://127.0.0.1:8787/",
            "UVICORN_ROOT_PATH": "https://workbench.example/s/session/p/8000/",
        },
        bound_port=8000,
    )

    assert resolved.active is True
    assert resolved.browser_mount == "/s/session/p/8000"
    assert resolved.external_origin == "https://workbench.example"


def test_supervised_handoff_removes_uvicorn_root_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(reload=True),
        environ={
            "RS_SERVER_URL": "http://127.0.0.1:8787/",
            "UVICORN_ROOT_PATH": "https://workbench.example/s/session/p/8000/",
        },
        bound_port=8000,
    )
    monkeypatch.setenv(
        "UVICORN_ROOT_PATH",
        "https://workbench.example/s/session/p/8000/",
    )

    class _Socket:
        def fileno(self) -> int:
            return 17

        def set_inheritable(self, value: bool) -> None:
            assert value is True

    class _ExecCalled(Exception):
        pass

    def fake_execv(*args: object) -> None:
        raise _ExecCalled(args)

    monkeypatch.setattr("hedron_posit.runner.os.execv", fake_execv)
    with pytest.raises(_ExecCalled):
        _exec_supervised(
            resolved,
            sock=_Socket(),  # type: ignore[arg-type]
            target="tests.integration._workbench_sample:app",
            factory=False,
        )

    assert "UVICORN_ROOT_PATH" not in os.environ
    assert os.environ["HEDRON_ROOT_PATH"] == "/s/session/p/8000"
    assert os.environ["HEDRON_WORKBENCH_RESOLVED_PUBLIC_BASE"] == (
        "https://workbench.example/s/session/p/8000"
    )
