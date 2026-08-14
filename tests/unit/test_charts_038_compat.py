"""COMPAT-038 beginner + matplotlib compatibility."""

from __future__ import annotations

from hedron_charts import AreaChart, BarChart, LineChart, MatplotlibChart, ScatterChart
from hedron_charts.compile import beginner_to_spec, compile_chart
from hedron_core.rendering import render


def test_beginner_signatures_source_compatible() -> None:
    data = [{"x": 1, "y": 2}, {"x": 2, "y": 3}]
    for cls, kind in (
        (LineChart, "line"),
        (AreaChart, "area"),
        (BarChart, "bar"),
        (ScatterChart, "scatter"),
    ):
        node = cls(data, x="x", y="y", title="T", description="D")
        html = render(node).html
        assert "hedron-chart" in html
        spec = beginner_to_spec(kind=kind, data=data, x="x", y="y", title="T", description="D")
        plan = compile_chart(spec)
        assert plan.mark_count == 2


def test_matplotlib_chart_still_supported() -> None:
    import matplotlib

    matplotlib.use("Agg", force=False)
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, 4])
    html = render(MatplotlibChart(fig, title="M", description="matplotlib path")).html
    plt.close(fig)
    assert "hedron-chart" in html or "<svg" in html or "img" in html
