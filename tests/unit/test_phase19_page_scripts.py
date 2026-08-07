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


def test_page_scripts_reject_path_traversal() -> None:
    with pytest.raises(HedronError, match="normalized|\\.\\.|without"):
        Page(
            Text("x"),
            scripts=[SafeUrl.parse("/assets/../secret.js", purpose=UrlPurpose.ASSET)],
        )


@pytest.mark.parametrize(
    "path",
    [
        "/assets/%2e%2e/secret.js",
        "/assets/%2E%2E/secret.js",
        "/assets/app.js%2e%2e/x",
        "/%2e%2e/secret.js",
    ],
)
def test_page_scripts_reject_percent_encoded_traversal(path: str) -> None:
    with pytest.raises(HedronError):
        Page(
            Text("x"),
            scripts=[SafeUrl.parse(path, purpose=UrlPurpose.ASSET)],
        )


def test_safeurl_asset_rejects_percent_encoded_traversal() -> None:
    with pytest.raises(HedronError):
        SafeUrl.parse("/assets/%2e%2e/secret.js", purpose=UrlPurpose.ASSET)


def test_page_scripts_async_emits_async_attr() -> None:
    page = Page(
        Text("hi"),
        scripts=[SafeUrl.parse("/assets/app.js", purpose=UrlPurpose.ASSET)],
        script_defer=False,
        script_async=True,
    )
    html = render(page).html
    assert '<script src="/assets/app.js" async></script>' in html
    assert "defer" not in html.split("app.js")[1].split(">")[0]


def test_page_scripts_reject_async_and_defer() -> None:
    with pytest.raises(HedronError, match="async and defer"):
        Page(
            Text("x"),
            scripts=[SafeUrl.parse("/assets/app.js", purpose=UrlPurpose.ASSET)],
            script_defer=True,
            script_async=True,
        )
