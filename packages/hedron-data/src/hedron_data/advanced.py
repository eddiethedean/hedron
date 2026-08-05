"""Advanced DataEditor helpers: formulas, merges, pivots, trees, formats."""

from __future__ import annotations

import ast
import operator
import re
from collections.abc import Mapping, Sequence
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
_BIN_OPS: dict[type[ast.operator], Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_UNARY_OPS: dict[type[ast.unaryop], Any] = {ast.UAdd: operator.pos, ast.USub: operator.neg}


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
    if not isinstance(expr, str) or not expr.strip():
        raise error(
            "HED-DATA-0030",
            title="Empty formula",
            explanation="Formulas must be non-empty strings.",
            remediation="Provide a formula such as '=[price]*[qty]'.",
        )
    text = expr.strip()
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
            return 0.0
        if isinstance(raw, (int, float)):
            return float(raw)
        if isinstance(raw, str):
            try:
                return float(raw)
            except ValueError:
                return 0.0
        return 0.0

    replaced = _COLUMN_REF.sub(lambda m: str(_cell_float(m.group(1))), text)
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
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
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
        return _eval(tree)
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
    buckets: dict[JsonValue, dict[JsonValue, list[float]]] = {}
    for row in rows:
        idx = row.get(index)
        col = row.get(columns)
        raw = row.get(values)
        try:
            num = float(raw)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        buckets.setdefault(idx, {}).setdefault(col, []).append(num)
    out: list[dict[str, JsonValue]] = []
    for idx, cols in buckets.items():
        item: dict[str, JsonValue] = {index: idx}
        for col, nums in cols.items():
            key = str(col)
            if agg == "sum":
                item[key] = sum(nums)
            elif agg == "count":
                item[key] = len(nums)
            elif agg == "avg":
                item[key] = sum(nums) / len(nums) if nums else 0.0
            else:
                raise ValueError(f"Unsupported pivot aggregate {agg!r}")
        out.append(item)
    return out


def rows_to_tree(
    rows: Sequence[Mapping[str, JsonValue]],
    *,
    id_field: str = "id",
    parent_field: str = "parent_id",
) -> list[TreeNode]:
    nodes: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get(id_field))
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
    return [build(key) for key in roots]


def flatten_tree(nodes: Sequence[TreeNode], *, depth: int = 0) -> list[dict[str, JsonValue]]:
    rows: list[dict[str, JsonValue]] = []
    for node in nodes:
        row = dict(node.data)
        row["_tree_key"] = node.key
        row["_tree_depth"] = depth
        rows.append(row)
        rows.extend(flatten_tree(node.children, depth=depth + 1))
    return rows
