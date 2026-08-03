"""Rollback documentation evidence."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_release_mentions_rollback_or_publish() -> None:
    text = (ROOT / "docs" / "RELEASE.md").read_text(encoding="utf-8").lower()
    assert "rollback" in text or "after publish" in text
