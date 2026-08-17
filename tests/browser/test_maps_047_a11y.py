"""A11Y-047 map alternative, keyboard, visual modes (skips engines without HEDRON_BROWSER)."""

from __future__ import annotations

import os

import pytest

from hedron_core.rendering import render
from hedron_maps import Map
from hedron_maps.assets_047 import map_module_path

pytestmark = pytest.mark.a11y

ENGINES = ("chromium", "firefox", "webkit")


def test_ssr_has_title_description_table() -> None:
    html = render(
        Map(
            title="Campus",
            description="Accessible campus map",
            markers=[{"id": "gate", "lat": 1.0, "lon": 2.0, "label": "Main gate", "href": "/gate"}],
        )
    ).html
    assert "Campus" in html
    assert "Accessible campus map" in html
    assert "hedron-map-alternative" in html
    assert "Main gate" in html
    assert 'role="region"' in html
    assert "SR-021" not in html


@pytest.mark.parametrize("engine", ENGINES)
def test_keyboard_can_leave_map(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    html = render(Map(title="T", description="D")).html
    page_html = (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'></head><body>"
        "<a href='#before'>before</a>"
        f"{html}"
        "<a href='#after'>after</a>"
        f"<script type='module'>\n{map_module_path().read_text(encoding='utf-8')}\n</script>"
        "</body></html>"
    )
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        page = browser.new_page()
        page.emulate_media(color_scheme="dark", reduced_motion="reduce")
        page.set_content(page_html)
        page.wait_for_selector("hedron-map[data-hedron-map-mounted='1']", timeout=8000)
        page.locator("[data-hedron-map-host]").focus()
        page.keyboard.press("Escape")
        page.keyboard.press("Tab")
        # Escape/Tab must not trap; after link remains reachable.
        assert page.locator("a[href='#after']").count() == 1
        browser.close()
