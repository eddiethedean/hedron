"""Browser HTMX lifecycle smoke for phase 0.6 (optional Playwright)."""

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
        reason="Opt-in: set HEDRON_BROWSER=1 and install hedron[browser] / Playwright Chromium",
    ),
]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="module")
def browser_app_url() -> Iterator[str]:
    uvicorn = pytest.importorskip("uvicorn")

    from hedron import Hedron, InteractionResult, Page, Stack, Text
    from hedron.interaction import FragmentRegion, InteractionPolicy, OobUpdate
    from hedron_core.html import html

    reset_browser_plugin_state()
    app = Hedron(
        title="BrowserSmoke",
        security="standard",
        session_secret="browser-secret",
        explorer="off",
    )
    regions = (
        FragmentRegion(id="chart-region", selector="#chart-region"),
        FragmentRegion(id="oob-status", selector="#oob-status"),
    )

    @app.page("/", fragment_regions=regions)
    def home() -> Page:
        return Page(
            Stack(
                html.div(Text("Primary panel"), id="chart-region"),
                html.div(Text("OOB status idle"), id="oob-status"),
                html.button(
                    "Refresh",
                    type="button",
                    **{
                        "hx-get": "/charts/fragment",
                        "hx-target": "#chart-region",
                        "hx-swap": "innerHTML",
                    },
                ),
                html.button(
                    "Bad target",
                    type="button",
                    id="bad-target",
                    **{
                        "hx-get": "/charts/fragment",
                        "hx-target": "#evil",
                        "hx-swap": "innerHTML",
                    },
                ),
            ),
            title="Browser smoke",
        )

    @app.component("/charts/fragment", fragment_regions=regions)
    def chart_fragment() -> InteractionResult:
        return InteractionResult(
            content=Text("Chart panel updated"),
            oob=(OobUpdate(content=Text("OOB status refreshed"), element_id="oob-status"),),
            policy=InteractionPolicy(declared_regions=regions, vary_on_target=True),
            cache="vary-htmx",
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


def _selected_engine() -> str:
    return os.environ.get("HEDRON_BROWSER_ENGINE") or "chromium"


def _open_ready_page(pw: object, url: str):  # noqa: ANN001
    browser_type = getattr(pw, _selected_engine())
    browser = browser_type.launch(headless=True)
    page = browser.new_page()
    page.goto(url + "/")
    page.wait_for_selector("#chart-region")
    page.wait_for_function("() => typeof window.htmx !== 'undefined'")
    return browser, page


def test_htmx_fragment_and_oob_update(browser_app_url: str) -> None:
    with sync_playwright() as pw:
        browser, page = _open_ready_page(pw, browser_app_url)
        try:
            page.get_by_role("button", name="Refresh").click()
            page.wait_for_function(
                "() => (document.querySelector('#chart-region')?.textContent || '')"
                ".includes('Chart panel updated')",
                timeout=10_000,
            )
            assert "OOB status refreshed" in page.locator("#oob-status").inner_text()
        finally:
            browser.close()


def test_unauthorized_target_returns_forbidden(browser_app_url: str) -> None:
    with sync_playwright() as pw:
        browser, page = _open_ready_page(pw, browser_app_url)
        try:
            response = page.request.get(
                browser_app_url + "/charts/fragment",
                headers={"HX-Request": "true", "HX-Target": "#evil"},
            )
            assert response.status == 403
        finally:
            browser.close()
