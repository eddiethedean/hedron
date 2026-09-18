"""Browser behavior of the static styles lab, served without an app backend."""

from __future__ import annotations

import functools
import http.server
import json
import os
import threading
from pathlib import Path

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(os.environ.get("HEDRON_BROWSER") != "1", reason="Opt-in browser test"),
]


@pytest.fixture
def static_url():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / "docs"))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/assets/styles-explorer/index.html"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_explorer_navigation_themes_comparison_and_exports(static_url, tmp_path) -> None:
    engine = os.environ.get("HEDRON_BROWSER_ENGINE", "chromium")
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors = []
        requests = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: requests.append((request.method, request.url)))
        page.goto(static_url)
        preview = page.frame_locator("#left")
        expect(preview.locator("#style-gallery")).to_contain_text("Operations dashboard")
        page.locator("#section").select_option("components")
        expect(preview.locator("#style-gallery")).to_contain_text("Component states")
        for theme in ("classic", "aurora", "folio"):
            page.locator("#theme").select_option(theme)
            for mode in ("dark", "light"):
                page.locator("#mode").select_option(mode)
                expect(preview.locator("html")).to_have_attribute("data-hedron-theme", theme)
                expect(preview.locator("html")).to_have_attribute("data-theme", mode)
                actual = preview.locator("html").evaluate(
                    "el => getComputedStyle(el).getPropertyValue('--hedron-color-bg').trim()"
                )
                expected = page.evaluate(
                    """([theme, mode]) => {
                        const data = JSON.parse(
                            document.getElementById('explorer-data').content.textContent);
                        const name = theme === 'folio' ? 'folio:green' : theme;
                        return data.themes[name].resolved_modes[mode]['color.bg'];
                    }""",
                    [theme, mode],
                )
                assert actual == expected
        before = preview.locator("html").evaluate(
            "el => getComputedStyle(el).getPropertyValue('--hedron-color-accent').trim()"
        )
        page.locator("#accent").select_option("blue")
        after = preview.locator("html").evaluate(
            "el => getComputedStyle(el).getPropertyValue('--hedron-color-accent').trim()"
        )
        assert before != after
        for accent in ("violet", "amber", "rose", "green", "blue"):
            page.locator("#accent").select_option(accent)
            expect(preview.locator("html")).to_have_attribute(
                "data-hedron-theme", "folio" if accent == "green" else f"folio-{accent}"
            )
        page.locator("#compare").select_option("aurora")
        expect(page.locator("#comparison")).to_be_visible()
        expect(page.frame_locator("#right").locator("#style-gallery")).to_contain_text(
            "Component states"
        )
        preview.get_by_role("link", name="Forms", exact=True).click()
        expect(page.locator("#section")).to_have_value("forms")
        expect(page.frame_locator("#right").locator("[data-hedron-sim-trace]")).to_contain_text(
            "GET /forms → 200"
        )
        # A native form submission must never POST to the static host.
        page.locator("#section").select_option("settings")
        expect(preview.locator("[data-hedron-sim-trace]")).to_contain_text("GET /settings → 200")
        preview.locator("form").first.evaluate("form => form.requestSubmit()")
        page.locator("#section").select_option("components")
        expect(preview.locator("#style-gallery")).to_contain_text("Component states")
        assert page.locator("#tokens tr.different").count() > 0
        page.locator("#token-filter").fill("color.bg")
        expect(page.locator("#tokens")).to_contain_text("color.bg")
        page.locator("#component-filter").fill("button")
        assert page.locator("#contracts details").count() > 0
        page.locator("#contracts summary").first.click()
        expect(page.locator("#contracts pre").first).to_be_visible()
        for label in (
            "Forms",
            "Surfaces",
            "Content",
            "Settings",
            "Orders",
            "Support",
            "Media",
            "Dashboard",
        ):
            page.locator("#section").select_option(label.lower())
            expect(preview.locator("[data-hedron-sim-trace]")).to_contain_text(
                f"GET /{label.lower()} → 200"
            )
        page.locator("#section").select_option("components")
        expect(preview.locator("#style-gallery")).to_contain_text("Component states")
        preview.get_by_role("tab", name="Feedback", exact=True).click()
        expect(preview.get_by_role("tabpanel").filter(has_text="New information")).to_be_visible()
        preview.get_by_role("button", name="Review changes", exact=True).click()
        expect(preview.locator("#gallery-dialog")).to_be_visible()
        preview.locator("#gallery-dialog").evaluate("dialog => dialog.close()")
        for control, filename in (
            ("export-css", "folio.css"),
            ("export-json", "folio.json"),
            ("export-report", "hedron-style-comparison.json"),
        ):
            with page.expect_download() as download_info:
                page.locator(f"#{control}").click()
            download = download_info.value
            assert download.suggested_filename == filename
            path = tmp_path / filename
            download.save_as(path)
            if control == "export-report":
                report = json.loads(path.read_text())
                assert report["selection"]["accent"] == "blue"
                assert report["differences"]
            elif control == "export-json":
                assert json.loads(path.read_text())["name"] == "folio-blue"
            else:
                assert "@layer tokens" in path.read_text()
        page.locator("#width").select_option("390px")
        assert page.locator("#left").evaluate("el => el.clientWidth") == 390
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
        saved = page.url
        page.reload()
        expect(page.locator("#accent")).to_have_value("blue")
        expect(page.locator("#section")).to_have_value("components")
        assert page.url == saved
        assert errors == []
        assert all(
            method == "GET" and url.startswith(static_url.split("/assets/")[0])
            for method, url in requests
        )
        browser.close()
