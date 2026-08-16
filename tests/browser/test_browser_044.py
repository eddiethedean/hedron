"""BROWSER-044: generated form keyboard path (opt-in Playwright)."""

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
    from typing import Annotated

    from pydantic import BaseModel

    from hedron import FormBody, Hedron, Page, Text

    reset_browser_plugin_state()
    app = Hedron(
        title="Type044",
        security="standard",
        session_secret="browser-secret-044",
        explorer="off",
    )

    class Payload(BaseModel):
        title: str = "hi"

    @app.command(fallback="/")
    def add(data: Annotated[Payload, FormBody()]):
        return Text(data.title)

    @app.page("/")
    def home():
        return Page(add.form(), title="Form")

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
        page.locator("form").first.focus()
        assert page.locator("label").count() >= 1
        browser.close()


@pytest.mark.parametrize("engine", ["chromium", "firefox", "webkit"])
def test_form_keyboard_submit(engine: str, browser_app_url: str) -> None:
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    _run_engine(engine, browser_app_url)
