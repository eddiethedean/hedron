"""BROWSER-060: theme-platform component behavior and media fallbacks."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from hedron import Brand, ConnectorFlow, ScrollRegion, ToastHost, render

pytestmark = pytest.mark.browser


@pytest.mark.parametrize("engine", ("chromium", "firefox", "webkit"))
def test_phase060_component_layout_and_media_contract(engine: str) -> None:
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
    markup = "".join(
        (
            render(Brand("Hedron", subtitle="A very long framework subtitle")).html,
            render(ToastHost(placement="bottom-start", width="field")).html,
            render(ConnectorFlow(background="dots", overflow="scroll", min_size="lg")).html,
            render(ScrollRegion("long log", axis="both", size="sm", label="Events")).html,
        )
    )
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch(headless=True)
        context = browser.new_context(viewport={"width": 480, "height": 320})
        page = context.new_page()
        page.set_content(f"<style>{css}</style>{markup}")

        assert page.locator(".hedron-brand-copy").count() == 1
        assert page.locator("#hedron-toast").get_attribute("data-hedron-toast-width") == "field"
        assert page.locator(".hedron-scroll-region").get_attribute("role") == "region"
        assert page.locator(".hedron-connector-flow").count() == 1
        assert (
            page.evaluate(
                "getComputedStyle(document.querySelector('.hedron-brand-copy')).minInlineSize"
            )
            == "0px"
        )

        page.emulate_media(media="print")
        assert page.evaluate(
            "getComputedStyle(document.querySelector('.hedron-scroll-region')).overflow"
        ) in {"visible", "clip"}
        page.emulate_media(media="screen", reduced_motion="reduce")
        assert page.evaluate(
            "getComputedStyle(document.documentElement).getPropertyValue('--hedron-motion-duration')"
        ) in {"0ms", ""}
        context.close()
        browser.close()
