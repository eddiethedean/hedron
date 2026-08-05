from hedron.testing import render_html
from hedron_charts import AreaChart, BarChart, ScatterChart


def test_beginner_charts_render() -> None:
    categorical = [{"x": "a", "y": 1}, {"x": "b", "y": 2}]
    for cls in (AreaChart, BarChart, ScatterChart):
        html = render_html(cls(categorical, x="x", y="y", title="T", description="D"))
        assert "T" in html
        assert 'role="img"' in html or "aria-label" in html or "hedron-chart" in html


def test_scatter_uses_numeric_x() -> None:
    data = [{"x": 10, "y": 1}, {"x": 20, "y": 2}, {"x": 30, "y": 4}]
    html = render_html(ScatterChart(data, x="x", y="y", title="Scatter", description="numeric"))
    assert "Scatter" in html
    # SVG fallback or matplotlib path should not label x as 0..n categories only.
    assert "hedron-chart" in html
