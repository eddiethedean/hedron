"""BROWSER-048 three-engine activation notes; unit-level cleanup."""

from __future__ import annotations

import os

import pytest
from tests.unit._helpers_048 import injected_page

from hedron_core.builtins import Text

ENGINES = ("chromium", "firefox", "webkit")


def test_page_scripts_are_defer_and_local() -> None:
    html, _ = injected_page(Text("ok"))
    assert 'src="/hedron-static/htmx.min.js" defer' in html or "htmx.min.js" in html
    assert "cdn.jsdelivr" not in html
    assert "unpkg.com" not in html


@pytest.mark.parametrize("engine", ENGINES)
def test_optional_three_engine_activation(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    html, _ = injected_page(Text(engine), title=engine)
    assert engine in html
    assert "head-support.js" in html
    assert "sse.js" in html
    assert "preload.js" not in html
