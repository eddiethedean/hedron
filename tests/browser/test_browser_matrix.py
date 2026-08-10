"""Three-engine HTMX hardening suite (phase 0.8)."""

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

ENGINES = ("chromium", "firefox", "webkit")


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
    from hedron_core.security import SafeUrl, UrlPurpose

    reset_browser_plugin_state()
    app = Hedron(
        title="BrowserMatrix",
        security="standard",
        session_secret="browser-secret",
        explorer="off",
    )
    regions = (
        FragmentRegion(id="chart-region", selector="#chart-region"),
        FragmentRegion(id="oob-status", selector="#oob-status"),
    )
    home_href = SafeUrl.parse("/", purpose=UrlPurpose.NAVIGATION)

    @app.page("/", fragment_regions=regions)
    def home() -> Page:
        return Page(
            Stack(
                html.div(Text("Primary panel"), id="chart-region"),
                html.div(Text("OOB status idle"), id="oob-status"),
                html.a("Boost link", href=home_href, id="boost-link"),
                html.button(
                    "Refresh",
                    type="button",
                    id="refresh",
                    **{
                        "hx-get": "/charts/fragment",
                        "hx-target": "#chart-region",
                        "hx-swap": "innerHTML",
                    },
                ),
            ),
            title="Browser matrix",
        )

    @app.component("/charts/fragment", fragment_regions=regions)
    def chart_fragment() -> InteractionResult:
        return InteractionResult(
            content=Text("Chart panel updated"),
            oob=(OobUpdate(content=Text("OOB status refreshed"), element_id="oob-status"),),
            policy=InteractionPolicy(declared_regions=regions, vary_on_target=True),
            cache="vary-htmx",
        )

    @app.page("/sensitive")
    def sensitive() -> Page:
        return Page(Text("private"), title="Sensitive")

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


def _launch(pw: object, engine: str):
    browser_type = getattr(pw, engine)
    return browser_type.launch(headless=True)


@pytest.fixture(params=ENGINES)
def engine(request: pytest.FixtureRequest) -> str:
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != request.param:
        pytest.skip(f"HEDRON_BROWSER_ENGINE={selected}")
    return str(request.param)


def test_fragment_oob_per_engine(browser_app_url: str, engine: str) -> None:
    with sync_playwright() as pw:
        browser = _launch(pw, engine)
        page = browser.new_page()
        try:
            page.goto(browser_app_url + "/")
            page.wait_for_selector("#chart-region")
            page.wait_for_function("() => typeof window.htmx !== 'undefined'")
            page.locator("#refresh").click()
            page.wait_for_function(
                "() => (document.querySelector('#chart-region')?.textContent || '')"
                ".includes('Chart panel updated')",
                timeout=15_000,
            )
            assert "OOB status refreshed" in page.locator("#oob-status").inner_text()
        finally:
            browser.close()


def test_csp_and_reduced_motion_meta(browser_app_url: str, engine: str) -> None:
    with sync_playwright() as pw:
        browser = _launch(pw, engine)
        page = browser.new_page()
        try:
            page.emulate_media(reduced_motion="reduce")
            response = page.goto(browser_app_url + "/")
            assert response is not None
            csp = response.headers.get("content-security-policy") or ""
            if not csp:
                # Some profiles emit CSP via meta; accept either form.
                csp = (
                    page.locator('meta[http-equiv="Content-Security-Policy"]').get_attribute(
                        "content"
                    )
                    or ""
                )
            assert csp, "expected Content-Security-Policy header or meta"
            assert "default-src" in csp or "script-src" in csp
            page.wait_for_function("() => typeof window.htmx !== 'undefined'", timeout=15_000)
            assert page.locator("#chart-region").count() == 1
        finally:
            browser.close()


def test_cache_vary_and_forbidden_target(browser_app_url: str, engine: str) -> None:
    # API-level assertions via the installed matrix engine (no Chromium hardcode).
    with sync_playwright() as pw:
        browser = _launch(pw, engine)
        page = browser.new_page()
        try:
            page.goto(browser_app_url + "/")
            frag = page.request.get(
                browser_app_url + "/charts/fragment",
                headers={"HX-Request": "true", "HX-Target": "#chart-region"},
            )
            assert frag.status == 200
            vary = frag.headers.get("vary", "")
            assert "HX-Request" in vary or "hx-request" in vary.lower()
            denied = page.request.get(
                browser_app_url + "/charts/fragment",
                headers={"HX-Request": "true", "HX-Target": "#evil"},
            )
            assert denied.status == 403
        finally:
            browser.close()


def test_history_restore_header_returns_page(browser_app_url: str, engine: str) -> None:
    """History restore must not return a bare fragment shell."""
    with sync_playwright() as pw:
        browser = _launch(pw, engine)
        page = browser.new_page()
        try:
            restored = page.request.get(
                browser_app_url + "/",
                headers={
                    "HX-Request": "true",
                    "HX-History-Restore-Request": "true",
                },
            )
            assert restored.status == 200
            body = restored.text()
            assert "<html" in body.lower()
        finally:
            browser.close()


def test_extension_assets_served(browser_app_url: str, engine: str) -> None:
    """Pinned SSE and head-support assets are locally reachable."""
    with sync_playwright() as pw:
        browser = _launch(pw, engine)
        page = browser.new_page()
        try:
            sse = page.request.get(browser_app_url + "/hedron-static/ext/sse.js")
            head = page.request.get(browser_app_url + "/hedron-static/ext/head-support.js")
            assert sse.status == 200
            assert "Server Sent Events" in sse.text() or "sse" in sse.text().lower()
            assert head.status == 200
            assert "head-support" in head.text().lower() or "head" in head.text().lower()
        finally:
            browser.close()


def test_htmx_core_loads_before_extensions(browser_app_url: str, engine: str) -> None:
    """Deferred extensions must not ReferenceError when the core is injected first (#55)."""
    page_errors: list[str] = []
    with sync_playwright() as pw:
        browser = _launch(pw, engine)
        page = browser.new_page()
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        try:
            page.goto(browser_app_url + "/", wait_until="load")
            page.wait_for_function("() => typeof window.htmx !== 'undefined'")
            assert page.evaluate("() => typeof window.htmx !== 'undefined'")
            assert not any("htmx is not defined" in err for err in page_errors), page_errors
        finally:
            browser.close()


def test_htmx_core_loads_before_extensions_under_mount(
    engine: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Custom Hedron mount paths must keep the same deferred script order (#55)."""
    uvicorn = pytest.importorskip("uvicorn")
    from starlette.applications import Starlette
    from starlette.routing import Mount

    from hedron import Hedron, Page, Stack, Text

    monkeypatch.setenv("HEDRON_ROOT_PATH", "/app")
    reset_browser_plugin_state()
    inner = Hedron(
        title="BrowserMounted",
        security="standard",
        session_secret="browser-secret-mounted",
        explorer="off",
    )

    @inner.page("/")
    def home() -> Page:
        return Page(Stack(Text("mounted")), title="Mounted")

    outer = Starlette(routes=[Mount("/app", app=inner)])
    port = _free_port()
    config = uvicorn.Config(outer, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    wait_for_port(port)
    page_errors: list[str] = []
    try:
        with sync_playwright() as pw:
            browser = _launch(pw, engine)
            page = browser.new_page()
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))
            try:
                page.goto(f"http://127.0.0.1:{port}/app/", wait_until="load")
                page.wait_for_function("() => typeof window.htmx !== 'undefined'")
                srcs = page.evaluate(
                    """() => Array.from(document.scripts)
                        .map((s) => s.getAttribute('src') || '')
                        .filter(Boolean)"""
                )
                core = "/app/hedron-static/htmx.min.js"
                assert core in srcs
                assert srcs.index(core) < srcs.index("/app/hedron-static/ext/head-support.js")
                assert srcs.index(core) < srcs.index("/app/hedron-static/ext/sse.js")
                assert not any("htmx is not defined" in err for err in page_errors), page_errors
            finally:
                browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=5)
