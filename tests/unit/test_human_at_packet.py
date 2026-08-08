"""Unit tests for scripts/check_human_at_packet.py (0.21 engineering)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_human_at_packet.py"


def test_human_at_packet_passes_without_sessions() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "ok: human AT" in proc.stdout


def test_human_at_protocol_gate_passes() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--gate", "PROTOCOL-021"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr


def test_human_at_sr_gate_without_sessions_passes() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--gate", "SR-021"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr


def test_human_at_packet_require_sessions_fails_on_placeholder_only() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--require-sessions"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "placeholder" in proc.stderr.lower() or "non-placeholder" in proc.stderr.lower()


def test_human_at_sr_require_sessions_fails() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--gate", "SR-021", "--require-sessions"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
