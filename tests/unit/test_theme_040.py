"""THEME-040 element style/token contracts."""

from __future__ import annotations

import pytest

from hedron_core.theme import (
    FORCED_COLOR_TOKENS,
    PRINT_SAFE_TOKENS,
    theme_element_compatibility,
    validate_element_style_contract,
)


def test_forced_color_and_print_token_sets() -> None:
    assert "color.fg" in FORCED_COLOR_TOKENS
    assert "color.bg" in PRINT_SAFE_TOKENS


def test_validate_element_style_contract_accepts_aligned_metadata() -> None:
    validate_element_style_contract(
        {"parts": "label", "slots": "default", "tokens": "--demo-fg"},
        parts=("label",),
        slots={"default": "content"},
        tokens=("--demo-fg",),
    )


def test_validate_element_style_contract_rejects_undeclared_part() -> None:
    with pytest.raises(ValueError, match="undeclared parts"):
        validate_element_style_contract(
            {"parts": "missing"},
            parts=("label",),
            slots={},
            tokens=(),
        )


def test_theme_element_compatibility_lists_missing_tokens() -> None:
    missing = theme_element_compatibility(
        {"color.fg": "#000", "color.bg": "#fff"},
        ("color.fg", "--demo-fg"),
    )
    assert missing == ["--demo-fg"]
