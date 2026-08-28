"""Browser regressions for the v1.0 open-issue implementation."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from hedron_core import render
from hedron_core.builtins.shell import AppShell

pytestmark = pytest.mark.browser


@pytest.mark.parametrize("engine", ("chromium", "firefox", "webkit"))
def test_collapsible_app_shell_keeps_rail_and_main_in_desktop_columns(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    css = (
        Path(__file__).resolve().parents[2]
        / "packages/hedron-core/src/hedron_core/static/hedron-default.css"
    ).read_text(encoding="utf-8")
    ui = (
        Path(__file__).resolve().parents[2]
        / "packages/hedron-core/src/hedron_core/static/hedron-ui.mjs"
    ).read_text(encoding="utf-8")
    markup = render(AppShell(nav="Navigation", body="Main", nav_collapse="user")).html

    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch(headless=True)
        context = browser.new_context(viewport={"width": 1200, "height": 800})
        page = context.new_page()
        page.set_content(f"<style>{css}</style>{markup}<script type='module'>{ui}</script>")

        toggle = page.locator(".hedron-app-shell-nav-toggle").bounding_box()
        nav = page.locator(".hedron-app-shell-nav").bounding_box()
        main = page.locator(".hedron-main-panel").bounding_box()
        assert toggle is not None and nav is not None and main is not None
        assert nav["y"] > toggle["y"]
        assert main["x"] > nav["x"] + nav["width"]
        assert abs(main["y"] - toggle["y"]) < 2

        button = page.locator(".hedron-app-shell-nav-toggle")
        assert button.get_attribute("aria-expanded") == "true"
        button.click()
        assert (
            page.locator(".hedron-app-shell").get_attribute("data-hedron-nav-collapsed") == "true"
        )
        assert button.get_attribute("aria-expanded") == "false"
        assert button.inner_text() == "Expand navigation"

        context.close()
