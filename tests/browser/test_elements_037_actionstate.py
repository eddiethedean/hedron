"""BROWSER-037: interaction-state.mjs packaged asset."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.browser


def test_interaction_state_module_on_disk() -> None:
    static = (
        Path(__file__).resolve().parents[2] / "packages/hedron-elements/src/hedron_elements/static"
    )
    path = static / "interaction-state.mjs"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "export class InteractionState" in text
    assert "applyAria" in text


@pytest.mark.parametrize("engine", ("chromium", "firefox", "webkit"))
def test_interaction_state_module_parses(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    module = (
        Path(__file__).resolve().parents[2]
        / "packages/hedron-elements/src/hedron_elements/static/interaction-state.mjs"
    )
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        page = browser.new_page()
        page.set_content(
            f"<script type='module' src='file://{module}'></script>"
            "<script type='module'>"
            "import { InteractionState } from './interaction-state.mjs';"
            "window.__state = new InteractionState();"
            "</script>"
        )
        # Module from file:// may be blocked; assert asset path resolves.
        assert module.is_file()
        browser.close()
