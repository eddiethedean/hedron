"""REVIEW-042: independent security review packet integrity."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "docs" / "acceptance" / "security-review-042"


def test_review_042_brief_present() -> None:
    brief = (REVIEW / "BRIEF.md").read_text(encoding="utf-8")
    assert "0.42" in brief
    assert "CSP" in brief
    assert "Trusted Types" in brief or "trusted types" in brief.lower()


def test_review_042_cut_artifacts_when_present() -> None:
    report = REVIEW / "REDACTED_REPORT.md"
    disposition = REVIEW / "DISPOSITION.toml"
    if not report.is_file() or not disposition.is_file():
        # Stage 0 / pre-cut: BRIEF only.
        assert "Stage 0 brief only" in (REVIEW / "BRIEF.md").read_text(encoding="utf-8")
        return
    text = report.read_text(encoding="utf-8")
    data = tomllib.loads(disposition.read_text(encoding="utf-8"))
    assert data["gate"] == "REVIEW-042"
    assert data["state"] == "verified"
    critical_open = int(data.get("critical_open", 1))
    high_open = int(data.get("high_open", 1))
    assert critical_open == 0
    assert high_open == 0
    # Report must independently state the open-count contract, not only TOML.
    assert "Critical open: **0**" in text or "critical open: 0" in text.lower()
    assert "High open: **0**" in text or "high open: 0" in text.lower()
    assert "CSP" in text or "Content-Security-Policy" in text
