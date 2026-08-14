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


def test_public_chart_docs_cover_runtime_boundaries() -> None:
    api = (ROOT / "docs/api/CHART.md").read_text(encoding="utf-8")
    package = (ROOT / "docs/packages/hedron-charts.md").read_text(encoding="utf-8")
    guide = (ROOT / "docs/guides/charts-and-htmx.md").read_text(encoding="utf-8")

    assert "Compiler contract versus current host coverage" in api
    assert "Bounds and enforcement" in api
    assert "Grammar coverage versus paint coverage" in package
    assert "Replace a real chart with HTMX" in guide
    assert "authorized=user_can_export" in api
    assert "authorized=user_can_export" in package
    assert "authorized=user_can_export" in guide


def test_advanced_chart_has_component_page() -> None:
    text = (ROOT / "docs/components/chart.md").read_text(encoding="utf-8")
    assert "from hedron_charts import Chart" in text
    assert "ChartSpec" in text
    assert "progressively enhances" in text


def test_maintainer_chart_contract_points_to_observed_coverage() -> None:
    catalog = (ROOT / "docs/implementation/CHART_SPEC.md").read_text(encoding="utf-8")
    plan = (ROOT / "docs/implementation/HEDRON_CHARTS_038.md").read_text(encoding="utf-8")

    assert "Planning-only" not in catalog
    assert "runtime coverage matrix" in catalog
    assert "Historical implementation plan" in plan
    assert "runtime coverage matrix" in plan
