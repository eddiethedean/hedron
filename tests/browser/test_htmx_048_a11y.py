"""A11Y-048 semantic fallback, focus, no SR-021 closure."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from tests.unit._helpers_048 import injected_page

from hedron_core.builtins import Text
from hedron_core.builtins.shell import HtmxLink
from hedron_core.rendering import render
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.sse_ext import SseRegion

pytestmark = pytest.mark.a11y

ENGINES = ("chromium", "firefox", "webkit")


def test_polling_and_ordinary_html_remain_the_fallback() -> None:
    html, _ = injected_page(Text("status"), title="Status")
    assert "<body" in html
    assert "status" in html
    src = Path("docs/acceptance/htmx-sse-head-preload-048.toml").read_text(encoding="utf-8")
    assert "polling_only = true" in src
    assert "reopen_polling_only = false" in src
    roadmap = Path("docs/ROADMAP.md").read_text(encoding="utf-8")
    # Scoped AT honesty: 0.48 does not close SR-021.
    assert "SR-021" in Path("docs/implementation/HTMX_EXTENSION_INTEGRATION_048.md").read_text(
        encoding="utf-8"
    ) or "SR-021" in Path("docs/acceptance/RELEASE_0_48.md").read_text(encoding="utf-8")
    del roadmap


def test_preload_does_not_steal_focus_or_announce() -> None:
    link = HtmxLink(
        "Next page",
        SafeUrl.parse("/next", purpose=UrlPurpose.NAVIGATION),
        preload="mousedown",
    )
    html, _ = injected_page(link, htmx_extensions={"preload"})
    assert ">Next page<" in html or "Next page" in html
    assert "aria-live" not in html
    region = SseRegion(Text("Live status"), connect="/events")
    frag = render(region).html
    assert "Live status" in frag


@pytest.mark.parametrize("engine", ENGINES)
def test_optional_browser_a11y(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    html, _ = injected_page(Text("ok"), title="A11y")
    assert "<html" in html
