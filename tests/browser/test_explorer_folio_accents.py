"""Explorer accent controls follow the selected theme without JavaScript."""

from __future__ import annotations

import os
from urllib.parse import urlsplit

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hedron_core.theme import folio_theme
from hedron_explorer.router import explorer_router

pytestmark = pytest.mark.browser


@pytest.mark.parametrize("engine", ("chromium", "firefox", "webkit"))
def test_explorer_shows_accents_only_when_folio_is_selected(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected_engine = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected_engine and selected_engine != engine:
        pytest.skip(f"engine filter {selected_engine}")
    pytest.importorskip("playwright")
    from playwright.sync_api import Route, expect, sync_playwright

    app = FastAPI()
    app.include_router(explorer_router(), prefix="/hedron-explorer")
    with TestClient(app) as client, sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        page = browser.new_page(java_script_enabled=False)

        def serve(route: Route) -> None:
            url = urlsplit(route.request.url)
            response = client.get(url.path + ("?" + url.query if url.query else ""))
            headers = dict(response.headers)
            headers.pop("content-length", None)
            route.fulfill(status=response.status_code, headers=headers, body=response.content)

        page.route("http://testserver/**", serve)
        page.goto("http://testserver/hedron-explorer/theme-lab?left=classic&right=aurora")
        accents = page.get_by_label("Folio accent")
        expect(accents).to_be_hidden()
        page.get_by_label("Theme", exact=True).select_option("folio")
        expect(accents).to_be_visible()
        expect(accents).to_have_value("green")
        accents.select_option("blue")
        page.get_by_role("button", name="Apply", exact=True).click()
        expect(accents).to_have_value("blue")
        preview = page.locator('[data-theme-lab-theme="folio"]')
        expect(preview).to_contain_text("Accent: Blue")
        expect(preview).to_contain_text(folio_theme(accent="blue").tokens["color.accent"])
        page.get_by_label("Theme", exact=True).select_option("classic")
        expect(accents).to_be_hidden()
        page.get_by_label("Compare with").select_option("folio")
        expect(accents).to_be_visible()
        page.get_by_label("Compare with").select_option("aurora")
        expect(accents).to_be_hidden()
        browser.close()
