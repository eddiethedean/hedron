"""COMPAT-048 / REGRESS-048 upgrade fixtures from Verified 0.47."""

from __future__ import annotations

from pathlib import Path

from tests.unit._helpers_048 import injected_page

from hedron_core.builtins import Page, Text
from hedron_core.htmx_contract import safe_hx_swap
from hedron_core.page_assets import inject_page_assets
from hedron_core.rendering import RenderMode, render


def test_fixture_1_unset_page_keeps_047_pair() -> None:
    html, result = injected_page(Text("unchanged"))
    assert "sse.js" in html
    assert "head-support.js" in html
    assert "preload.js" not in html
    assert any(d.code == "HED-EXT-0001" for d in result.diagnostics)


def test_fixture_2_opt_out_zero_bytes() -> None:
    html, _ = injected_page(Text("opt"), htmx_extensions=())
    assert "ext/" not in html or "ext/sse.js" not in html
    assert "sse.js" not in html


def test_fixture_3_sse_only_declaration() -> None:
    html, _ = injected_page(Text("sse"), htmx_extensions={"sse"})
    assert "sse.js" in html
    assert "head-support.js" not in html


def test_existing_swaps_and_polling_unchanged() -> None:
    assert safe_hx_swap("innerHTML")
    assert safe_hx_swap("outerHTML")
    assert not safe_hx_swap("morph")
    src = Path("docs/acceptance/htmx-sse-head-preload-048.toml").read_text(encoding="utf-8")
    assert "polling_only = true" in src
    assert "reopen_polling_only = false" in src


def test_fragment_still_skips_extension_assets() -> None:
    result = render(Page(Text("frag"), title="f"), mode=RenderMode.FRAGMENT)
    out = inject_page_assets(result.html, RenderMode.FRAGMENT)
    assert "sse.js" not in out
    assert "head-support.js" not in out
    assert all(d.code != "HED-EXT-0001" for d in result.diagnostics)
