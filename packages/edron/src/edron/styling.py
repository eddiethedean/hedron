from __future__ import annotations

from hedron import Color, DesignSystem, StyleContext, StyleRecipe, Theme, ThemeSpec


def theme(
    name: str,
    *,
    accent: str | Color,
    base: Theme | None = None,
    density: object = "comfortable",
    geometry: object = "soft",
    typography: object = "system-sans",
    elevation: object = "subtle",
    motion: object = "standard",
    navigation: object = "default",
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
