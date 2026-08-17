"""HEAD-048 registered AssetRef merge and fragment deny."""

from __future__ import annotations

from types import MappingProxyType

import pytest
from tests.unit._helpers_048 import injected_page

from hedron_core import HedronError
from hedron_core.builtins import Page, Text
from hedron_core.codes import HED_EXT_0011
from hedron_core.head_support import (
    admit_head_assets,
    head_tags_from_assets,
    merge_registered_head,
    reject_invented_fragment_scripts,
)
from hedron_core.htmx_contract import is_local_path
from hedron_core.htmx_extensions import ExtensionPlan
from hedron_core.page_assets import inject_page_assets
from hedron_core.rendering import AssetRef, RenderMode, render


def test_admitted_local_assets_merge_when_head_support_declared() -> None:
    css = AssetRef(kind="css", href="/hedron-assets/app.css", attributes=MappingProxyType({}))
    html, _ = injected_page(Text("ok"), htmx_extensions={"head-support"})
    merged = merge_registered_head(html, (css,), enabled=True)
    assert 'href="/hedron-assets/app.css"' in merged
    again = merge_registered_head(merged, (css,), enabled=True)
    assert again.count("app.css") == 1


def test_remote_and_handler_assets_rejected() -> None:
    with pytest.raises(HedronError) as remote:
        admit_head_assets((AssetRef(kind="js", href="https://cdn.example/x.js"),))
    assert remote.value.diagnostic.code == HED_EXT_0011
    with pytest.raises(HedronError) as nonce:
        admit_head_assets(
            (AssetRef(kind="js", href="/x.js", attributes=MappingProxyType({"nonce": "abc"})),)
        )
    assert nonce.value.diagnostic.code == HED_EXT_0011


def test_breakout_and_traversal_hrefs_fail_closed() -> None:
    vectors = (
        '/ok?"onclick="alert(1)',
        '/"onclick="alert(1)',
        "/x><img src=x onerror=alert(1)>",
        "/../hedron-static/htmx.min.js",
    )
    for href in vectors:
        asset = AssetRef(kind="css" if ">" in href else "js", href=href)
        with pytest.raises(HedronError) as rejected:
            admit_head_assets((asset,))
        assert rejected.value.diagnostic.code == HED_EXT_0011
        with pytest.raises(HedronError) as tagged:
            head_tags_from_assets((asset,))
        assert tagged.value.diagnostic.code == HED_EXT_0011
    assert is_local_path('/ok?"onclick="alert(1)') is True
    assert is_local_path("/x><img src=x onerror=alert(1)>") is False


def test_inject_page_assets_does_not_emit_unescaped_duplicate() -> None:
    css = AssetRef(kind="css", href="/hedron-assets/app.css", attributes=MappingProxyType({}))
    plan = ExtensionPlan(ids=("head-support",), source="declared", inject=True)
    html = inject_page_assets(
        "<html><head></head><body></body></html>",
        RenderMode.PAGE,
        assets=(css,),
        include_default_styles=False,
        include_ui_modules=False,
        plan=plan,
    )
    assert html.count("/hedron-assets/app.css") == 1
    assert '<link rel="stylesheet" href="/hedron-assets/app.css">' in html
    again = merge_registered_head(html, (css,), enabled=True)
    assert again.count("/hedron-assets/app.css") == 1

    evil = AssetRef(kind="js", href='/ok?"onclick="alert(1)', attributes=MappingProxyType({}))
    with pytest.raises(HedronError) as injected:
        inject_page_assets(
            "<html><head></head><body></body></html>",
            RenderMode.PAGE,
            assets=(evil,),
            include_default_styles=False,
            include_ui_modules=False,
            plan=plan,
        )
    assert injected.value.diagnostic.code == HED_EXT_0011


def test_fragment_rejects_invented_scripts() -> None:
    html = render(Page(Text("frag"), title="f"), mode=RenderMode.FRAGMENT).html
    injected = inject_page_assets(html, RenderMode.FRAGMENT)
    assert "sse.js" not in injected
    with pytest.raises(HedronError) as invented:
        inject_page_assets('<div><script src="/evil.js"></script></div>', RenderMode.FRAGMENT)
    assert invented.value.diagnostic.code == HED_EXT_0011
    reject_invented_fragment_scripts(
        '<div><script src="/ok.js"></script></div>', admitted_hrefs=("/ok.js",)
    )


def test_head_support_absent_skips_merge() -> None:
    css = AssetRef(kind="css", href="/hedron-assets/app.css")
    html, _ = injected_page(Text("ok"), htmx_extensions={"sse"})
    assert merge_registered_head(html, (css,), enabled=False) == html
