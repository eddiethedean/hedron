"""REALWB checker behavior (skip on unavailable license)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import check_realwb_029  # noqa: E402


def test_live_skip_on_unavailable_license_exit_code(monkeypatch) -> None:
    def fake_check_call(cmd, *, cwd):  # type: ignore[no-untyped-def]
        assert cmd == ["bash", str(ROOT / "scripts" / "realwb_029.sh")]
        raise subprocess.CalledProcessError(check_realwb_029.SKIP_EXIT_CODE, cmd)

    monkeypatch.setattr(subprocess, "check_call", fake_check_call)
    assert check_realwb_029.main(["--live"]) == 0
