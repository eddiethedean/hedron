"""BROWSER-047 three-engine host evidence (skips without HEDRON_BROWSER)."""

from __future__ import annotations

import os

import pytest

from hedron_core.rendering import render
from hedron_maps import Map
from hedron_maps.assets_047 import map_module_path

pytestmark = pytest.mark.browser

ENGINES = ("chromium", "firefox", "webkit")


def _map_page(fragment_html: str, module_js: str) -> str:
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<title>Hedron map browser fixture</title></head><body>"
        f"{fragment_html}"
        f"<script type='module'>\n{module_js}\n</script>"
        "</body></html>"
    )


def test_ssr_hedron_map_without_browser() -> None:
    html = render(Map(title="T", description="D")).html
    assert "hedron-map" in html
    assert "data-hedron-payload" in html
    assert "hedron-map-alternative" in html


@pytest.mark.parametrize("engine", ENGINES)
def test_hedron_map_upgrades(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    html = render(Map(title="T", description="D")).html
    module_js = map_module_path().read_text(encoding="utf-8")
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        page = browser.new_page()
        page.set_content(_map_page(html, module_js))
        page.wait_for_selector("hedron-map[data-hedron-map-mounted='1']", timeout=8000)
        assert page.locator(".hedron-map-alternative").count() >= 1
        browser.close()
