from hedron_data.plans import TransformPlan, TransformStep, apply_plan_in_memory, plan_from_query
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
