"""BROWSER-041: three-engine composition/navigation failure-isolation smoke."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.browser


@pytest.mark.parametrize("engine", ("chromium", "firefox", "webkit"))
def test_phase041_module_preserves_native_fallback(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    module = (
        Path(__file__).resolve().parents[2]
        / "packages/hedron-elements/src/hedron_elements/static/composition-041.mjs"
    )
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        page = browser.new_page()
        page.set_content(
            "<main tabindex='-1'><a id='fragment' href='#target'>Jump</a>"
            "<section id='target'>Server fallback</section></main>"
            f"<script type='module' src='{module.as_uri()}'></script>"
        )
        assert page.locator("#target").inner_text() == "Server fallback"
        page.locator("#fragment").click()
        assert page.evaluate("location.hash") == "#target"
        browser.close()
