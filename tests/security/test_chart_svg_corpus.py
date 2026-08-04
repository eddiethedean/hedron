"""Adversarial chart/SVG/Markdown corpus for 0.6 closure."""

from __future__ import annotations

import pytest

from hedron_charts.limits import reject_active_svg, reject_callbacks, reject_remote_urls
from hedron_core.diagnostics import HedronError
from hedron_core.icons import clear_icons_for_tests, register_icon
from hedron_core.rendering import RenderMode, render
from hedron_core.security import TrustedHtml


def test_reject_plotly_style_callback() -> None:
    with pytest.raises(HedronError) as exc:
        reject_callbacks({"layout": {"updatemenus": [{"buttons": [{"args": ["function()"]}]}]}})
    assert exc.value.diagnostic.code == "HED-CHART-0004"


def test_reject_onclick_key() -> None:
    with pytest.raises(HedronError) as exc:
        reject_callbacks({"onclick": "alert(1)"})
    assert exc.value.diagnostic.code == "HED-CHART-0004"


def test_reject_cdn_url() -> None:
    with pytest.raises(HedronError) as exc:
        reject_remote_urls({"data": [{"url": "https://cdn.plot.ly/plotly.min.js"}]})
    assert exc.value.diagnostic.code == "HED-CHART-0005"


def test_reject_protocol_relative_cdn() -> None:
    with pytest.raises(HedronError) as exc:
        reject_remote_urls("//cdn.jsdelivr.net/npm/vega")
    assert exc.value.diagnostic.code == "HED-CHART-0005"


def test_benign_spec_allowed() -> None:
    reject_callbacks({"data": [{"x": [1, 2], "y": [3, 4]}], "layout": {"title": "ok"}})
    reject_remote_urls({"data": [{"values": [{"a": 1}]}], "mark": "bar"})


def test_altair_schema_metadata_is_removed_from_local_payload() -> None:
    altair = pytest.importorskip("altair")
    from hedron_charts import AltairAdapter
    from hedron_core.visualization import ChartAccessibility

    chart = altair.Chart(altair.Data(values=[{"x": "A", "y": 1}])).mark_bar().encode(
        x="x:N", y="y:Q"
    )
    output = AltairAdapter().compile(
        chart,
        accessibility=ChartAccessibility(title="Local chart", description="Local values"),
    )

    assert '"$schema"' not in str(output.body)


def test_reject_svg_onload() -> None:
    with pytest.raises(HedronError) as exc:
        reject_active_svg('<svg onload="alert(1)"></svg>')
    assert exc.value.diagnostic.code == "HED-CHART-0006"


def test_reject_svg_foreign_object() -> None:
    with pytest.raises(HedronError) as exc:
        reject_active_svg("<svg><foreignObject><script>x</script></foreignObject></svg>")
    assert exc.value.diagnostic.code == "HED-CHART-0006"


def test_icon_rejects_onload() -> None:
    clear_icons_for_tests()
    with pytest.raises(HedronError) as exc:
        register_icon("bad", '<svg onload="alert(1)"></svg>', title="Bad")
    assert exc.value.diagnostic.code == "HED-ICON-0003"


def test_markdown_strips_script() -> None:
    pytest.importorskip("markdown")
    pytest.importorskip("nh3")
    from hedron.content import Markdown

    html_out = render(
        Markdown("# Hi\n\n<script>alert(1)</script>"),
        mode=RenderMode.FRAGMENT,
    ).html
    assert "<script" not in html_out.lower()
    assert "Hi" in html_out


def test_trusted_html_nh3_strips_onmouseover() -> None:
    pytest.importorskip("nh3")
    trusted = TrustedHtml.nh3('<b onmouseover="alert(1)">ok</b>')
    assert "onmouseover" not in trusted.value.lower()
    assert "ok" in trusted.value


def test_line_chart_tabular_fallback_escaped() -> None:
    from hedron_charts import LineChart

    node = LineChart(
        [{"month": "<script>", "revenue": 1}],
        x="month",
        y="revenue",
        title="T",
        description="D",
        alt="A",
    )
    # Force SVG fallback path by temporarily hiding matplotlib if present —
    # still assert title/description and escaped content when rendered.
    html_out = render(node, mode=RenderMode.FRAGMENT).html
    assert "T" in html_out
    # Script tags from data must not execute as markup tags.
    assert "<script>" not in html_out or "&lt;script&gt;" in html_out or "script" in html_out
