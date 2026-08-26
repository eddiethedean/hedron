from __future__ import annotations

from typing import Any

from hedron import Color, DesignSystem, StyleContext, StyleRecipe, Theme, ThemeSpec


def theme(
    name: str,
    *,
    accent: str | Color,
    base: Theme | None = None,
    density: Any = "comfortable",
    geometry: Any = "soft",
    typography: Any = "system-sans",
    elevation: Any = "subtle",
    motion: Any = "standard",
    navigation: Any = "default",
    recipes: tuple[StyleRecipe, ...] = (),
) -> DesignSystem:
    return DesignSystem.brand(
        name,
        accent=accent,
        base=base,
        density=density,
        geometry=geometry,
        typography=typography,
        elevation=elevation,
        motion=motion,
        navigation=navigation,
        recipes=recipes,
    )


__all__ = ["Color", "DesignSystem", "StyleContext", "StyleRecipe", "Theme", "ThemeSpec", "theme"]
