"""Browser feature plan policy for a render session."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from hedron_core.alpine import (
    ALPINE_CORE_ASSET,
    HEDRON_BRIDGE_ASSET,
    AlpineFeatureDemand,
    BrowserFeaturePlan,
    browser_assets_for_features,
)


class BrowserPlanBuilder(Protocol):
    def build(self, demands: Iterable[AlpineFeatureDemand]) -> BrowserFeaturePlan: ...


class DefaultBrowserPlanBuilder:
    """Build the deterministic browser closure used by the default renderer."""

    def build(self, demands: Iterable[AlpineFeatureDemand]) -> BrowserFeaturePlan:
        collected = tuple(demands)
        return BrowserFeaturePlan.from_demands(
            collected,
            assets=(
                (ALPINE_CORE_ASSET, HEDRON_BRIDGE_ASSET)
                + browser_assets_for_features(demand.feature for demand in collected)
                if collected
                else ()
            ),
        )
