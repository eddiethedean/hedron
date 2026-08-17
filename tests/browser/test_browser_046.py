"""BROWSER-046: native + enhanced workflow path across engines (opt-in Playwright)."""

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
    from pydantic import BaseModel

    from hedron import Hedron, Page
    from hedron_data import DataWorkspace, DataWorkspacePolicy, InMemoryDataSource

    reset_browser_plugin_state()
    app = Hedron(
        title="Type046",
        security="standard",
        session_secret="browser-secret-046",
        explorer="development",
    )

    class Row(BaseModel):
        id: str
        title: str = "n"

    workspace = DataWorkspace(
        name="notes",
        model=Row,
        source=InMemoryDataSource([{"id": "1", "title": "hello"}], key_field="id"),
        policy=DataWorkspacePolicy(can_read=lambda: True),
    )
    app.include_feature(workspace)

    @app.page("/")
    def home():
        return Page(workspace.list_view(), title="Notes")  # type: ignore[misc]

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
        assert page.locator("table").count() >= 1
        page.goto(f"{url}/hedron-explorer/features")
        assert page.locator("table").count() >= 1
        browser.close()


@pytest.mark.parametrize("engine", ["chromium", "firefox", "webkit"])
def test_workspace_and_features_across_engines(engine: str, browser_app_url: str) -> None:
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    _run_engine(engine, browser_app_url)
