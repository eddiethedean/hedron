"""Phase 0.19 SCRIPT-019: allowlisted Page progressive-enhancement scripts."""

from __future__ import annotations

import pytest

from hedron_core import Page, Text, render
from hedron_core.diagnostics import HedronError
from hedron_core.security import SafeUrl, UrlPurpose


def test_page_scripts_emit_defer_src_once() -> None:
    page = Page(
        Text("hi"),
        title="Scripts",
        scripts=[SafeUrl.parse("/assets/app.js", purpose=UrlPurpose.ASSET)],
        script_defer=True,
    )
    html = render(page).html
    assert html.count('<script src="/assets/app.js" defer></script>') == 1
    assert "hi" in html


def test_page_scripts_reject_non_asset_purpose() -> None:
    with pytest.raises(HedronError):
        Page(
            Text("x"),
            scripts=[SafeUrl.parse("/go", purpose=UrlPurpose.NAVIGATION)],
        )


def test_page_scripts_reject_external() -> None:
    with pytest.raises(HedronError):
        Page(
            Text("x"),
            scripts=[
                SafeUrl.parse(
                    "https://cdn.example/x.js",
                    purpose=UrlPurpose.ASSET,
                    allow_external=True,
                )
            ],
        )


def test_page_scripts_require_safeurl() -> None:
    with pytest.raises(TypeError, match="SafeUrl"):
        Page(Text("x"), scripts=["/assets/app.js"])  # type: ignore[list-item]
