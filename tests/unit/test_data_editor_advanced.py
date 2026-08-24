import pytest

from hedron_core.diagnostics import HedronError
from hedron_data.advanced import (
    MergeRegion,
    evaluate_formula,
    flatten_tree,
    pivot_rows,
    rows_to_tree,
)


def test_formula_and_injection() -> None:
    assert evaluate_formula("=[price]*[qty]", {"price": 2, "qty": 3}) == 6.0
    with pytest.raises(HedronError):
        evaluate_formula("=__import__('os').system('x')", {})
    with pytest.raises(HedronError):
        evaluate_formula("=[secret]", {"secret": 1}, allowed_names=frozenset({"price"}))
    with pytest.raises(HedronError):
        evaluate_formula("=1/0", {})
    with pytest.raises(HedronError, match="HED-DATA-0032"):
        evaluate_formula("=True+False", {})


def test_pivot_tree_merge() -> None:
    rows = [
        {"id": "1", "parent_id": None, "region": "east", "sku": "a", "amt": 2},
        {"id": "2", "parent_id": "1", "region": "east", "sku": "b", "amt": 3},
    ]
    piv = pivot_rows(rows, index="region", columns="sku", values="amt")
    assert piv
    tree = rows_to_tree(rows)
    flat = flatten_tree(tree)
    assert flat[0]["_tree_depth"] == 0
    MergeRegion(0, 0, 1, 1).validated()
    with pytest.raises(HedronError):
        rows_to_tree(
            [
                {"id": "a", "parent_id": "b"},
                {"id": "b", "parent_id": "a"},
            ]
        )


def test_pivot_validates_aggregate_and_grouping_keys() -> None:
    with pytest.raises(ValueError, match="Unsupported pivot aggregate"):
        pivot_rows([], index="i", columns="c", values="v", agg="bogus")
    with pytest.raises(ValueError, match="hashable"):
        pivot_rows(
            [{"i": ["a"], "c": "b", "v": 1}],
            index="i",
            columns="c",
            values="v",
        )


def test_pivot_preserves_typed_dimensions_counts_text_and_rejects_collisions() -> None:
    typed = pivot_rows(
        [
            {"i": "a", "c": True, "v": 10},
            {"i": "a", "c": 1, "v": 100},
        ],
        index="i",
        columns="c",
        values="v",
    )
    assert typed[0]["True"] == 10.0
    assert typed[0]["1"] == 100.0

    counted = pivot_rows(
        [{"i": "a", "c": "x", "v": "label"}],
        index="i",
        columns="c",
        values="v",
        agg="count",
    )
    assert counted == [{"i": "a", "x": 1}]

    with pytest.raises(ValueError, match="collide"):
        pivot_rows(
            [{"i": 1, "c": 1, "v": 5}, {"i": 1, "c": "1", "v": 7}],
            index="i",
            columns="c",
            values="v",
        )


def test_tree_rejects_unreachable_nodes() -> None:
    with pytest.raises(HedronError, match="HED-DATA-0033"):
        rows_to_tree([{"id": "0", "parent_id": 0}, {"id": "1", "parent_id": None}])
