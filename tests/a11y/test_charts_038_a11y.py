"""A11Y-038 automated checks (axe when browser enabled)."""

from __future__ import annotations

import os

import pytest
from tests.unit.charts_038_helpers import sample_plan

from hedron_charts import LineChart
from hedron_core.rendering import render

pytestmark = pytest.mark.a11y


def test_a11y_plan_has_required_text() -> None:
    plan = sample_plan()
    assert plan.accessibility.title
    assert plan.accessibility.description
    assert "Interactions:" in plan.accessibility.interaction_help


def test_ssr_includes_fallback_semantics() -> None:
    chart = LineChart(
        [{"x": "a", "y": 1}, {"x": "b", "y": 2}],
        x="x",
        y="y",
        title="Sales",
        description="Demo",
    )
    html = render(chart).html
    assert "Sales" in html
    assert "hedron-chart-summary" in html or "hedron-chart-fallback" in html


@pytest.mark.browser
def test_axe_hedron_chart_chromium() -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != "chromium":
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")
    pytest.importorskip("axe_playwright_python")

    from axe_playwright_python.sync_playwright import Axe
    from playwright.sync_api import sync_playwright

    from hedron_charts.assets_038 import chart_module_path

    html = render(
        LineChart([{"x": 1, "y": 2}, {"x": 2, "y": 3}], x="x", y="y", title="T", description="D")
    ).html
    module_js = chart_module_path().read_text(encoding="utf-8")
    page_html = (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<title>Hedron chart a11y fixture</title></head><body>"
        f"{html}"
        f"<script type='module'>\n{module_js}\n</script>"
        "</body></html>"
    )
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        # Inline the module: Chromium blocks file:// ES modules from set_content pages.
        page.set_content(page_html)
        page.wait_for_selector("hedron-chart[data-hedron-chart-mounted='1']", timeout=5000)
        results = Axe().run(page)
        serious = {"critical", "serious"}
        violations = [
            v for v in results.response.get("violations", []) if v.get("impact") in serious
        ]
        assert not violations, violations
        browser.close()
