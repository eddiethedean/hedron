"""Browser regression: explicit OobUpdate preserves semantic shell hosts (#57)."""

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
        reason="Opt-in: set HEDRON_BROWSER=1 and install Playwright browsers",
    ),
]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="module")
def shell_app_url() -> Iterator[str]:
    uvicorn = pytest.importorskip("uvicorn")

    from hedron import Hedron, HtmxLink, InteractionResult, MainPanel, Page, Stack, Text, html
    from hedron.interaction import FragmentRegion, InteractionPolicy, OobUpdate
    from hedron_core.security import SafeUrl, UrlPurpose

    reset_browser_plugin_state()
    app = Hedron(
        title="ShellOobSemantics",
        security="standard",
        session_secret="browser-secret",
        explorer="off",
    )
    regions = (
        FragmentRegion(id="main-panel", selector="#main-panel"),
        FragmentRegion(id="side-nav", selector="#side-nav"),
    )
    policy = InteractionPolicy(declared_regions=regions, vary_on_target=True)

    def _href(path: str) -> SafeUrl:
        return SafeUrl.parse(path, purpose=UrlPurpose.NAVIGATION)

    def side_nav(*items: str):
        return html.nav(
            *[html.a(label, href=_href(f"/{label.lower()}")) for label in items],
            id="side-nav",
            aria={"label": "Account navigation"},
        )

    @app.page("/", fragment_regions=regions)
    def home() -> Page:
        return Page(
            Stack(
                side_nav("Home", "Profile"),
                MainPanel(Text("Home panel"), id="main-panel"),
                HtmxLink(
                    "Profile",
                    "/profile",
                    target="#main-panel",
                    swap="innerHTML",
                    # Intentionally omit select_oob for #side-nav — OobUpdate owns that target.
                    id="go-profile",
                ),
            ),
            title="Shell OOB",
        )

    @app.fragment("/profile", fragment_regions=regions)
    def profile() -> InteractionResult:
        return InteractionResult(
            content=Text("Profile panel"),
            oob=(
                OobUpdate(
                    content=html.a("Profile", href=_href("/profile")),
                    element_id="side-nav",
                    swap="innerHTML",
                ),
            ),
            policy=policy,
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


def test_side_nav_remains_nav_with_aria_label(shell_app_url: str) -> None:
    with sync_playwright() as pw:
        browser = getattr(pw, _selected_engine()).launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(shell_app_url + "/")
            before = page.evaluate(
                """() => {
                  const el = document.querySelector("#side-nav");
                  return {tag: el && el.tagName, label: el && el.getAttribute("aria-label")};
                }"""
            )
            assert before == {"tag": "NAV", "label": "Account navigation"}
            page.click("#go-profile")
            page.wait_for_function(
                "() => document.querySelector('#main-panel')?.textContent?.includes('Profile')"
            )
            after = page.evaluate(
                """() => {
                  const el = document.querySelector("#side-nav");
                  return {tag: el && el.tagName, label: el && el.getAttribute("aria-label")};
                }"""
            )
            assert after == {"tag": "NAV", "label": "Account navigation"}
        finally:
            browser.close()


@pytest.fixture(scope="module")
def shell_conflict_app_url() -> Iterator[str]:
    """Anti-pattern fixture: select_oob + OobUpdate on the same id (#57)."""
    uvicorn = pytest.importorskip("uvicorn")

    from hedron import Hedron, HtmxLink, InteractionResult, MainPanel, Page, Stack, Text, html
    from hedron.interaction import FragmentRegion, InteractionPolicy, OobUpdate
    from hedron_core.security import SafeUrl, UrlPurpose

    reset_browser_plugin_state()
    app = Hedron(
        title="ShellOobConflict",
        security="standard",
        session_secret="browser-secret",
        explorer="off",
    )
    regions = (
        FragmentRegion(id="main-panel", selector="#main-panel"),
        FragmentRegion(id="side-nav", selector="#side-nav"),
    )
    policy = InteractionPolicy(declared_regions=regions, vary_on_target=True)

    def _href(path: str) -> SafeUrl:
        return SafeUrl.parse(path, purpose=UrlPurpose.NAVIGATION)

    def side_nav(*items: str):
        return html.nav(
            *[html.a(label, href=_href(f"/{label.lower()}")) for label in items],
            id="side-nav",
            aria={"label": "Account navigation"},
        )

    @app.page("/", fragment_regions=regions)
    def home() -> Page:
        return Page(
            Stack(
                side_nav("Home", "Profile"),
                MainPanel(Text("Home panel"), id="main-panel"),
                HtmxLink(
                    "Profile",
                    "/profile",
                    target="#main-panel",
                    swap="innerHTML",
                    select_oob="#side-nav",
                    id="go-profile-conflict",
                ),
            ),
            title="Shell OOB conflict",
        )

    @app.fragment("/profile", fragment_regions=regions)
    def profile() -> InteractionResult:
        # OuterHTML OOB envelope + matching select_oob replaces the <nav> host.
        return InteractionResult(
            content=Text("Profile panel"),
            oob=(
                OobUpdate(
                    content=html.a("Profile", href=_href("/profile")),
                    element_id="side-nav",
                    swap="outerHTML",
                ),
            ),
            policy=policy,
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


def test_select_oob_plus_oobupdate_replaces_nav_host(shell_conflict_app_url: str) -> None:
    """Regression evidence for #57: the conflict replaces landmark <nav> with a div."""
    with sync_playwright() as pw:
        browser = getattr(pw, _selected_engine()).launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(shell_conflict_app_url + "/")
            page.click("#go-profile-conflict")
            page.wait_for_function(
                "() => document.querySelector('#main-panel')?.textContent?.includes('Profile')"
            )
            after = page.evaluate(
                """() => {
                  const el = document.querySelector("#side-nav");
                  return {tag: el && el.tagName, label: el && el.getAttribute("aria-label")};
                }"""
            )
            assert after["tag"] == "DIV"
            assert after["label"] is None
        finally:
            browser.close()
