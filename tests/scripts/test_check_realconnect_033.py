"""REALCONNECT-033 checker behavior (skip on unavailable license)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import check_realconnect_033 as smoke  # noqa: E402


def test_live_skip_on_unavailable_license_exit_code(monkeypatch) -> None:
    def fake_check_call(cmd, *, cwd):  # type: ignore[no-untyped-def]
        assert cmd == ["bash", str(ROOT / "scripts" / "realconnect_033_probe.sh")]
        raise subprocess.CalledProcessError(smoke.SKIP_EXIT_CODE, cmd)

    monkeypatch.setattr(subprocess, "check_call", fake_check_call)
    assert smoke.main(["--live"]) == 0


def test_offline_result_log_includes_native_cookie_markers() -> None:
    text = smoke.RESULT.read_text(encoding="utf-8")
    assert smoke._validate_log(text) == []
