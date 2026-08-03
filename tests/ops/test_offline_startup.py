"""Offline startup / manifest evidence."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_lockfile_and_license_present() -> None:
    assert (ROOT / "uv.lock").is_file()
    assert (ROOT / "LICENSE").is_file()
