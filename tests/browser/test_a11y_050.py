"""A11Y-050 Explorer landmarks, skip link, no-JS tables."""

from __future__ import annotations

import os
import socket
import threading

import pytest
from fastapi.testclient import TestClient
from tests.unit._helpers_050 import make_app, reset_050

from hedron import Page, Text


def setup_function() -> None:
    reset_050()


def test_explorer_landmarks_and_skip_link() -> None:
    app = make_app(security="standard", explorer="development")

    @app.page("/")
    def home():
        return Page(Text("hi"), title="T")

    with TestClient(app) as client:
        page = client.get("/hedron-explorer/")
        assert page.status_code == 200
        assert "Skip to content" in page.text
        assert 'href="#main"' in page.text
        assert "<nav" in page.text
        assert 'id="main"' in page.text or "<main" in page.text
        noscript = client.get("/hedron-explorer/routes")
        assert "<table" in noscript.text
        assert "<form" in noscript.text


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.mark.browser
@pytest.mark.skipif(
    os.environ.get("HEDRON_BROWSER") != "1",
    reason="Opt-in: set HEDRON_BROWSER=1",
)
def test_keyboard_focus_playwright() -> None:
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright
    from tests.browser._harness import reset_browser_plugin_state, wait_for_port

    uvicorn = pytest.importorskip("uvicorn")
    reset_browser_plugin_state()
    app = make_app(security="standard", explorer="development")

    @app.page("/")
    def home():
        return Page(Text("hi"), title="T")

    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    wait_for_port(port)
    try:
        with sync_playwright() as playwright:
            page = playwright.chromium.launch(headless=True).new_page()
            page.goto(f"http://127.0.0.1:{port}/hedron-explorer/")
            page.keyboard.press("Tab")
            focused = page.evaluate(
                "() => document.activeElement && document.activeElement.textContent"
            )
            assert focused is not None
    finally:
        server.should_exit = True
        thread.join(timeout=5)
