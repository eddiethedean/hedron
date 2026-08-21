"""RECIPE-058 evidence."""

from __future__ import annotations

import pytest

from hedron import Button, DesignSystem, StyleRecipe
from hedron_core.codes import HED_RECIPE_0001
from hedron_core.design_system import BUILTIN_RECIPES, FEATURE_ROLES
from hedron_core.diagnostics import HedronError


def test_builtin_recipes_and_feature_roles() -> None:
    assert "primary_action" in BUILTIN_RECIPES
    assert FEATURE_ROLES["form.primary_action"] == "primary_action"


def test_style_recipe_control_apply_and_explicit_wins() -> None:
    design = DesignSystem.brand("recipe", accent="#2f6fed")
    styled = design.apply("primary_action", Button("Save"))
    assert styled.props.emphasis == "primary" or styled.props.appearance == "solid"

    explicit = design.apply("primary_action", Button("Save", emphasis="secondary"))
    assert explicit.props.emphasis == "secondary"

    custom = StyleRecipe.control("my_btn", appearance="outline", size="sm")
    with_custom = design.with_recipes(custom)
    applied = with_custom.apply("my_btn", Button("Go"))
    assert applied.props.appearance == "outline"
    assert applied.props.size == "sm"


def test_unknown_recipe_fails() -> None:
    design = DesignSystem.brand("missing", accent="#2f6fed")
    with pytest.raises(HedronError) as exc:
        design.apply("does-not-exist", Button("x"))
    assert exc.value.diagnostic.code == HED_RECIPE_0001
