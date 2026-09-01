"""Meta-tests that keep assertions and retirement policy honest."""

from __future__ import annotations

import ast
from pathlib import Path


def test_suite_contains_no_assert_or_true_escape_hatches() -> None:
    root = Path(__file__).parents[1]
    violations: list[str] = []
    for path in sorted(root.rglob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assert) or not isinstance(node.test, ast.BoolOp):
                continue
            if not isinstance(node.test.op, ast.Or):
                continue
            if any(
                isinstance(value, ast.Constant) and value.value is True
                for value in node.test.values
            ):
                violations.append(f"{path.relative_to(root)}:{node.lineno}")
    assert violations == [], "vacuous `assert ... or True` expressions:\n" + "\n".join(violations)


def test_retirement_inventory_has_no_duplicates_and_is_sorted() -> None:
    inventory = Path(__file__).parents[1] / "legacy_0x_inventory.txt"
    nodeids = [
        line.strip()
        for line in inventory.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert len(nodeids) == len(set(nodeids))
    assert nodeids == sorted(nodeids)
