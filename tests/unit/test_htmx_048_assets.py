"""ASSET-048 demand-driven pins, order, opt-out, CSP, mount."""

from __future__ import annotations

from pathlib import Path

from tests.unit._helpers_048 import injected_page

from hedron_core.builtins import Text
from hedron_core.htmx_extensions import known_extensions
from hedron_core.page_assets import inject_htmx_extensions


def test_compat_default_is_after_core_and_skips_preload() -> None:
    html, _ = injected_page(Text("ok"))
    core = html.index("htmx.min.js")
    head = html.index("/hedron-static/ext/head-support.js")
    sse = html.index("/hedron-static/ext/sse.js")
    assert core < head < sse
    assert "preload.js" not in html
    assert html.count("head-support.js") == 1
    assert html.count("sse.js") == 1


def test_declared_preload_injects_only_preload() -> None:
    html, result = injected_page(Text("ok"), htmx_extensions={"preload"})
    assert "preload.js" in html
    assert "sse.js" not in html
    assert "head-support.js" not in html
    assert result.htmx_plan.ids == ("preload",)  # type: ignore[union-attr]


def test_dual_static_trees_match_digests() -> None:
    import hashlib

    for ext in known_extensions():
        rel = ext.path.removeprefix("/hedron-static/")
        for root in (
            Path("packages/hedron-core/src/hedron_core/static"),
            Path("packages/hedron/src/hedron/static"),
        ):
            data = (root / rel).read_bytes()
            assert f"sha256-{hashlib.sha256(data).hexdigest()}" == ext.digest
            assert ext.csp == "script-src 'self'"
            assert not ext.deferred


def test_none_plan_keeps_compat_default() -> None:
    html = (
        "<!DOCTYPE html><html><head>"
        '<script src="/hedron-static/htmx.min.js" defer></script>'
        "</head><body>ok</body></html>"
    )
    out = inject_htmx_extensions(html)
    assert "head-support.js" in out
    assert "sse.js" in out
    assert "preload.js" not in out
    assert 'hx-ext="head-support,sse"' in out
