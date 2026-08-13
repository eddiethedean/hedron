"""REALWB checker behavior (skip on unavailable license)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import check_realwb_smoke as smoke  # noqa: E402


def test_live_skip_on_unavailable_license_exit_code(monkeypatch) -> None:
    def fake_check_call(cmd, *, cwd):  # type: ignore[no-untyped-def]
        assert cmd == ["bash", str(ROOT / "scripts" / "realwb_smoke.sh")]
        raise subprocess.CalledProcessError(smoke.SKIP_EXIT_CODE, cmd)

    monkeypatch.setattr(subprocess, "check_call", fake_check_call)
    assert smoke.main(["--live"]) == 0


def test_offline_result_log_includes_both_packages() -> None:
    text = smoke.RESULT.read_text(encoding="utf-8")
    assert smoke._validate_log(text) == []


def test_offline_floor_result_log_includes_three_packages() -> None:
    text = smoke.RESULT_FLOOR.read_text(encoding="utf-8")
    assert smoke._validate_floor_log(text) == []
