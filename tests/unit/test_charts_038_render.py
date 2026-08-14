"""RENDER-038 first-party element + host lifecycle remediations."""

from __future__ import annotations

from pathlib import Path

from hedron_charts import LineChart
from hedron_charts.assets_038 import chart_css_path, chart_module_path
from hedron_charts.element import TAG_NAME
from hedron_core.rendering import render

ROOT = Path(__file__).resolve().parents[2]


def test_linechart_renders_hedron_chart_element() -> None:
    html = render(
        LineChart([{"x": 1, "y": 2}, {"x": 2, "y": 4}], x="x", y="y", title="T", description="D")
    ).html
    assert f"<{TAG_NAME}" in html
    assert "data-hedron-payload=" in html
    assert "data-hedron-abi=" in html
    assert "hedron-chart-fallback" in html or "hedron-chart-summary" in html


def test_static_assets_present_and_within_budget() -> None:
    import gzip

    module = chart_module_path().read_bytes()
    css = chart_css_path().read_bytes()
    assert b"customElements.define" in module
    assert b"--hedron-chart-color-1" in css
    gz = gzip.compress(module)
    assert len(gz) <= 90 * 1024


def test_plotly_host_purges_stale_generation() -> None:
    host = (ROOT / "packages/hedron-charts/src/hedron_charts/assets/plotly/host.js").read_text(
        encoding="utf-8"
    )
    assert "Plotly.purge" in host
    assert "el._hedronPlotlyGen !== gen" in host


def test_mermaid_host_has_generation_guard() -> None:
    host = (ROOT / "packages/hedron-charts/src/hedron_charts/assets/mermaid/host.js").read_text(
        encoding="utf-8"
    )
    assert "_hedronMermaidGen" in host
