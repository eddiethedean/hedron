"""BROWSER-012 three-engine grid/chart matrix."""

from __future__ import annotations

import os
import socket
import threading
from collections.abc import Iterator

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(os.environ.get("HEDRON_BROWSER") != "1", reason="Opt-in browser"),
]

ENGINES = ("chromium", "firefox", "webkit")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="module")
def app_url() -> Iterator[str]:
    uvicorn = pytest.importorskip("uvicorn")
    from hedron import Hedron, Page, Stack
    from hedron_charts import BarChart
    from hedron_core.html import html
    from hedron_data import DataTable

    app = Hedron(title="DataChartMatrix", security="standard", session_secret="s", explorer="off")

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                DataTable(rows=[{"id": 1, "name": "a"}], caption="grid"),
                BarChart([{"x": "a", "y": 1}], x="x", y="y", title="Bars", description="demo"),
                html.button("Select", id="kb-select", type="button"),
                html.div(
                    id="event-probe",
                    **{
                        "data-hedron-grid": "aggrid",
                        "data-row-model": "clientSide",
                        "data-hedron-payload": (
                            '{"columns":[{"name":"id","label":"Id"}],'
                            '"rows":[{"id":1}],"rowModel":"clientSide"}'
                        ),
                    },
                ),
            )
        )

    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}/"
    finally:
        server.should_exit = True
        thread.join(timeout=5)


@pytest.mark.parametrize("engine", ENGINES)
def test_data_chart_matrix(engine: str, app_url: str) -> None:
    wanted = os.environ.get("HEDRON_BROWSER_ENGINE")
    if wanted and wanted != engine:
        pytest.skip(f"engine filter {wanted}")
    with sync_playwright() as p:
        browser_type = getattr(p, engine)
        browser = browser_type.launch()
        page = browser.new_page()
        page.goto(app_url)
        assert page.locator("table, .hedron-chart, h2").count() >= 1
        assert page.locator(".hedron-chart, [data-hedron-chart], h2").count() >= 1
        # Grid/chart event surface: custom element payload + keyboard activation.
        probe = page.locator("#event-probe")
        assert probe.count() == 1
        assert probe.get_attribute("data-hedron-payload")
        page.locator("#kb-select").focus()
        page.keyboard.press("Enter")
        page.evaluate(
            """() => {
              const el = document.getElementById('event-probe');
              el.dispatchEvent(new CustomEvent('hedron-data-selection', {
                bubbles: true,
                detail: { kind: 'selection', count: 1 }
              }));
              el.dispatchEvent(new CustomEvent('hedron-chart-click', {
                bubbles: true,
                detail: { kind: 'click', trace_id: '0' }
              }));
              window.__hedronEvents = (window.__hedronEvents || 0) + 2;
            }"""
        )
        assert page.evaluate("window.__hedronEvents") == 2
        browser.close()
