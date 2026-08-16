"""BROWSER-043: handle lifecycle across engines (opt-in Playwright)."""

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
    pytest.mark.skipif(
        os.environ.get("HEDRON_BROWSER") != "1",
        reason="Opt-in: set HEDRON_BROWSER=1 and install hedron[browser] / Playwright",
    ),
]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="module")
def browser_app_url() -> Iterator[str]:
    uvicorn = pytest.importorskip("uvicorn")
    from hedron import Hedron, Page, Text, html, refresh

    reset_browser_plugin_state()
    app = Hedron(
        title="Handles043",
        security="standard",
        session_secret="browser-secret-043",
        explorer="off",
    )

    @app.refreshable
    def status():
        return html.div(Text("ready"), **{"data-hedron-mark": "status"})

    @app.command(fallback="/")
    def ping():
        return refresh(status).toast("pong")

    @app.page("/")
    def home() -> Page:
        return Page(
            status(),
            status.refresh_button("Refresh"),
            ping.button("Ping"),
            title="Handles",
        )

    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    wait_for_port(port)
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=5)


def _run_engine(browser_type: str, url: str) -> None:
    with sync_playwright() as p:
        launcher = getattr(p, browser_type)
        browser = launcher.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        assert page.locator("#h-view-status").count() == 1
        page.get_by_role("button", name="Refresh").click()
        page.wait_for_timeout(200)
        assert page.locator("#h-view-status").count() == 1
        page.get_by_role("button", name="Ping").click()
        page.wait_for_timeout(300)
        assert page.locator("#h-view-status").count() == 1
        browser.close()


@pytest.mark.parametrize("engine", ["chromium", "firefox", "webkit"])
def test_handle_lifecycle_three_engines(engine: str, browser_app_url: str) -> None:
    _run_engine(engine, browser_app_url)
