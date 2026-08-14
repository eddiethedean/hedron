"""DOCS-038 packet + guide presence."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_docs_038_artifacts_exist() -> None:
    required = [
        "docs/implementation/HEDRON_CHARTS_038.md",
        "docs/implementation/CHART_SPEC.md",
        "docs/rfcs/RFC-0069-HIGH-FIDELITY-CHARTS.md",
        "docs/acceptance/RELEASE_0_38.md",
        "docs/acceptance/upgrade-fixtures-038.md",
        "docs/acceptance/baselines-038.toml",
        "docs/guides/whats-new-0.38.md",
        "docs/packages/hedron-charts.md",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), rel


def test_whats_new_mentions_chartspec() -> None:
    text = (ROOT / "docs/guides/whats-new-0.38.md").read_text(encoding="utf-8")
    assert "ChartSpec" in text
    assert "hedron-chart" in text
