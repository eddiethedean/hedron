"""Advanced DataEditor helpers: formulas, merges, pivots, trees, formats."""

from __future__ import annotations

import ast
import math
import operator
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from hedron_core.diagnostics import error
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "CellFormat",
    "MergeRegion",
    "TreeNode",
    "evaluate_formula",
    "flatten_tree",
    "pivot_rows",
    "rows_to_tree",
]

_COLUMN_REF = re.compile(r"\[([A-Za-z_][A-Za-z0-9_]*)\]")
_BIN_OPS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: lambda a, b: a / b,
}
_UNARY_OPS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


@dataclass(frozen=True, slots=True)
class MergeRegion:
    start_row: int
    start_col: int
    end_row: int
    end_col: int

    def validated(self) -> MergeRegion:
        if (
            self.start_row < 0
            or self.start_col < 0
            or self.end_row < self.start_row
            or self.end_col < self.start_col
        ):
            raise ValueError("Invalid merge region bounds")
        return self


@dataclass(frozen=True, slots=True)
class CellFormat:
    bold: bool = False
    italic: bool = False
    number_format: str | None = None
    fill: str | None = None


@dataclass(frozen=True, slots=True)
class TreeNode:
    key: str
    data: Mapping[str, JsonValue]
    children: tuple[TreeNode, ...] = ()


def evaluate_formula(
    expr: str,
    row: Mapping[str, JsonValue],
    *,
    allowed_names: frozenset[str] | None = None,
) -> JsonValue:
    """Evaluate a constrained numeric formula with ``[field]`` column refs."""
    raw_expr: Any = expr
    if not isinstance(raw_expr, str) or not raw_expr.strip():
        raise error(
            "HED-DATA-0030",
            title="Empty formula",
            explanation="Formulas must be non-empty strings.",
            remediation="Provide a formula such as '=[price]*[qty]'.",
        )
    text = raw_expr.strip()
    if text.startswith("="):
        text = text[1:]
    refs = _COLUMN_REF.findall(text)
    if allowed_names is not None:
        for name in refs:
            if name not in allowed_names:
                raise error(
                    "HED-DATA-0031",
                    title="Formula references disallowed field",
                    explanation=f"Field {name!r} is not in the allowlist.",
                    remediation="Restrict formulas to authorized columns.",
                )

    def _cell_float(name: str) -> float:
        raw = row.get(name)
        if isinstance(raw, bool) or raw is None:
            raise error(
                "HED-DATA-0032",
                title="Non-numeric formula cell",
                explanation=f"Column {name!r} is {raw!r}; formulas require numbers.",
                remediation="Use numeric cells, or omit non-numeric columns from the formula.",
            )
        if isinstance(raw, (int, float)):
            numeric = float(raw)
            if not math.isfinite(numeric):
                raise error(
                    "HED-DATA-0032",
                    title="Non-finite formula cell",
                    explanation=f"Column {name!r} must contain a finite number.",
                    remediation="Replace NaN and Infinity values before evaluating formulas.",
                )
            return numeric
        if isinstance(raw, str):
            try:
                numeric = float(raw)
                if not math.isfinite(numeric):
                    raise ValueError("non-finite number")
                return numeric
            except ValueError:
                raise error(
                    "HED-DATA-0032",
                    title="Non-numeric formula cell",
                    explanation=f"Column {name!r} value {raw!r} is not a number.",
                    remediation="Use numeric cells, or omit non-numeric columns from the formula.",
                ) from None
        raise error(
            "HED-DATA-0032",
            title="Non-numeric formula cell",
            explanation=f"Column {name!r} has unsupported type {type(raw).__name__}.",
            remediation="Use numeric cells, or omit non-numeric columns from the formula.",
        )

    # Replace column refs with bound Names so "[a]e3" cannot become scientific
    # notation after string substitution (#247).
    env: dict[str, float] = {}
    for name in refs:
        env[f"_col_{name}"] = _cell_float(name)
    replaced = _COLUMN_REF.sub(lambda m: f"_col_{m.group(1)}", text)
    try:
        tree = ast.parse(replaced, mode="eval")
    except SyntaxError as exc:
        raise error(
            "HED-DATA-0032",
            title="Invalid formula syntax",
            explanation=str(exc),
            remediation="Use only numeric literals, [column] refs, and + - * /.",
        ) from exc

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, (int, float))
            and not isinstance(node.value, bool)
        ):
            return float(node.value)
        if isinstance(node, ast.Name):
            if node.id not in env:
                raise error(
                    "HED-DATA-0032",
                    title="Disallowed formula construct",
                    explanation=f"Unknown name {node.id!r} is not permitted.",
                    remediation="Use only numeric literals, [column] refs, and + - * /.",
                )
            return env[node.id]
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            fn = _UNARY_OPS.get(op_type)
            if fn is None:
                raise error(
                    "HED-DATA-0032",
                    title="Disallowed formula construct",
                    explanation=f"Unary op {op_type.__name__} is not permitted.",
                    remediation="Use only + and - unary operators.",
                )
            return fn(_eval(node.operand))
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            fn = _BIN_OPS.get(op_type)
            if fn is None:
                raise error(
                    "HED-DATA-0032",
                    title="Disallowed formula construct",
                    explanation=f"Binary op {op_type.__name__} is not permitted.",
                    remediation="Use only + - * /.",
                )
            return fn(_eval(node.left), _eval(node.right))
        raise error(
            "HED-DATA-0032",
            title="Disallowed formula construct",
            explanation=f"Node type {type(node).__name__} is not permitted.",
            remediation="Reject attribute access, calls, names, and imports.",
        )

    try:
        result = _eval(tree)
        if not math.isfinite(result):
            raise ValueError("formula result is not finite")
        return result
    except (ZeroDivisionError, OverflowError, ValueError) as exc:
        raise error(
            "HED-DATA-0032",
            title="Invalid formula evaluation",
            explanation=str(exc),
            remediation="Use only numeric literals, [column] refs, and + - * /.",
        ) from exc


def pivot_rows(
    rows: Sequence[Mapping[str, JsonValue]],
    *,
    index: str,
    columns: str,
    values: str,
    agg: str = "sum",
) -> list[dict[str, JsonValue]]:
    if agg not in {"sum", "count", "avg"}:
        raise ValueError(f"Unsupported pivot aggregate {agg!r}")
    buckets: dict[tuple[tuple[str, JsonValue], tuple[str, JsonValue]], list[float]] = {}

    def _typed_key(value: JsonValue) -> tuple[str, JsonValue]:
        try:
            hash(value)
        except TypeError as exc:
            raise ValueError("Pivot index and column values must be hashable") from exc
        return (type(value).__name__, value)

    for row in rows:
        idx = row.get(index)
        col = row.get(columns)
        bucket_key = (_typed_key(idx), _typed_key(col))
        raw = row.get(values)
        if agg == "count":
            buckets.setdefault(bucket_key, []).append(1.0)
            continue
        if isinstance(raw, bool):
            continue
        try:
            num = float(raw)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        if not math.isfinite(num):
            continue
        buckets.setdefault(bucket_key, []).append(num)
    out: list[dict[str, JsonValue]] = []
    by_index: dict[tuple[str, JsonValue], dict[tuple[str, JsonValue], list[float]]] = {}
    for (idx_key, col_key), nums in buckets.items():
        by_index.setdefault(idx_key, {})[col_key] = nums
    for idx_key, cols in by_index.items():
        item: dict[str, JsonValue] = {index: idx_key[1]}
        emitted: dict[str, tuple[str, JsonValue]] = {}
        for col_key, nums in cols.items():
            key = str(col_key[1])
            previous = emitted.get(key)
            if previous is not None and previous != col_key:
                raise ValueError(f"Pivot column values {previous[1]!r} and {col_key[1]!r} collide")
            emitted[key] = col_key
            if agg == "sum":
                aggregate = sum(nums)
            elif agg == "count":
                aggregate = len(nums)
            else:  # agg == "avg"; unsupported values are rejected above.
                aggregate = sum(nums) / len(nums) if nums else 0.0
            if isinstance(aggregate, float) and not math.isfinite(aggregate):
                raise ValueError("Pivot aggregate is not a finite JSON number")
            item[key] = aggregate
        out.append(item)
    return out


def rows_to_tree(
    rows: Sequence[Mapping[str, JsonValue]],
    *,
    id_field: str = "id",
    parent_field: str = "parent_id",
) -> list[TreeNode]:
    nodes: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        key = str(row.get(id_field))
        if key in nodes:
            raise error(
                "HED-DATA-0034",
                title="Duplicate tree id",
                explanation=(f"Duplicate {id_field!r} value {key!r} at row index {index}."),
                remediation="Ensure id values are unique before building a tree.",
            )
        nodes[key] = {"data": dict(row), "children": [], "parent": row.get(parent_field)}
    roots: list[str] = []
    for key, node in nodes.items():
        parent = node["parent"]
        if parent is None or str(parent) not in nodes:
            roots.append(key)
        else:
            nodes[str(parent)]["children"].append(key)

    visiting: set[str] = set()
    visited: set[str] = set()

    def build(key: str) -> TreeNode:
        if key in visiting:
            raise error(
                "HED-DATA-0033",
                title="Tree cycle detected",
                explanation=f"Parent/child cycle involving {key!r}.",
                remediation="Ensure id/parent_id relationships form a forest.",
            )
        if key in visited:
            node = nodes[key]
            return TreeNode(key=key, data=node["data"], children=())
        visiting.add(key)
        node = nodes[key]
        children = tuple(build(child) for child in node["children"])
        visiting.remove(key)
        visited.add(key)
        return TreeNode(key=key, data=node["data"], children=children)

    if nodes and not roots:
        # Pure cycle (every node has a parent in the set) — fail closed.
        raise error(
            "HED-DATA-0033",
            title="Tree cycle detected",
            explanation="Parent/child relationships form a cycle with no roots.",
            remediation="Ensure id/parent_id relationships form a forest.",
        )
    result = [build(key) for key in roots]
    if len(visited) != len(nodes):
        unreachable = sorted(set(nodes) - visited)
        raise error(
            "HED-DATA-0033",
            title="Unreachable tree node",
            explanation=f"Tree nodes are not reachable from a root: {unreachable!r}.",
            remediation="Ensure every parent_id refers to a reachable id or is null.",
        )
    return result


def flatten_tree(nodes: Sequence[TreeNode], *, depth: int = 0) -> list[dict[str, JsonValue]]:
    rows: list[dict[str, JsonValue]] = []
    for node in nodes:
        row = dict(node.data)
        row["_tree_key"] = node.key
        row["_tree_depth"] = depth
        rows.append(row)
        rows.extend(flatten_tree(node.children, depth=depth + 1))
    return rows
