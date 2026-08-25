"""Phase 0.60 theme-platform, accessibility, and compatibility evidence."""

from __future__ import annotations

import pytest

from hedron import (
    Brand,
    Button,
    Color,
    ConnectorFlow,
    DesignSystem,
    RecipeFamily,
    ScrollRegion,
    StyleContext,
    StyleRecipe,
    ThemeBuilder,
    ThemePicker,
    ThemePreference,
    ThemeSpec,
    ToastHost,
    conformance_report,
    diff_theme_specs,
    explain_theme_spec,
    load_theme_package,
    package_theme,
    register_recipe_family,
    render,
    theme_boot_asset,
    theme_markers,
    validate_theme_spec,
)
from hedron_core import HedronError
from hedron_core.page_assets import inject_page_assets
from hedron_core.rendering import RenderMode
from hedron_core.theme import Theme


def _valid_tokens() -> dict[str, str]:
    return {
        "color.bg": "#ffffff",
        "color.surface": "#ffffff",
        "color.fg": "#111827",
        "color.muted": "#4b5563",
        "color.border": "#d1d5db",
        "color.accent": "#1d4ed8",
        "color.focus": "#1d4ed8",
        "color.danger": "#b91c1c",
        "font.family": "system-ui",
        "font.size": "1rem",
        "space.unit": "0.25rem",
        "motion.duration": "160ms",
        "focus.ring": "3px solid #1d4ed8",
    }


def test_absolute_modern_colors_have_deterministic_srgb_fallbacks() -> None:
    oklch = Color.parse("oklch(65% 0.18 275)")
    rgb = Color.parse("rgb(37 99 235)")
    rgb_percent = Color.parse("rgb(50% 0% 100%)")
    lab = Color.parse("lab(65% 20 30)")

    assert oklch.space == "oklch"
    assert oklch.to_css(fallback=False).startswith("oklch(")
    assert oklch.to_hex().startswith("#")
    assert rgb.to_hex() == "#2563eb"
    assert rgb_percent.to_hex() == "#8000ff"
    assert Color.rgb(37 / 255, 99 / 255, 235 / 255).to_hex() == "#2563eb"
    assert lab.coords[0] == 65.0
    with pytest.raises(ValueError, match="unsafe absolute color"):
        Color.parse("url(https://example.test/color.svg)")

    assert Color.hsl(220, 0.7, 0.5).to_hex().startswith("#")
    assert Color.hwb(220, 0.1, 0.1).gamut_map().space == "srgb"
    assert Color.lab(65, 20, 30).to_hex().startswith("#")
    assert Color.lch(65, 30, 275).to_hex().startswith("#")
    assert Color.oklab(0.65, 0.1, -0.1).to_hex().startswith("#")


def test_brand_accepts_absolute_color_and_records_provenance() -> None:
    design = DesignSystem.brand("modern", accent=Color.parse("oklch(55% 0.12 260)"))

    assert design.inputs["accent_space"] == "oklch"
    assert design.inputs["accent_requested"].startswith("oklch(")
    assert design.to_theme().palette["brand.seed"].startswith("#")


def test_theme_builder_supports_contract_authoring_ladder() -> None:
    spec = (
        ThemeBuilder("acme")
        .brand(accent=Color.oklch(0.68, 0.18, 275))
        .groups(density="comfortable", geometry="soft", typography="system-sans")
        .tokens({"color.info": "#2563eb"})
        .accessibility_mode("more-contrast", {"color.focus": "CanvasText"})
        .recipe("button", {"appearance": "raised"})
        .build_spec()
    )

    assert spec.groups["density"] == "comfortable"
    assert spec.recipes["button"]["appearance"] == "raised"
    assert spec.accessibility_modes["more-contrast"]["color.focus"] == "CanvasText"
    assert spec.metadata["brand"]["space"] == "oklch"
    assert ThemeSpec.from_dict(spec.to_dict()).fingerprint == spec.fingerprint


def test_theme_spec_aliases_patches_and_accessibility_bridge_are_immutable() -> None:
    spec = (
        ThemeBuilder("phase060")
        .token("color.bg", "#ffffff")
        .token("color.fg", "#111827")
        .token("color.focus", "#1d4ed8")
        .alias("color.surface", "color.bg")
        .accessibility("forced-colors", **{"color.focus": "Highlight"})
        .build()
    )
    patched = spec.patch(tokens={"font.family": "system-ui"})
    direct = ThemeSpec(
        "direct",
        tokens={"base": "#fff"},
        aliases={"surface": "@base"},
    )

    assert spec.resolve_token("color.surface") == "#ffffff"
    assert patched.resolve_token("font.family") == "system-ui"
    assert direct.resolve_token("surface") == "#fff"
    assert "forced-colors" in spec.accessibility_modes
    assert spec.fingerprint != spec.patch().fingerprint
    with pytest.raises(TypeError):
        spec.tokens["new"] = "#000000"  # type: ignore[index]


@pytest.mark.parametrize(
    "value",
    [
        "red; background: url(https://attacker.test/x)",
        "red; } body { color: red",
        "url(https://attacker.test/x)",
    ],
)
def test_theme_mode_values_cannot_inject_css(value: str) -> None:
    with pytest.raises(ValueError):
        ThemeSpec("unsafe", tokens=_valid_tokens(), modes={"dark": {"color.fg": value}})
    with pytest.raises(HedronError):
        Theme(name="unsafe", tokens=_valid_tokens(), modes={"dark": {"color.fg": value}})


def test_theme_validation_and_package_are_reproducible() -> None:
    spec = ThemeSpec(
        "packaged",
        tokens=_valid_tokens(),
        accessibility_modes={"forced-colors": {"color.focus": "Highlight"}},
    )

    report = validate_theme_spec(spec, profile="complete")
    first = package_theme(spec, profile="complete", licenses=("MIT",))
    second = package_theme(spec, profile="complete", licenses=("MIT",))

    assert report.ok
    assert first.archive == second.archive
    assert first.fingerprint == spec.fingerprint
    assert first.manifest["validation"] == report.digest
    loaded = load_theme_package(first)
    assert loaded.fingerprint == spec.fingerprint
    assert conformance_report(loaded, profile="complete")["ok"]


def test_recipe_family_and_style_context_preserve_bounded_precedence() -> None:
    family = RecipeFamily(
        "phase060-control",
        fields={"appearance": ("plain", "raised")},
        components=("Button",),
    )
    register_recipe_family(family)
    recipe = StyleRecipe(
        "workflow-panel",
        family="phase060-control",
        values={"appearance": "raised"},
    )

    assert recipe.family == "phase060-control"
    assert (
        StyleContext(recipes={"phase060-control": "workflow-panel"}).resolve(
            "phase060-control", explicit="explicit"
        )
        == "explicit"
    )
    design = DesignSystem.from_theme(DesignSystem.brand("recipe", accent="#2563eb").to_theme())
    styled = design.apply(recipe, Button("Run"))
    assert styled.props.appearance == "raised"


def test_phase060_components_emit_only_bounded_contract_markers() -> None:
    brand = render(Brand("Hedron", subtitle="Framework", subtitle_overflow="break")).html
    toast = render(
        ToastHost(placement="bottom-start", position="sticky", width="field", gap="md")
    ).html
    flow = render(ConnectorFlow(background="dots", overflow="scroll", min_size="lg")).html
    scroll = render(
        ScrollRegion("log", axis="both", size="sm", affordance="always", label="Events")
    ).html

    assert 'data-hedron-brand-subtitle-overflow="break"' in brand
    assert 'data-hedron-toast-placement="bottom-start"' in toast
    assert 'data-hedron-toast-position="sticky"' in toast
    assert 'data-hedron-connector-background="dots"' in flow
    assert 'data-hedron-scroll-axis="both"' in scroll
    assert 'role="region"' in scroll
    assert 'aria-label="Events"' in scroll


def test_theme_preference_is_allowlisted_and_server_first() -> None:
    preference = ThemePreference(theme="aurora", color_mode="dark")
    markers = theme_markers(preference)
    boot = theme_boot_asset(("default", "aurora"))
    picker = render(ThemePicker(selected=preference)).html

    assert markers["data-hedron-theme"] == "aurora"
    assert "localStorage.getItem" in boot
    assert "hedron-color-mode" in boot
    assert "colorScheme" in boot
    assert "aurora" in picker
    assert "color_mode" in picker


def test_theme_services_are_deterministic_and_explain_provenance() -> None:
    base = ThemeBuilder("services").token("color.bg", "#fff").token("color.fg", "#111")
    left = base.token("color.focus", "#06f").build()
    right = (
        ThemeBuilder.from_spec(left)
        .token("space.unit", "0.25rem")
        .provenance(source="test", reason="phase-060")
        .build()
    )

    delta = diff_theme_specs(left, right)
    explanation = explain_theme_spec(right)
    assert delta["tokens"]["added"] == {"space.unit": "0.25rem"}
    assert explanation["provenance"][-1]["source"] == "test"


def test_page_assets_can_emit_server_first_theme_preference_markers() -> None:
    html = inject_page_assets(
        "<html><head></head><body></body></html>",
        RenderMode.PAGE,
        include_default_styles=False,
        include_ui_modules=False,
        theme_preference=ThemePreference(theme="aurora", color_mode="dark"),
    )

    assert 'data-hedron-theme="aurora"' in html
    assert 'data-hedron-color-mode="dark"' in html
    assert 'data-theme="dark"' in html
