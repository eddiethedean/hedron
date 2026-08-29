"""Phase 0.67 Alpine CSP/plugin smoke across the supported browser engines."""

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
def browser_app_url() -> Iterator[str]:
    uvicorn = pytest.importorskip("uvicorn")
    from hedron import FileUpload, Hedron, Page, Tabs
    from hedron_core.alpine import AlpineAttrs, AlpineDirective, AlpineExpression
    from hedron_core.builtins.forms import Checkbox, Select, TextArea, TextInput
    from hedron_core.builtins.forms_extra import DirectoryUpload
    from hedron_core.builtins.live_ui import Dialog
    from hedron_core.builtins.utilities import Expander
    from hedron_core.html import html

    reset_browser_plugin_state()
    app = Hedron(
        title="Phase067Alpine",
        security="standard",
        session_secret="phase067-browser-secret",
        explorer="off",
    )

    @app.page("/")
    def home() -> Page:
        return Page(
            html.main(
                html.h1("Alpine smoke"),
                Expander(
                    "More details",
                    html.p("Expanded semantic content", id="browser-expander-body"),
                    id="browser-expander",
                ),
                Dialog(
                    "Browser dialog",
                    html.p("Dialog semantic content", id="browser-dialog-body"),
                    id="browser-dialog",
                ),
                html.button(
                    "Open dialog",
                    type="button",
                    id="open-browser-dialog",
                    data={"hedron-dialog-open": "#browser-dialog"},
                ),
                TextInput("browser-name", id="browser-name", value="Ada"),
                TextArea("browser-bio", id="browser-bio", value="Engineer"),
                Select("browser-role", (("admin", "Admin"),), id="browser-role", value="admin"),
                Checkbox("browser-enabled", "Enabled", id="browser-enabled", checked=True),
                DirectoryUpload(name="browser-directory", id="browser-directory"),
                FileUpload(name="browser-file", label="Upload browser file"),
                Tabs(
                    ("First", html.p("First panel")),
                    ("Second", html.p("Second panel")),
                    id="phase-tabs",
                ),
                html.button(
                    "Toggle",
                    type="button",
                    id="toggle",
                    alpine=AlpineAttrs.on(
                        "click",
                        AlpineExpression.assign(
                            "open",
                            AlpineExpression.binary(
                                "===",
                                AlpineExpression.name("open"),
                                AlpineExpression.literal(False),
                            ),
                        ),
                    ),
                ),
                html.p(
                    "Visible semantic content",
                    id="panel",
                    alpine=AlpineAttrs(
                        directives={
                            "x-show": AlpineExpression.name("open"),
                            "x-text": AlpineExpression.literal("Visible semantic content"),
                        },
                    ),
                ),
                html.label(
                    "Name",
                    html.input(
                        type="text",
                        id="name-input",
                        value="Ada",
                        alpine=AlpineAttrs.model("name", source="browser:phase067:name-input"),
                    ),
                ),
                html.output(
                    "Ada",
                    id="name-output",
                    alpine=AlpineAttrs.text(
                        AlpineExpression.name("name"), source="browser:phase067:name-output"
                    ),
                ),
                html.ul(
                    html.template(
                        html.li(
                            alpine=AlpineAttrs.text(
                                AlpineExpression.name("item"), source="browser:phase067:for-item"
                            ).merge(
                                AlpineAttrs.bind(
                                    "id",
                                    AlpineExpression.name("item"),
                                    source="browser:phase067:for-key",
                                )
                            )
                        ),
                        alpine=AlpineAttrs(
                            directives=(AlpineDirective("x-for", "item in items"),),
                            source="browser:phase067:for",
                        ),
                    ),
                    id="items",
                ),
                html.template(
                    html.p("Created detail", id="created-detail"),
                    alpine=AlpineAttrs(
                        directives=(AlpineDirective("x-if", AlpineExpression.name("showDetails")),),
                        source="browser:phase067:if",
                    ),
                ),
                html.button(
                    "Create detail",
                    type="button",
                    id="create-detail",
                    alpine=AlpineAttrs.on(
                        "click",
                        AlpineExpression.assign("showDetails", AlpineExpression.literal(True)),
                        source="browser:phase067:create-detail",
                    ),
                ),
                html.div(
                    "Focus trap",
                    id="trap",
                    alpine=AlpineAttrs(
                        directives={"x-trap": AlpineExpression.name("open")},
                        features=(
                            "anchor",
                            "collapse",
                            "focus",
                            "intersect",
                            "mask",
                            "morph",
                            "persist",
                            "resize",
                            "sort",
                            "ui",
                        ),
                    ),
                ),
                alpine=AlpineAttrs(
                    state={
                        "open": False,
                        "name": "Ada",
                        "items": ["one", "two"],
                        "showDetails": False,
                    },
                    directives=(AlpineDirective("x-init", AlpineExpression.name("open")),),
                    source="browser:phase067",
                ),
            ),
            title="Phase 0.67 Alpine",
        )

    port = _free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    wait_for_port(port)
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=5)


@pytest.mark.parametrize("engine", ("chromium", "firefox", "webkit"))
def test_alpine_core_and_focus_plugin_are_demand_loaded(browser_app_url: str, engine: str) -> None:
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"HEDRON_BROWSER_ENGINE={selected}")
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch(headless=True)
        page = browser.new_page()
        try:
            response = page.goto(browser_app_url + "/")
            assert response is not None and response.ok
            assert page.locator('meta[name="hedron-browser-plan"]').count() == 1
            assert page.locator('script[src*="csp-3.16.3.js"]').count() == 1
            assert page.locator('script[src*="focus-3.16.3.js"]').count() == 1
            for plugin in (
                "anchor",
                "collapse",
                "intersect",
                "mask",
                "morph",
                "persist",
                "resize",
                "sort",
                "ui",
            ):
                assert page.locator(f'script[src*="{plugin}-3.16.3.js"]').count() == 1
            page.get_by_role("button", name="Toggle").click()
            page.wait_for_function(
                "() => document.querySelector('#panel')?.style.display !== 'none'",
                timeout=5_000,
            )
            page.get_by_role("button", name="Toggle").click()
            page.wait_for_function(
                "() => document.querySelector('#panel')?.style.display === 'none'"
            )
            page.locator("#browser-expander > summary").click()
            page.locator("#browser-expander-body").wait_for(state="visible")
            page.locator("#browser-expander > summary").click()
            page.locator("#browser-expander-body").wait_for(state="hidden")
            page.get_by_role("button", name="Open dialog").click()
            page.locator("#browser-dialog").wait_for(state="visible")
            assert page.locator("#browser-dialog").get_attribute("open") is not None
            page.get_by_role("button", name="Close").click()
            page.locator("#browser-dialog").wait_for(state="hidden")
            page.locator("input[type=file][name='browser-file']").set_input_files(
                {"name": "readme.txt", "mimeType": "text/plain", "buffer": b"hello"}
            )
            page.locator("#hedron-file-upload-status-browser-file-local").wait_for(state="visible")
            assert page.locator("#name-output").inner_text() == "Ada"
            page.locator("#name-input").fill("Grace")
            page.wait_for_function(
                "() => document.querySelector('#name-output')?.textContent === 'Grace'"
            )
            assert page.locator("#items li").count() == 2
            page.get_by_role("button", name="Create detail").click()
            page.wait_for_selector("#created-detail")
            page.get_by_role("tab", name="Second").click()
            page.wait_for_function(
                "() => document.querySelector('#phase-tabs-panel-1')?.style.display !== 'none'"
            )
        finally:
            browser.close()


def test_semantic_content_survives_javascript_disabled(browser_app_url: str) -> None:
    with sync_playwright() as pw:
        browser = getattr(pw, os.environ.get("HEDRON_BROWSER_ENGINE") or "chromium").launch(
            headless=True
        )
        context = browser.new_context(java_script_enabled=False)
        page = context.new_page()
        try:
            response = page.goto(browser_app_url + "/")
            assert response is not None and response.ok
            assert page.get_by_role("heading", name="Alpine smoke").is_visible()
            assert page.get_by_role("button", name="Toggle").is_visible()
            assert page.locator("#panel").is_visible()
            assert page.locator("#name-input").input_value() == "Ada"
        finally:
            context.close()
            browser.close()


def test_semantic_content_survives_alpine_asset_failure(browser_app_url: str) -> None:
    with sync_playwright() as pw:
        browser = getattr(pw, os.environ.get("HEDRON_BROWSER_ENGINE") or "chromium").launch(
            headless=True
        )
        context = browser.new_context()
        page = context.new_page()
        page.route("**/hedron-static/alpine/*.js", lambda route: route.abort())
        try:
            response = page.goto(browser_app_url + "/")
            assert response is not None and response.ok
            assert page.get_by_role("heading", name="Alpine smoke").is_visible()
            assert page.get_by_role("button", name="Toggle").is_visible()
            assert page.locator("#name-input").is_visible()
        finally:
            context.close()
            browser.close()


def test_integrity_failure_does_not_cloak_semantic_content(browser_app_url: str) -> None:
    with sync_playwright() as pw:
        browser = getattr(pw, os.environ.get("HEDRON_BROWSER_ENGINE") or "chromium").launch(
            headless=True
        )
        context = browser.new_context()
        page = context.new_page()

        def corrupt_core(route: object) -> None:
            route.fulfill(status=200, body="export default {};", content_type="text/javascript")

        page.route("**/hedron-static/alpine/csp-3.16.3.js", corrupt_core)
        try:
            response = page.goto(browser_app_url + "/")
            assert response is not None and response.ok
            assert page.get_by_role("heading", name="Alpine smoke").is_visible()
            assert page.locator("#panel").is_visible()
        finally:
            context.close()
            browser.close()
