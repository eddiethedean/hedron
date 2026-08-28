"""Runtime HTMX lifecycle checks for chart hosts (opt-in Playwright)."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "packages" / "hedron-charts" / "src" / "hedron_charts" / "assets"

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"},
        reason="Opt-in: set HEDRON_BROWSER=1 and install Playwright browsers",
    ),
]


@contextmanager
def _browser_page() -> Iterator[object]:
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        engine = os.environ.get("HEDRON_BROWSER_ENGINE", "chromium")
        browser = getattr(pw, engine).launch(headless=True)
        context = browser.new_context()
        try:
            yield context.new_page()
        finally:
            context.close()


def _dispatch(page, selector: str, event_name: str) -> None:
    page.locator(selector).evaluate(
        "(el, name) => el.dispatchEvent(new CustomEvent(name, {bubbles: true}))",
        event_name,
    )


def test_plotly_host_disposes_and_remounts_a_self_targeted_swap() -> None:
    with _browser_page() as page:
        host = (ASSETS / "plotly/host.js").read_text(encoding="utf-8")
        page.set_content(
            f"""
            <div id="chart" data-hedron-chart="plotly"
                 data-hedron-payload='{{"data": [], "layout": {{}}}}'></div>
            <script>
              window.__calls = {{newPlot: 0, purge: 0}};
              window.Plotly = {{
                newPlot: () => {{ window.__calls.newPlot += 1; return Promise.resolve(); }},
                purge: () => {{ window.__calls.purge += 1; }}
              }};
            </script>
            <script>{host}</script>
            """
        )
        page.wait_for_function("() => window.__calls.newPlot === 1")

        _dispatch(page, "#chart", "htmx:beforeSwap")
        assert page.evaluate("window.__calls.purge") == 2
        _dispatch(page, "#chart", "htmx:afterSwap")
        page.wait_for_function("() => window.__calls.newPlot === 2")


def test_plotly_host_purges_a_stale_async_mount() -> None:
    with _browser_page() as page:
        host = (ASSETS / "plotly/host.js").read_text(encoding="utf-8")
        page.set_content(
            f"""
            <div id="chart" data-hedron-chart="plotly"
                 data-hedron-payload='{{"data": [], "layout": {{}}}}'></div>
            <script>
              window.__resolvers = [];
              window.__purges = 0;
              window.Plotly = {{
                newPlot: () => new Promise(resolve => window.__resolvers.push(resolve)),
                purge: () => {{ window.__purges += 1; }}
              }};
            </script>
            <script>{host}</script>
            """
        )
        page.wait_for_function("() => window.__resolvers.length === 1")
        _dispatch(page, "#chart", "htmx:afterSwap")
        page.wait_for_function("() => window.__resolvers.length === 2")

        page.evaluate("window.__resolvers[0]()")
        page.wait_for_function("() => window.__purges >= 3")


def test_static_host_clears_and_remounts_a_self_targeted_swap() -> None:
    with _browser_page() as page:
        host = (ASSETS / "static/host.js").read_text(encoding="utf-8")
        page.set_content(
            f"""
            <div id="chart" data-hedron-chart="static"
                 data-hedron-payload='{{"spec": {{"title": "Revenue"}}}}'></div>
            <script>{host}</script>
            """
        )
        chart = page.locator("#chart")
        assert "Revenue" in chart.inner_text()
        assert chart.get_attribute("data-hedron-chart-mounted") == "1"

        _dispatch(page, "#chart", "htmx:beforeSwap")
        assert chart.inner_text() == ""
        assert chart.get_attribute("data-hedron-chart-mounted") is None
        _dispatch(page, "#chart", "htmx:afterSwap")
        assert "Revenue" in chart.inner_text()
        assert chart.get_attribute("data-hedron-chart-mounted") == "1"
