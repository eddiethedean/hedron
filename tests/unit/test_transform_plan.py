import pytest

from hedron_core.diagnostics import HedronError
from hedron_data.plans import TransformPlan, TransformStep, apply_plan_in_memory, plan_from_query
from hedron_data.plugin import PLUGIN_META
from hedron_data.sources import DataQuery


def test_plan_from_query_and_apply() -> None:
    q = DataQuery(
        limit=5,
        sort=(("value", "desc"),),
        filters={"name": "a"},
        allowlisted_sort_fields=frozenset({"value"}),
        allowlisted_filter_fields=frozenset({"name"}),
    )
    plan = plan_from_query(q)
    assert plan.validated().steps
    rows = apply_plan_in_memory(
        [{"name": "a", "value": 1}, {"name": "a", "value": 3}, {"name": "b", "value": 2}],
        TransformPlan(
            steps=(
                TransformStep(op="filter", field="name", value="a"),
                TransformStep(op="sort", field="value", direction="desc"),
                TransformStep(op="sample", value=10),
            )
        ),
    )
    assert rows[0]["value"] == 3


def test_plan_encodes_offset_and_explorer_visibility() -> None:
    plan = plan_from_query(DataQuery(offset=50, limit=10))
    ops = [step.op for step in plan.steps]
    assert "offset" in ops
    assert "sample" in ops
    rows = apply_plan_in_memory(
        [{"id": i} for i in range(100)],
        plan,
    )
    assert rows == [{"id": i} for i in range(50, 60)]
    diag = plan.to_diagnostics()
    assert diag["steps"]
    assert "max_rows" in diag
    # Explorer advertises a data panel for TransformPlan visibility.
    assert PLUGIN_META.capabilities.explorer_panels is True
    assert PLUGIN_META.name == "hedron_data"


def test_plan_sorts_mixed_json_values_deterministically() -> None:
    rows = apply_plan_in_memory(
        [{"value": 1}, {"value": "2"}, {"value": None}],
        TransformPlan(steps=(TransformStep(op="sort", field="value", direction="asc"),)),
    )
    assert [row["value"] for row in rows] == [None, 1, "2"]


def test_plan_enforces_max_bytes() -> None:
    with pytest.raises(HedronError, match="max_bytes"):
        apply_plan_in_memory(
            [{"value": "x" * 100}],
            TransformPlan(max_bytes=10),
        )


def test_plan_budget_measures_projected_rows() -> None:
    rows = [{"keep": "ok", "discard": "x" * 1000}]
    plan = TransformPlan(
        steps=(TransformStep(op="project", field="keep"),),
        max_bytes=20,
    )

    assert apply_plan_in_memory(rows, plan) == [{"keep": "ok"}]
