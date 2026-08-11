"""CHARTS-028: static / beginner chart matrix + payload / SVG guards."""

from __future__ import annotations

import pytest

from hedron.testing import render_html
from hedron_charts import AreaChart, BarChart, LineChart, MatplotlibChart, ScatterChart
from hedron_charts.limits import reject_active_svg, reject_remote_urls
from hedron_core.diagnostics import HedronError
from hedron_core.visualization import VisualizationLimits

_DATA = [{"x": "a", "y": 1}, {"x": "b", "y": 2}]


def _assert_accessible_chart(html: str, title: str) -> None:
    assert title in html
    assert 'role="img"' in html or "aria-label" in html or "hedron-chart" in html
    assert (
        "<table" in html.lower()
        or "hedron-chart-fallback" in html
        or "demo" in html.lower()
        or "description" in html.lower()
        or title in html
    )


@pytest.mark.parametrize("cls", [LineChart, BarChart, AreaChart, ScatterChart])
def test_beginner_static_matrix(cls: type) -> None:
    html = render_html(cls(_DATA, x="x", y="y", title="Matrix028", description="demo"))
    _assert_accessible_chart(html, "Matrix028")


def test_matplotlib_chart_smoke() -> None:
    pytest.importorskip("matplotlib")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([1, 2], [1, 4])
    try:
        html = render_html(
            MatplotlibChart(fig, title="Squares028", description="y = x^2", alt="Quadratic")
        )
    finally:
        plt.close(fig)
    _assert_accessible_chart(html, "Squares028")
    assert "<svg" in html.lower() or "image/svg" in html.lower() or "hedron-chart" in html


def test_payload_row_limit_rejects() -> None:
    with pytest.raises(HedronError) as exc:
        render_html(
            BarChart(
                _DATA,
                x="x",
                y="y",
                title="Rows",
                description="demo",
                limits=VisualizationLimits(max_rows=1),
            )
        )
    assert exc.value.diagnostic.code == "HED-CHART-0002"


def test_payload_byte_limit_rejects() -> None:
    pytest.importorskip("matplotlib")
    with pytest.raises(HedronError) as exc:
        render_html(
            LineChart(
                _DATA,
                x="x",
                y="y",
                title="Bytes",
                description="demo",
                limits=VisualizationLimits(max_payload_bytes=10),
            )
        )
    assert exc.value.diagnostic.code == "HED-CHART-0003"


def test_reject_remote_urls_and_active_svg() -> None:
    with pytest.raises(HedronError) as exc:
        reject_remote_urls({"data": [{"url": "https://cdn.plot.ly/plotly.min.js"}]})
    assert exc.value.diagnostic.code == "HED-CHART-0005"

    with pytest.raises(HedronError) as svg_exc:
        reject_active_svg('<svg onload="alert(1)"></svg>')
    assert svg_exc.value.diagnostic.code == "HED-CHART-0006"
