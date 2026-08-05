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
