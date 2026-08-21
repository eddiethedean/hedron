"""BRAND-058 evidence."""

from __future__ import annotations

import pytest

from hedron import DesignSystem
from hedron_core.codes import HED_BRAND_0001
from hedron_core.diagnostics import HedronError


def test_brand_hex_seed_and_palette() -> None:
    design = DesignSystem.brand("acme", accent="#2f6fed")
    theme = design.to_theme()
    assert theme.palette["brand.seed"] == "#2f6fed"
    assert design.inputs["accent"] == "#2f6fed"


def test_brand_rejects_named_color() -> None:
    with pytest.raises(HedronError) as exc:
        DesignSystem.brand("bad", accent="red")
    assert exc.value.diagnostic.code == HED_BRAND_0001


def test_brand_adjusts_white_and_black_seeds() -> None:
    white = DesignSystem.brand("white-brand", accent="#ffffff")
    assert white.to_theme().palette["brand.seed"] == "#ffffff"
    assert white.adjustments
    assert any(item.get("code") == "HED-BRAND-0003" for item in white.adjustments)

    black = DesignSystem.brand("black-brand", accent="#000000")
    assert black.to_theme().palette["brand.seed"] == "#000000"
    # Black seeds may still adjust accent for on-accent contrast.
    assert black.adjustments or black.to_theme().tokens.get("color.accent")
