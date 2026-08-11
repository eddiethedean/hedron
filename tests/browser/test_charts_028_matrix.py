"""BROWSER charts matrix for BarChart/LineChart (CHARTS-028 print/CSP evidence)."""

from __future__ import annotations

import os
import socket
import threading
from collections.abc import Iterator

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright
from tests.browser._harness import reset_browser_plugin_state, wait_for_port

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(os.environ.get("HEDRON_BROWSER") != "1", reason="Opt-in browser"),
]

ENGINES = ("chromium",)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="module")
def app_url() -> Iterator[str]:
    uvicorn = pytest.importorskip("uvicorn")
    from hedron import Hedron, Page, Stack
    from hedron_charts import BarChart, LineChart

    reset_browser_plugin_state()
    app = Hedron(title="Charts028Matrix", security="standard", session_secret="s", explorer="off")

    @app.page("/")
    def home() -> Page:
        rows = [{"x": "a", "y": 1}, {"x": "b", "y": 2}]
        return Page(
            Stack(
                BarChart(rows, x="x", y="y", title="Bars028", description="bar demo"),
                LineChart(rows, x="x", y="y", title="Lines028", description="line demo"),
            )
        )

    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    wait_for_port(port)
    try:
        yield f"http://127.0.0.1:{port}/"
    finally:
        server.should_exit = True
        thread.join(timeout=5)


@pytest.mark.parametrize("engine", ENGINES)
def test_charts_028_matrix(engine: str, app_url: str) -> None:
    wanted = os.environ.get("HEDRON_BROWSER_ENGINE")
    if wanted and wanted != engine:
        pytest.skip(f"engine filter {wanted}")
    with sync_playwright() as p:
        browser_type = getattr(p, engine)
        browser = browser_type.launch()
        page = browser.new_page()
        page.goto(app_url)
        assert page.get_by_text("Bars028").count() >= 1
        assert page.get_by_text("Lines028").count() >= 1
        assert page.locator(".hedron-chart, [role='img'], [data-hedron-chart]").count() >= 1
        content = page.content().lower()
        for needle in (
            "cdn.plot.ly",
            "cdn.jsdelivr.net",
            "unpkg.com",
            "https://cdn.",
            "http://cdn.",
        ):
            assert needle not in content
        pdf = page.pdf()
        assert len(pdf) > 1000
        browser.close()
