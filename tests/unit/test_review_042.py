"""REVIEW-042: independent security review packet integrity."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "docs" / "acceptance" / "security-review-042"


def test_review_042_brief_present() -> None:
    brief = (REVIEW / "BRIEF.md").read_text(encoding="utf-8")
    assert "0.42" in brief
    assert "CSP" in brief or "Trusted Types" in brief


def test_review_042_cut_artifacts_when_present() -> None:
    report = REVIEW / "REDACTED_REPORT.md"
    disposition = REVIEW / "DISPOSITION.toml"
    if not report.is_file() or not disposition.is_file():
        # Stage 0 / pre-cut: BRIEF only.
        assert "Stage 0 brief only" in (REVIEW / "BRIEF.md").read_text(encoding="utf-8")
        return
    text = report.read_text(encoding="utf-8")
    assert "critical" in text.lower()
    data = tomllib.loads(disposition.read_text(encoding="utf-8"))
    assert data["gate"] == "REVIEW-042"
    assert data["state"] == "verified"
    assert int(data.get("critical_open", 1)) == 0
    assert int(data.get("high_open", 1)) == 0
