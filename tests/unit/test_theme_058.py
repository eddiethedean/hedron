"""THEME-058 evidence."""

from __future__ import annotations

from hedron import DesignSystem, Hedron
from hedron_core.registry import reset_registry_for_tests


def test_hedron_accepts_design_system_theme() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    design = DesignSystem.brand("theme-host", accent="#2f6fed")
    app = Hedron(
        title="t",
        security="development",
        session_secret="test-secret",
        explorer="off",
        theme=design,
    )
    assert app.hedron_theme == "theme-host"


def test_from_theme_to_theme_roundtrip() -> None:
    design = DesignSystem.brand("roundtrip", accent="#2563eb")
    theme = design.to_theme()
    restored = DesignSystem.from_theme(theme)
    assert restored.name == theme.name
    assert restored.to_theme().name == theme.name
    assert restored.to_theme().palette.get("brand.seed") == theme.palette.get("brand.seed")
