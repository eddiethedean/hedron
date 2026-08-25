"""Regression coverage for immutable phase 0.64 presentation contracts."""

from __future__ import annotations

import pytest

from hedron_core import (
    ResponsiveCondition,
    ScopedStyleRecipe,
    compile_scoped_styles,
    presentation_contract,
)


def test_presentation_contract_collections_are_immutable() -> None:
    states = ["invalid"]
    conditions = [ResponsiveCondition("direction", "rtl")]
    recipe = ScopedStyleRecipe(
        component="Card",
        part="body",
        declarations={"color": "red"},
        states=states,  # type: ignore[arg-type]
        conditions=conditions,  # type: ignore[arg-type]
    )
    bundle = compile_scoped_styles((recipe,))
    contract = presentation_contract()
    states.append("busy")
    conditions.clear()

    with pytest.raises(TypeError):
        recipe.declarations["color"] = "red; background: url(https://attacker.test/x)"  # type: ignore[index]
    with pytest.raises(TypeError):
        bundle.recipes[0]["declarations"]["color"] = "blue"  # type: ignore[index]
    with pytest.raises(TypeError):
        bundle.recipes[0]["conditions"][0]["kind"] = "bogus"  # type: ignore[index]
    for mapping, key in (
        (contract.tokens, "space.1"),
        (contract.breakpoints, "sm"),
        (contract.container_sizes, "sm"),
        (contract.motion, "standard"),
    ):
        with pytest.raises(TypeError):
            mapping[key] = "0px"  # type: ignore[index]

    assert recipe.states == ("invalid",)
    assert len(recipe.conditions) == 1
    assert presentation_contract().breakpoints["sm"] == "40rem"
