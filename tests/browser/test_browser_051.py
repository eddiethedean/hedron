"""BROWSER-051 extras hosts and companion authoring."""

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
    from hedron import Hedron, Page, TextInput
    from hedron_extras.composition import ChoiceCards

    reset_browser_plugin_state()
    app = Hedron(title="Extras051", security="standard", session_secret="browser-secret-051")

    @app.page("/")
    def home():
        return Page(
            ChoiceCards("pick", [{"value": "a", "label": "A"}]),
            TextInput("pw", type="password"),
            title="Extras",
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
    with sync_playwright() as playwright:
        launcher = getattr(playwright, browser_type)
        browser = launcher.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector("hedron-extras-composition")
        assert page.locator("[data-hedron-password-toggle]").count() >= 1
        page.locator("[data-hedron-password-toggle]").first.click()
        assert page.locator('input[name="pw"]').get_attribute("type") == "text"
        browser.close()


def _maybe_skip_engine(engine: str) -> None:
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")


@pytest.mark.parametrize("engine", ["chromium", "firefox", "webkit"])
def test_extras_hosts_three_engines(engine: str, browser_app_url: str) -> None:
    _maybe_skip_engine(engine)
    _run_engine(engine, browser_app_url)
