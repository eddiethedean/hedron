"""EXPLAIN-058 evidence."""

from __future__ import annotations

from pydantic import BaseModel, Field

from hedron import DashboardWorkspace, DesignSystem, Text
from hedron_core.feature_explanation import EXPLANATION_SCHEMA, explain_feature


def test_explain_feature_schema() -> None:
    class Filters(BaseModel):
        region: str = "all"
        limit: int = Field(default=3, ge=1, le=10)

    dash = DashboardWorkspace(
        name="ops",
        path="/ops",
        title="Ops",
        filters=Filters,
        load=lambda filters: {"region": filters.region},
        panels={"summary": lambda data: Text(str(data))},
    )
    plan = explain_feature(dash)
    assert plan["schema"] == EXPLANATION_SCHEMA
    for key in (
        "logical_id",
        "kind",
        "surfaces",
        "routes",
        "effects",
        "security",
        "limitations",
        "source",
    ):
        assert key in plan
    assert plan["security"].get("redacted") is True


def test_design_system_explain_plan_schema() -> None:
    design = DesignSystem.brand("explain", accent="#2f6fed")
    plan = design.explain()
    payload = plan.to_dict()
    assert payload["schema"] == "hedron.design-system-plan/1"
    assert payload["logical_id"] == "design:explain"
    assert payload["digest"]
    assert "recipes" in payload
    assert "provenance" in payload
