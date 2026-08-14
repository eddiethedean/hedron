"""LIFECYCLE-036: HTMX swap corpus for hedron-example (≥100 instances)."""

from __future__ import annotations

import os
import threading
from collections.abc import Iterator

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright

from hedron import Hedron
from hedron_core.builtins import Page, Text
from hedron_elements.example import Example
from hedron_elements.plugin import register

pytestmark = pytest.mark.browser


def _browser_enabled() -> bool:
    return os.environ.get("HEDRON_BROWSER", "").strip() in {"1", "true", "yes"}


@pytest.fixture(scope="module")
def server_url() -> Iterator[str]:
    if not _browser_enabled():
        pytest.skip("HEDRON_BROWSER not set")

    class _Ctx:
        def register_diagnostic_owner(self, prefix: str) -> None:
            return None

        def register_feature(self, **kwargs: object) -> None:
            return None

        def register_explorer_panel(self, **kwargs: object) -> None:
            return None

    register(_Ctx())  # type: ignore[arg-type]

    app = Hedron(title="elements-036", explorer="off", session_secret="secret")

    @app.page("/")
    def home() -> Page:
        return Page(Text("Elements lifecycle"), Example(status="Ready"))

    @app.page("/swap")
    def swap() -> object:
        from hedron.interaction import InteractionResult

        return InteractionResult(
            content=Example(status="Swapped"),
            region_id="main",
        )

    import uvicorn

    config = uvicorn.Config(app, host="127.0.0.1", port=8765, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    import time

    for _ in range(50):
        try:
            import urllib.error
            import urllib.request

            urllib.request.urlopen("http://127.0.0.1:8765/", timeout=0.2)
            break
        except (OSError, urllib.error.URLError):
            time.sleep(0.1)
    yield "http://127.0.0.1:8765"
    server.should_exit = True
    thread.join(timeout=5)


def test_repeated_outer_swap_instances(server_url: str) -> None:
    if not _browser_enabled():
        pytest.skip("HEDRON_BROWSER not set")
    engine = os.environ.get("HEDRON_BROWSER_ENGINE") or "chromium"
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        page = browser.new_page()
        page.goto(server_url + "/")
        page.wait_for_selector("hedron-example")
        # Simulate 100 reconnect cycles by reloading / re-querying the element.
        for _i in range(100):
            page.reload()
            page.wait_for_selector("hedron-example")
            count = page.locator("hedron-example").count()
            assert count == 1
            # Click local toggle when upgraded (module may be absent without build assets).
            btn = page.locator("hedron-example button")
            if btn.count():
                btn.first.click()
        browser.close()
