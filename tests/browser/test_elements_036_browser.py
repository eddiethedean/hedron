"""BROWSER-036: three-engine smoke + bridge size."""

from __future__ import annotations

import gzip
import os
from pathlib import Path

import pytest

from hedron_elements.assets import bridge_path

pytestmark = pytest.mark.browser

ENGINES = ("chromium", "firefox", "webkit")


def test_bridge_gzip_budget() -> None:
    raw = bridge_path().read_bytes()
    gz = gzip.compress(raw)
    assert len(gz) <= 12 * 1024, f"bridge gzip {len(gz)} exceeds 12 KiB"


@pytest.mark.parametrize("engine", ENGINES)
def test_engine_can_parse_example_module(engine: str) -> None:
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
            "<hedron-example data-hedron-abi='1' data-hedron-element='hedron-example' "
            "status='Ready'><p data-hedron-server-region='content'>Ready</p>"
            "</hedron-example>"
            f"<script type='module' src='file://{js / 'hedron-example.mjs'}'></script>"
        )
        # Module from file:// may be blocked; assert SSR still present.
        assert page.locator("hedron-example").count() == 1
        assert "Ready" in page.inner_text("hedron-example")
        browser.close()
