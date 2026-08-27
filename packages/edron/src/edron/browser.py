"""Edron's thin browser contract over the native Hedron planner."""

from __future__ import annotations

from collections.abc import Sequence

from hedron import (
    AlpineAttrs,
    AlpineDirective,
    AlpineExpression,
    AlpineFeatureDemand,
    AlpineMaturity,
    BrowserFeaturePlan,
    BrowserPlanClosure,
)

HEDRON_BROWSER_TRAIN = "0.67.0"
HEDRON_BROWSER_REQUIREMENT = ">=0.67.0,<2.0"
HEDRON_BROWSER_FORWARD_TARGET = "1.0.0"


def feature_demand(
    feature: str,
    source: str = "edron",
    *,
    maturity: AlpineMaturity = AlpineMaturity.SUPPORTED,
) -> AlpineFeatureDemand:
    """Declare one browser-local feature for the native document planner."""
    return AlpineFeatureDemand(feature, source, maturity)


def browser_plan(
    demands: Sequence[AlpineFeatureDemand] = (),
    *,
    assets: Sequence[str] = (),
) -> BrowserFeaturePlan:
    """Build the native demand-driven plan; empty input remains feature-off."""
    return BrowserFeaturePlan.from_demands(demands, assets=assets)


def browser_closure(
    initial: BrowserFeaturePlan | None = None,
    *,
    fragments: Sequence[tuple[str, BrowserFeaturePlan]] = (),
) -> BrowserPlanClosure:
    """Build the native page/fragment browser closure before serving a page."""
    closure = BrowserPlanClosure(initial=initial or BrowserFeaturePlan())
    for name, plan in fragments:
        closure = closure.add_fragment(name, plan)
    return closure


__all__ = [
    "AlpineAttrs",
    "AlpineDirective",
    "AlpineExpression",
    "AlpineFeatureDemand",
    "AlpineMaturity",
    "BrowserFeaturePlan",
    "BrowserPlanClosure",
    "HEDRON_BROWSER_FORWARD_TARGET",
    "HEDRON_BROWSER_REQUIREMENT",
    "HEDRON_BROWSER_TRAIN",
    "browser_closure",
    "browser_plan",
    "feature_demand",
]
