"""Dependency audit must inspect the repository lock export, not host packages."""

from __future__ import annotations

import sys
from pathlib import Path
from subprocess import CompletedProcess

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import dep_audit  # noqa: E402


def test_audit_uses_exported_requirements(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        if "export" in args:
            return CompletedProcess(args, 0, "", "")
        return CompletedProcess(args, 0, '{"dependencies": []}', "")

    monkeypatch.setattr(dep_audit.shutil, "which", lambda _: "/usr/local/bin/uv")
    monkeypatch.setattr(dep_audit.subprocess, "run", fake_run)

    result = dep_audit._run_pip_audit()

    assert result.returncode == 0
    assert len(calls) == 2
    audit_call = calls[1]
    assert "--requirement" in audit_call
    assert "--no-deps" in audit_call
    assert "--disable-pip" in audit_call
    assert audit_call[audit_call.index("--requirement") + 1].endswith("requirements.txt")
