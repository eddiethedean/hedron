"""BROWSER-037: bridge budget and SSR smoke for 0.37 primitives."""

from __future__ import annotations

import gzip
import os
from pathlib import Path

import pytest

from hedron_core.rendering import render
from hedron_elements.assets import bridge_path
from hedron_elements.disclosure import Disclosure
from hedron_elements.field_text import FieldText

pytestmark = pytest.mark.browser

ENGINES = ("chromium", "firefox", "webkit")


def test_bridge_gzip_budget() -> None:
    raw = bridge_path().read_bytes()
    gz = gzip.compress(raw)
    assert len(gz) <= 12 * 1024, f"bridge gzip {len(gz)} exceeds 12 KiB"


def test_037_ssr_markup_present_without_browser() -> None:
    html = render(FieldText("name", value="Ada")).html
    assert "hedron-field-text" in html
    assert "Ada" in html
    disc = render(Disclosure(summary="More")).html
    assert "hedron-disclosure" in disc
    assert "More" in disc


@pytest.mark.parametrize("engine", ENGINES)
def test_engine_can_parse_field_text_ssr(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    js = Path(__file__).resolve().parents[2] / "packages/hedron-elements/src/hedron_elements/static"
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        page = browser.new_page()
        page.set_content(
            "<hedron-field-text data-hedron-abi='1' data-hedron-element='hedron-field-text' "
            "name='email' value='a@b.c'>"
            "<input data-hedron-server-region='control' name='email' value='a@b.c'>"
            "</hedron-field-text>"
            f"<script type='module' src='file://{js / 'hedron-field-text.mjs'}'></script>"
        )
        assert page.locator("hedron-field-text").count() == 1
        assert "a@b.c" in page.inner_text("hedron-field-text")
        browser.close()
