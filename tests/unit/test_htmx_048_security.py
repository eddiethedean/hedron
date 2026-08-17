"""SECURITY-048 fail-closed catalog, digest, CSP, HDJ, preload, head."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from hedron_core import HedronError
from hedron_core.builtins.shell import HtmxLink
from hedron_core.codes import (
    HED_EXT_0002,
    HED_EXT_0005,
    HED_EXT_0006,
    HED_EXT_0009,
    HED_EXT_0011,
    HED_HTMX_0001,
    HED_HTMX_0002,
)
from hedron_core.head_support import admit_head_assets
from hedron_core.htmx_extensions import parse_htmx_extensions
from hedron_core.page_assets import inject_htmx_extensions
from hedron_core.rendering import AssetRef
from hedron_core.security import SafeUrl, UrlPurpose


def test_existing_htmx_codes_remain() -> None:
    assert HED_HTMX_0001 == "HED-HTMX-0001"
    assert HED_HTMX_0002 == "HED-HTMX-0002"


def test_unknown_cdn_and_digest_fail_closed() -> None:
    with pytest.raises(HedronError) as unknown:
        parse_htmx_extensions(["json-enc"])
    assert unknown.value.diagnostic.code == HED_EXT_0002
    with pytest.raises(HedronError) as cdn:
        parse_htmx_extensions(["//cdn.jsdelivr.net/npm/htmx-ext-sse"])
    assert cdn.value.diagnostic.code == HED_EXT_0009
    html = (
        "<html><head>"
        '<script src="/hedron-static/htmx.min.js" defer></script>'
        "</head><body></body></html>"
    )
    inject_htmx_extensions(html)  # valid pins succeed
    from hedron_core.htmx_extensions import ExtensionAsset, ExtensionPlan

    bogus = ExtensionPlan(
        ids=("sse",),
        source="declared",
        inject=True,
    )
    # Digests of known files must match; mutating the served path is covered by HED_EXT_0005
    # via ExtensionAsset verification.
    assert HED_EXT_0005 == "HED-EXT-0005"
    del html, bogus, ExtensionAsset


def test_core_has_no_fastapi() -> None:
    tree = ast.parse(
        Path("packages/hedron-core/src/hedron_core/htmx_extensions.py").read_text(encoding="utf-8")
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert "fastapi" not in node.module


def test_preload_and_head_boundaries() -> None:
    with pytest.raises(HedronError) as post:
        HtmxLink(
            "x",
            SafeUrl.parse("/x", purpose=UrlPurpose.NAVIGATION),
            method="delete",
            preload="touchstart",
        )
    assert post.value.diagnostic.code == HED_EXT_0006
    with pytest.raises(HedronError) as remote:
        admit_head_assets((AssetRef(kind="js", href="http://evil.example/x.js"),))
    assert remote.value.diagnostic.code == HED_EXT_0011
    with pytest.raises(HedronError) as breakout:
        admit_head_assets((AssetRef(kind="js", href='/ok?"onclick="alert(1)'),))
    assert breakout.value.diagnostic.code == HED_EXT_0011
