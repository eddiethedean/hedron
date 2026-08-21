"""CSP-057 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from hedron_core import FormGrid, Inline, Stack, Text
from hedron_core.diagnostics import HedronError
from hedron_core.rendering import RenderContext, RenderMode, render


def test_csp_057_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.57.toml").read_text(encoding="utf-8"))
    assert gate["evidence"][1]["id"] == "CSP-057"
    assert gate["evidence"][1]["state"] == "Verified"


def test_layout_gaps_emit_data_markers_without_inline_styles() -> None:
    ctx = RenderContext.standalone()
    for node in (
        Stack(Text("a"), gap="1rem"),
        Inline(Text("a"), gap="0.5rem"),
        FormGrid(Text("a"), gap="md"),
    ):
        html = render(node, context=ctx, mode=RenderMode.FRAGMENT).html
        assert "style=" not in html or "--hedron-gap" not in html
        assert "data-hedron-gap=" in html


def test_invalid_gap_fails_diagnostically() -> None:
    with pytest.raises(HedronError):
        Stack(Text("x"), gap="calc(100vh - 2rem)")
