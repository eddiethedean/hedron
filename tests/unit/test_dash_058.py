"""DASH-058 evidence."""

from __future__ import annotations

from pydantic import BaseModel, Field

from hedron import DashboardWorkspace, Text
from hedron_core.bundles import FeatureBundle


def test_dashboard_workspace_to_bundle() -> None:
    class Filters(BaseModel):
        region: str = "all"
        limit: int = Field(default=5, ge=1, le=50)

    dash = DashboardWorkspace(
        name="sales",
        path="/sales",
        title="Sales",
        filters=Filters,
        load=lambda filters: {"region": filters.region, "total": filters.limit},
        panels={"summary": lambda data: Text(str(data))},
        history="replace",
    )
    bundle = dash.to_bundle()
    assert isinstance(bundle, FeatureBundle)
    assert bundle.logical_id
