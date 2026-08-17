"""Notebook FeatureBundle inspection. Localhost-only; not a workflow store."""

from __future__ import annotations

from hedron_core.bundles import FeatureBundle, included_bundles

__all__ = ["inspect_features"]


def inspect_features(*, app_id: str | None = None) -> tuple[FeatureBundle, ...]:
    return included_bundles(app_id=app_id)
