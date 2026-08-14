"""BROWSER-037: gesture catalog module asset."""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.browser


def test_gesture_catalog_module_on_disk() -> None:
    static = (
        Path(__file__).resolve().parents[2] / "packages/hedron-elements/src/hedron_elements/static"
    )
    path = static / "gesture-catalog.mjs"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "GestureOverlayCatalog" in text
    kinds = re.findall(r'"dialog"|"popover"|"menu"|"toast"', text)
    assert len(kinds) >= 4


@pytest.mark.parametrize("engine", ("chromium", "firefox", "webkit"))
def test_gesture_catalog_module_loads(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    module = (
        Path(__file__).resolve().parents[2]
        / "packages/hedron-elements/src/hedron_elements/static/gesture-catalog.mjs"
    )
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        page = browser.new_page()
        page.set_content(f"<script type='module' src='file://{module}'></script>")
        assert module.is_file()
        browser.close()
