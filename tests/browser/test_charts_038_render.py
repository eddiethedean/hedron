"""Browser evidence for RENDER/INTERACT/VISUAL-038 (skips without HEDRON_BROWSER)."""

from __future__ import annotations

import os

import pytest

from hedron_charts import BarChart, LineChart, ScatterChart
from hedron_charts.assets_038 import chart_module_path
from hedron_core.rendering import render

pytestmark = pytest.mark.browser

ENGINES = ("chromium", "firefox", "webkit")


def _chart_page(fragment_html: str, module_js: str) -> str:
    # Inline the module: Chromium blocks file:// ES modules from set_content pages.
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<title>Hedron chart browser fixture</title></head><body>"
        f"{fragment_html}"
        f"<script type='module'>\n{module_js}\n</script>"
        "</body></html>"
    )


def test_ssr_hedron_chart_without_browser() -> None:
    html = render(
        LineChart([{"x": 1, "y": 2}, {"x": 2, "y": 5}], x="x", y="y", title="T", description="D")
    ).html
    assert "hedron-chart" in html
    assert "data-hedron-payload" in html


@pytest.mark.parametrize("engine", ENGINES)
def test_hedron_chart_upgrades(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    html = render(
        LineChart([{"x": 1, "y": 2}, {"x": 2, "y": 5}], x="x", y="y", title="T", description="D")
    ).html
    module_js = chart_module_path().read_text(encoding="utf-8")
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        page = browser.new_page()
        page.set_content(_chart_page(html, module_js))
        page.wait_for_selector("hedron-chart[data-hedron-chart-mounted='1']", timeout=5000)
        assert page.locator("hedron-chart svg, hedron-chart canvas").count() >= 1
        browser.close()


@pytest.mark.parametrize("engine", ENGINES)
def test_hedron_chart_keydown_not_stacked_on_remount(engine: str) -> None:
    """#270: remounts leave at most one live keydown listener."""
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    html = render(
        LineChart([{"x": 1, "y": 2}, {"x": 2, "y": 5}], x="x", y="y", title="T", description="D")
    ).html
    module_js = chart_module_path().read_text(encoding="utf-8")
    probe = (
        "<script>"
        "window.__hcKeyAdds=0;window.__hcKeyRemoves=0;"
        "const add=EventTarget.prototype.addEventListener;"
        "EventTarget.prototype.addEventListener=function(type,listener,options){"
        "if(type==='keydown'&&this&&this.localName==='hedron-chart')window.__hcKeyAdds++;"
        "return add.call(this,type,listener,options);};"
        "const rem=EventTarget.prototype.removeEventListener;"
        "EventTarget.prototype.removeEventListener=function(type,listener,options){"
        "if(type==='keydown'&&this&&this.localName==='hedron-chart')window.__hcKeyRemoves++;"
        "return rem.call(this,type,listener,options);};"
        "</script>"
    )
    page_html = _chart_page(html, module_js).replace("<body>", "<body>" + probe, 1)
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        page = browser.new_page()
        page.set_content(page_html)
        page.wait_for_selector("hedron-chart[data-hedron-chart-mounted='1']", timeout=5000)
        page.locator("hedron-chart").evaluate(
            """el => {
              const raw = el.getAttribute('data-hedron-payload');
              for (let i = 0; i < 5; i++) {
                el.removeAttribute('data-hedron-payload');
                el.setAttribute('data-hedron-payload', raw);
              }
            }"""
        )
        live = page.evaluate("window.__hcKeyAdds - window.__hcKeyRemoves")
        assert live == 1
        browser.close()


@pytest.mark.parametrize("engine", ENGINES)
def test_hedron_chart_idle_resize_observer_does_not_remount(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    html = render(
        LineChart([{"x": 1, "y": 2}, {"x": 2, "y": 5}], x="x", y="y", title="T", description="D")
    ).html
    module_js = chart_module_path().read_text(encoding="utf-8")
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        page = browser.new_page()
        page.set_content(
            _chart_page(html, module_js).replace(
                "</head>",
                "<style>hedron-chart{display:block;padding:10px;border:2px solid}</style></head>",
            )
        )
        page.wait_for_selector("hedron-chart[data-hedron-chart-mounted='1']", timeout=5000)
        result = page.locator("hedron-chart").evaluate(
            """async el => {
              let changes = 0;
              const observer = new MutationObserver(mutations => {
                changes += mutations.filter(m => m.type === 'childList').length;
              });
              observer.observe(el, {subtree: true, childList: true});
              const mark = el.querySelector('circle');
              mark.focus();
              for (let i = 0; i < 8; i++) await new Promise(requestAnimationFrame);
              observer.disconnect();
              return {
                changes,
                connected: mark.isConnected,
                focused: document.activeElement === mark
              };
            }"""
        )
        assert result == {"changes": 0, "connected": True, "focused": True}
        browser.close()


@pytest.mark.parametrize("engine", ENGINES)
def test_hedron_chart_scatter_uses_numeric_x_spacing(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    html = render(
        ScatterChart(
            [{"x": 0, "y": 1}, {"x": 1, "y": 2}, {"x": 100, "y": 3}],
            x="x",
            y="y",
            title="T",
            description="D",
        )
    ).html
    module_js = chart_module_path().read_text(encoding="utf-8")
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        page = browser.new_page()
        page.set_content(_chart_page(html, module_js))
        page.wait_for_selector("hedron-chart[data-hedron-chart-mounted='1']", timeout=5000)
        positions = page.locator("hedron-chart circle").evaluate_all(
            "circles => circles.map(circle => Number(circle.getAttribute('cx')))"
        )
        assert positions == pytest.approx([40, 45.6, 600], abs=0.2)
        browser.close()


@pytest.mark.parametrize("engine", ENGINES)
def test_hedron_chart_numeric_string_categories_remain_ordinal(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    html = render(
        BarChart(
            [{"category": "1", "y": 1}, {"category": "2", "y": 2}, {"category": "100", "y": 3}],
            x="category",
            y="y",
            title="T",
            description="D",
        )
    ).html
    module_js = chart_module_path().read_text(encoding="utf-8")
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        page = browser.new_page()
        page.set_content(_chart_page(html, module_js))
        page.wait_for_selector("hedron-chart[data-hedron-chart-mounted='1']", timeout=5000)
        positions = page.locator("hedron-chart rect[data-hedron-mark]").evaluate_all(
            "rects => rects.map(rect => Number(rect.getAttribute('x')))"
        )
        assert positions[0] < positions[1] < positions[2] < 640
        browser.close()
