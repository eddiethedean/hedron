"""Phase 0.64 bounded presentation and opt-in extension contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

from hedron_core import (
    HEDRON_LIFECYCLE_SCHEMA,
    HedronLifecycleEvent,
    LifecycleFact,
    LifecyclePolicy,
    LifecycleState,
    PresentationError,
    ResponsiveCondition,
    ScopedStyleRecipe,
    compile_scoped_styles,
    component_presentation_manifest,
    default_theme,
    emit_theme_css,
    lifecycle_attributes,
    presentation_contract,
    presentation_tokens,
    transition_lifecycle,
)
from hedron_core.htmx_extensions import (
    compile_extension_plan,
    known_extensions,
    parse_htmx_extensions,
)
from hedron_core.page_assets import inject_htmx_extensions


def test_presentation_contract_is_closed_and_theme_aware() -> None:
    theme = default_theme().extend(
        "app",
        tokens={"type.body.size": "1.0625rem", "space.4": "1.125rem"},
    )

    contract = presentation_contract(theme).to_dict()

    assert contract["schema"] == "hedron.presentation-contract/1"
    assert contract["tokens"]["type.body.size"] == "1.0625rem"
    assert contract["tokens"]["space.4"] == "1.125rem"
    assert contract["breakpoints"] == {"lg": "72rem", "md": "56rem", "sm": "40rem", "xl": "90rem"}
    assert "reduced-motion" in contract["motion"] or "standard" in contract["motion"]
    assert "select" in contract["native_controls"]
    assert "--hedron-space-4: 1.125rem;" in emit_theme_css(theme)


def test_scoped_recipe_compilation_is_deterministic_and_logical() -> None:
    recipe = ScopedStyleRecipe(
        component="FormField",
        part="control",
        states=("invalid", "busy"),
        declarations={
            "border-color": "var(--hedron-color-danger)",
            "padding-inline": "var(--hedron-space-3)",
        },
        conditions=(
            ResponsiveCondition("container", "md"),
            ResponsiveCondition("direction", "rtl"),
        ),
    )

    first = compile_scoped_styles((recipe,))
    second = compile_scoped_styles((recipe,))
    reversed_conditions = ScopedStyleRecipe(
        component=recipe.component,
        part=recipe.part,
        states=recipe.states,
        declarations=recipe.declarations,
        conditions=tuple(reversed(recipe.conditions)),
    )
    reversed_bundle = compile_scoped_styles((reversed_conditions,))

    assert first.css == second.css
    assert first.digest == second.digest
    assert first.css == reversed_bundle.css
    assert "@container (min-width: 40rem)" in first.css
    assert '[dir="rtl"]' in first.css
    assert f'[dir="rtl"] .{recipe.class_name}' in first.css
    assert '[dir="rtl"] @container' not in first.css
    assert '[data-hedron-state~="invalid"]' in first.css
    assert '[data-hedron-state~="busy"]' in first.css
    assert "padding-inline" in first.css
    assert "padding-left" not in first.css

    direction_only = ScopedStyleRecipe(
        component="Card",
        part="body",
        declarations={"color": "red"},
        conditions=(ResponsiveCondition("direction", "rtl"),),
    )
    direction_css = compile_scoped_styles((direction_only,)).css
    assert f'@layer components {{\n[dir="rtl"] .{direction_only.class_name} {{' in direction_css
    assert '[dir="rtl"] @layer' not in direction_css


@pytest.mark.parametrize(
    "kwargs",
    [
        {"component": "Card;bad", "part": "body", "declarations": {}},
        {"component": "Card", "part": "body", "declarations": {"position": "fixed"}},
        {"component": "Card", "part": "body", "declarations": {"color": "url(https://evil)"}},
        {"component": "Card", "part": "body", "declarations": {"color": "red; } body {"}},
    ],
)
def test_scoped_recipe_rejects_unsafe_selector_or_css(kwargs: dict[str, object]) -> None:
    with pytest.raises(PresentationError):
        ScopedStyleRecipe(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("kind", ["bogus", "print", "media"])
def test_responsive_condition_rejects_unknown_kind(kind: str) -> None:
    with pytest.raises(PresentationError, match="unknown responsive condition kind"):
        ResponsiveCondition(kind, "x")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("kind", "value"),
    [
        ("viewport", "xxl"),
        ("container", "xxl"),
        ("direction", "auto"),
        ("writing-mode", "sideways-rl"),
        ("accessibility", "high-contrast"),
        ("viewport", []),
    ],
)
def test_responsive_condition_rejects_malformed_value(kind: str, value: object) -> None:
    with pytest.raises(PresentationError, match="unknown"):
        ResponsiveCondition(kind, value)  # type: ignore[arg-type]


def test_manifest_and_asset_are_portable() -> None:
    manifest = component_presentation_manifest()
    asset = next(item for item in known_extensions() if item.public_id == "hedron")
    asset_path = Path("packages/hedron/src/hedron/static/ext/hedron.js")

    assert manifest["parts_and_states"]["Card"]["parts"] == ["header", "body", "footer"]
    assert asset.path == "/hedron-static/ext/hedron.js"
    assert asset.digest.startswith("sha256-")
    assert asset_path.is_file()
    assert 'defineExtension("hedron"' in asset_path.read_text(encoding="utf-8")
    assert presentation_tokens(default_theme())["motion.standard"] == "150ms"


def test_lifecycle_contract_rejects_stale_responses_and_bounds_attributes() -> None:
    idle = LifecycleFact(LifecycleState.IDLE, generation=4, operation_id="op-4")
    pending = transition_lifecycle(
        idle, HedronLifecycleEvent.REQUEST, generation=5, operation_id="op-5"
    )
    stale = transition_lifecycle(pending, HedronLifecycleEvent.SUCCESS, generation=4)
    success = transition_lifecycle(pending, HedronLifecycleEvent.SUCCESS, generation=5)

    assert pending.state is LifecycleState.PENDING
    assert stale.state is LifecycleState.STALE
    assert success.state is LifecycleState.SUCCESS
    assert success.to_dict()["schema"] == HEDRON_LIFECYCLE_SCHEMA
    assert success.fingerprint
    assert (
        lifecycle_attributes(concurrency=LifecyclePolicy.REPLACE)["data-hedron-state-host"]
        == "true"
    )

    with pytest.raises(ValueError):
        lifecycle_attributes(concurrency="arbitrary")


def test_opt_in_extension_is_injected_after_htmx_core() -> None:
    html = (
        '<html><head><script src="/hedron-static/htmx.min.js"></script></head><body></body></html>'
    )
    plan = compile_extension_plan(declaration=parse_htmx_extensions(("hedron",)))

    rendered = inject_htmx_extensions(html, plan=plan)

    assert rendered.index("htmx.min.js") < rendered.index("/hedron-static/ext/hedron.js")
    assert 'hx-ext="hedron"' in rendered
