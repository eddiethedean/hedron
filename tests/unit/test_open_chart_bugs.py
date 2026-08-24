from hedron_charts.compile import apply_transforms
from hedron_charts.limits import redact_rows
from hedron_charts.spec import TransformDef


def test_chart_sort_handles_mixed_json_cell_types() -> None:
    rows = apply_transforms(
        [{"x": 1}, {"x": "a"}, {"x": None}],
        [TransformDef(op="sort", field="x")],
    )
    assert [row["x"] for row in rows] == [None, 1, "a"]


def test_chart_count_distinct_handles_unhashable_cells() -> None:
    rows = apply_transforms(
        [{"group": "a", "x": {"k": 1}}, {"group": "a", "x": {"k": 1}}],
        [
            TransformDef(
                op="aggregate",
                params={
                    "groupby": ["group"],
                    "metrics": [{"op": "count_distinct", "field": "x", "as": "distinct"}],
                },
            )
        ],
    )
    assert rows == [{"group": "a", "distinct": 1}]


def test_chart_redaction_recurses_without_secret_substring_false_positives() -> None:
    rows = redact_rows(
        [
            {
                "secretary": "Ada",
                "meta": {"token": "hidden", "nested": [{"password": "hidden"}]},
            }
        ]
    )
    assert rows == [
        {
            "secretary": "Ada",
            "meta": {"token": "***", "nested": [{"password": "***"}]},
        }
    ]
