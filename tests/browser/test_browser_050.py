"""BROWSER-050 Chromium/Firefox/WebKit Explorer journeys including provider crash."""

from __future__ import annotations

import os
import socket
import threading
from collections.abc import Iterator

import pytest
from tests.browser._harness import reset_browser_plugin_state, wait_for_port

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright

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
    from hedron import Hedron, Page, Text
    from hedron_core.plugins import ExplorerProvider, register_explorer_provider

    reset_browser_plugin_state()

    def _boom() -> str:
        raise RuntimeError("boom")

    register_explorer_provider(
        ExplorerProvider(panel_id="crashy", title="Crashy", plugin="demo", render=_boom)
    )

    app = Hedron(
        title="Explorer050",
        security="standard",
        session_secret="browser-secret-050",
        explorer="development",
    )

    @app.page("/")
    def home():
        return Page(Text("home"), title="Home")

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
    with sync_playwright() as playwright:
        launcher = getattr(playwright, browser_type)
        browser = launcher.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.goto(f"{url}/hedron-explorer/")
        assert page.locator("table").count() >= 1
        page.goto(f"{url}/hedron-explorer/packages")
        content = page.content()
        assert "Package health" in content
        assert "HED-EXPLORER-0002" in content
        browser.close()


def _maybe_skip_engine(engine: str) -> None:
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")


def test_chromium(browser_app_url: str) -> None:
    _maybe_skip_engine("chromium")
    _run_engine("chromium", browser_app_url)


def test_firefox(browser_app_url: str) -> None:
    _maybe_skip_engine("firefox")
    _run_engine("firefox", browser_app_url)


def test_webkit(browser_app_url: str) -> None:
    _maybe_skip_engine("webkit")
    _run_engine("webkit", browser_app_url)
