"""Regression coverage for phase 0.65 issues #712–#715."""

from __future__ import annotations

import pytest

from hedron_core import (
    AmbientCanvas,
    AmbientLayer,
    AppShell,
    AppShellChrome,
    PresentationError,
    ResponsiveCondition,
    ScopedStyleRecipe,
    compile_scoped_styles,
    component_presentation_manifest,
    default_theme,
    presentation_token_manifest,
    render,
)


def test_ambient_canvas_renders_ordered_inert_layers() -> None:
    html = render(
        AmbientCanvas(
            "content",
            layers=(
                AmbientLayer(pattern="grid", placement="fixed-canvas", order=2, scale="lg"),
                AmbientLayer(pattern="dots", tone="muted", placement="surface", order=1),
            ),
        )
    ).html

    assert html.count("data-hedron-ambient-layer=") == 2
    assert 'data-hedron-ambient-placement="fixed-canvas"' in html
    assert 'data-hedron-ambient-pattern="grid"' in html
    assert 'aria-hidden="true"' in html
    assert html.index("data-hedron-ambient-layer") < html.index("content")


def test_app_shell_chrome_is_finite_and_themeable() -> None:
    html = render(
        AppShell(
            body="body",
            chrome=AppShellChrome(
                preset="editorial",
                header_behavior="sticky",
                nav_behavior="flow",
                nav_offset="banner",
                content_inset="wide",
            ),
        )
    ).html

    assert 'data-hedron-shell-preset="editorial"' in html
    assert 'data-hedron-shell-header="sticky"' in html
    assert 'data-hedron-shell-nav="flow"' in html
    assert 'data-hedron-shell-nav-offset="banner"' in html
    with pytest.raises(ValueError):
        AppShellChrome(preset="compact", header_density="spacious")  # type: ignore[arg-type]


def test_presentation_manifest_has_consumption_and_overrides() -> None:
    theme = default_theme().extend("app", tokens={"space.4": "1.125rem"})
    manifest = presentation_token_manifest(theme)
    assert "space.4" in manifest["declared"]
    assert manifest["consumed"]["space.4"] == ["layout"]
    assert manifest["overridden"]["space.4"] == "1.125rem"
    assert manifest["unconsumed"] == []
    assert component_presentation_manifest()["presentation_tokens"]["schema"] == (
        "hedron.presentation-token-manifest/1"
    )


def test_max_and_range_conditions_compile_deterministically() -> None:
    recipe = ScopedStyleRecipe(
        component="Card",
        part="body",
        declarations={"padding-inline": "var(--hedron-space-4)"},
        conditions=(
            ResponsiveCondition.container_range("sm", "lg"),
            ResponsiveCondition("viewport", "max-lg"),
        ),
    )
    css = compile_scoped_styles((recipe,)).css
    assert "@media (max-width: 72rem)" in css
    assert "@container (min-width: 24rem) and (max-width: 56rem)" in css
    assert ResponsiveCondition.viewport_range("md", "lg").media_prefix() == (
        "@media (min-width: 56rem) and (max-width: 72rem)"
    )

    with pytest.raises(PresentationError, match="contradictory"):
        ScopedStyleRecipe(
            component="Card",
            part="body",
            declarations={"color": "red"},
            conditions=(
                ResponsiveCondition("viewport", "xl"),
                ResponsiveCondition("viewport-max", "md"),
            ),
        )


def test_public_style_recipes_reject_private_hooks_and_accept_named_motion() -> None:
    with pytest.raises(PresentationError, match="unknown public application style hook"):
        ScopedStyleRecipe(
            component="PrivateWidget",
            part="internal",
            declarations={"color": "red"},
        )
    recipe = ScopedStyleRecipe(
        component="Card",
        part="heading",
        declarations={"opacity": "1"},
        motion="crossfade",
    )
    css = compile_scoped_styles((recipe,)).css
    assert "transition-duration: var(--hedron-motion-crossfade);" in css
    assert "transition-timing-function: var(--hedron-motion-easing-standard);" in css
