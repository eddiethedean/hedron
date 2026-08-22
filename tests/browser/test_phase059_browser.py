"""BROWSER-059: modern CSS feature-on and fallback evidence."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.browser


@pytest.mark.parametrize("engine", ("chromium", "firefox", "webkit"))
def test_phase059_css_feature_and_fallback_contract(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    css_path = (
        Path(__file__).resolve().parents[2]
        / "packages/hedron-core/src/hedron_core/static/hedron-default.css"
    )
    css = css_path.read_text(encoding="utf-8")
    assert "@media print" in css
    assert "prefers-reduced-motion" in css
    assert "container-type: inline-size" in css
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch(headless=True)
        page = browser.new_page()
        page.set_content(
            f"<style>{css}</style>"
            "<div class='hedron-container' data-hedron-container-query='inline-size'>"
            "<p id='content'>Content</p></div>"
            "<button id='trigger' popovertarget='panel'>Open</button>"
            "<div id='panel' popover='auto'>Panel</div>"
            "<dialog id='dialog'>Dialog</dialog>"
        )
        assert page.locator("[data-hedron-container-query='inline-size']").count() == 1
        assert page.locator("#content").inner_text() == "Content"
        assert page.locator("#trigger").get_attribute("popovertarget") == "panel"
        assert page.locator("#dialog").count() == 1

        page.emulate_media(media="print")
        assert page.evaluate("getComputedStyle(document.body).paddingTop") == "0px"
        page.emulate_media(media="screen", reduced_motion="reduce")
        assert page.evaluate(
            "getComputedStyle(document.documentElement).getPropertyValue('--hedron-motion-duration')"
        ) in {"0ms", ""}
        browser.close()
