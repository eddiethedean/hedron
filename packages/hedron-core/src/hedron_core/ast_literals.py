"""Parse Python literal syntax into ``object`` values without ``Any``."""

from __future__ import annotations

import ast
from typing import Protocol, cast


class _ConstantNode(Protocol):
    value: object


def parse_literal(source: str) -> object:
    """Safely parse Python literal syntax with an ``object`` return type."""
    expression = ast.parse(source, mode="eval")
    return _literal_value(expression.body)


def _literal_value(node: ast.expr) -> object:
    if isinstance(node, ast.Constant):
        return cast(_ConstantNode, cast(object, node)).value
    if isinstance(node, ast.List):
        return [_literal_value(item) for item in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(_literal_value(item) for item in node.elts)
    if isinstance(node, ast.Set):
        return {_literal_value(item) for item in node.elts}
    if isinstance(node, ast.Dict):
        result: dict[object, object] = {}
        for key_node, value_node in zip(node.keys, node.values, strict=True):
            if key_node is None:
                unpacked = _literal_value(value_node)
                if not isinstance(unpacked, dict):
                    raise ValueError("dictionary unpacking requires a literal dictionary")
                result.update(cast(dict[object, object], unpacked))
            else:
                result[_literal_value(key_node)] = _literal_value(value_node)
        return result
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _literal_value(node.operand)
        if not isinstance(value, (int, float, complex)):
            raise ValueError("unary signs require a numeric literal")
        return value if isinstance(node.op, ast.UAdd) else -value
    raise ValueError(f"unsupported literal syntax: {type(node).__name__}")
