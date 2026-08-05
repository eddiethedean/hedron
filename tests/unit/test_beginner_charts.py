from hedron.testing import render_html
from hedron_charts import AreaChart, BarChart, ScatterChart


def test_beginner_charts_render() -> None:
    data = [{"x": "a", "y": 1}, {"x": "b", "y": 2}]
    for cls in (AreaChart, BarChart, ScatterChart):
        html = render_html(cls(data, x="x", y="y", title="T", description="D"))
        assert "T" in html
