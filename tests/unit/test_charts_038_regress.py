"""REGRESS-038 umbrella for phase 0.38 chart packet."""

from __future__ import annotations

from pathlib import Path

from hedron_charts import __version__
from hedron_charts.compile import CANVAS_MARK_THRESHOLD

ROOT = Path(__file__).resolve().parents[2]


def test_regress_medium_issue_hosts_and_limits() -> None:
    plotly = (ROOT / "packages/hedron-charts/src/hedron_charts/assets/plotly/host.js").read_text(
        encoding="utf-8"
    )
    mermaid = (ROOT / "packages/hedron-charts/src/hedron_charts/assets/mermaid/host.js").read_text(
        encoding="utf-8"
    )
    adapters = (ROOT / "packages/hedron-charts/src/hedron_charts/adapters.py").read_text(
        encoding="utf-8"
    )
    assert "Plotly.purge" in plotly
    assert "_hedronMermaidGen" in mermaid
    assert "cleaned[:50]" not in adapters
    assert CANVAS_MARK_THRESHOLD == 2500


def test_package_version_string_present() -> None:
    assert __version__
