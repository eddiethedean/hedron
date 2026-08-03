"""HDN expression evaluator (bounded, no arbitrary calls)."""

from __future__ import annotations

import ast
import operator
from collections.abc import Callable, Mapping
from typing import Any

from hedron_core.codes import HED_HDN_TYPE, HED_HDN_UNKNOWN_HELPER, HED_HDN_UNSAFE
from hedron_core.diagnostics import error

__all__ = ["PURE_HELPERS", "eval_expr", "parse_expr"]

_BINOPS: dict[type[Any], Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
}

_CMPOPS: dict[type[ast.cmpop], Callable[[Any, Any], Any]] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
    ast.Is: operator.is_,
    ast.IsNot: operator.is_not,
}


def _helper_len(value: Any) -> int:
    return len(value)


def _helper_str(value: Any) -> str:
    return str(value)


def _helper_int(value: Any) -> int:
    return int(value)


def _helper_bool(value: Any) -> bool:
    return bool(value)


def _helper_enum_name(value: Any) -> str:
    return getattr(value, "name", str(value))


PURE_HELPERS: dict[str, Callable[..., Any]] = {
    "len": _helper_len,
    "str": _helper_str,
    "int": _helper_int,
    "bool": _helper_bool,
    "enum_name": _helper_enum_name,
}


def parse_expr(source: str) -> ast.AST:
    # Support ?? as a token rewrite to a sentinel call before Python parse.
    rewritten = _rewrite_nullish(source)
    try:
        tree = ast.parse(rewritten, mode="eval")
    except SyntaxError as exc:
        raise error(
            HED_HDN_TYPE,
            title="Invalid HDN expression",
            explanation=f"Could not parse expression {source!r}: {exc.msg}",
            remediation="Fix the expression syntax.",
            context={"expression": source},
        ) from exc
    return tree.body


def _rewrite_nullish(source: str) -> str:
    """Rewrite ``a ?? b`` into ``__coalesce(a, b)`` without splitting string literals."""
    if "??" not in source:
        return source
    parts: list[str] = []
    buf: list[str] = []
    i = 0
    n = len(source)
    in_str: str | None = None
    while i < n:
        ch = source[i]
        if in_str:
            buf.append(ch)
            if ch == "\\" and i + 1 < n:
                buf.append(source[i + 1])
                i += 2
                continue
            if ch == in_str:
                in_str = None
            i += 1
            continue
        if ch in {'"', "'"}:
            in_str = ch
            buf.append(ch)
            i += 1
            continue
        if ch == "?" and i + 1 < n and source[i + 1] == "?":
            parts.append("".join(buf).strip())
            buf = []
            i += 2
            continue
        buf.append(ch)
        i += 1
    parts.append("".join(buf).strip())
    if len(parts) == 1:
        return source
    if any(not p for p in parts):
        raise error(
            HED_HDN_TYPE,
            title="Invalid nullish coalescing",
            explanation=f"Malformed ?? expression in {source!r}.",
            remediation="Use `a ?? b` with non-empty operands.",
            context={"expression": source},
        )
    expr = parts[0]
    for part in parts[1:]:
        expr = f"__coalesce({expr}, {part})"
    return expr


def eval_expr(source: str, env: Mapping[str, Any]) -> Any:
    try:
        node = parse_expr(source)
        return _eval(node, dict(env))
    except Exception as exc:
        from hedron_core.diagnostics import HedronError

        if isinstance(exc, HedronError):
            raise
        raise error(
            HED_HDN_TYPE,
            title="Expression evaluation failed",
            explanation=f"Failed to evaluate {source!r}: {exc}",
            remediation="Fix the expression or provide valid runtime values.",
            context={"expression": source},
        ) from exc


def _eval(node: ast.AST, env: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id == "true":
            return True
        if node.id == "false":
            return False
        if node.id == "null" or node.id == "None":
            return None
        if node.id not in env:
            raise error(
                HED_HDN_TYPE,
                title="Unknown name in expression",
                explanation=f"Name {node.id!r} is not in scope.",
                remediation="Pass the value in the render scope or fix the name.",
            )
        return env[node.id]
    if isinstance(node, ast.Attribute):
        value = _eval(node.value, env)
        if node.attr.startswith("_"):
            raise error(
                HED_HDN_UNSAFE,
                title="Private attribute access rejected",
                explanation=f"Cannot access {node.attr!r}.",
                remediation="Expose a public property instead.",
            )
        try:
            return getattr(value, node.attr)
        except AttributeError:
            if isinstance(value, Mapping) and node.attr in value:
                return value[node.attr]
            raise error(
                HED_HDN_TYPE,
                title="Unknown attribute",
                explanation=f"Attribute {node.attr!r} not found.",
                remediation="Check the property name.",
            ) from None
    if isinstance(node, ast.Subscript):
        value = _eval(node.value, env)
        sl = node.slice
        index = _eval(sl, env)
        try:
            return value[index]
        except Exception as exc:
            raise error(
                HED_HDN_TYPE,
                title="Invalid index",
                explanation=f"Cannot index value with {index!r}.",
                remediation="Use a valid typed index.",
            ) from exc
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not _eval(node.operand, env)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval(node.operand, env)
    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            result: Any = True
            for v in node.values:
                result = _eval(v, env)
                if not result:
                    return result
            return result
        if isinstance(node.op, ast.Or):
            result = False
            for v in node.values:
                result = _eval(v, env)
                if result:
                    return result
            return result
    if isinstance(node, ast.BinOp):
        left = _eval(node.left, env)
        right = _eval(node.right, env)
        op_type = type(node.op)
        if op_type not in {ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod}:
            raise error(
                HED_HDN_UNSAFE,
                title="Unsupported operator",
                explanation=f"Operator {op_type.__name__} is not allowed in HDN.",
                remediation="Use supported arithmetic or comparison operators.",
            )
        try:
            return _BINOPS[op_type](left, right)
        except Exception as exc:
            raise error(
                HED_HDN_TYPE,
                title="Arithmetic error",
                explanation=f"Operator {op_type.__name__} failed: {exc}",
                remediation="Check operand types and values.",
            ) from exc
    if isinstance(node, ast.Compare):
        left = _eval(node.left, env)
        for op, comparator in zip(node.ops, node.comparators, strict=True):
            right = _eval(comparator, env)
            fn = _CMPOPS.get(type(op))
            if fn is None:
                raise error(
                    HED_HDN_UNSAFE,
                    title="Unsupported comparison",
                    explanation="Comparison operator is not allowed.",
                    remediation="Use ==, !=, <, <=, >, >=, in, or not in.",
                )
            if not fn(left, right):
                return False
            left = right
        return True
    if isinstance(node, ast.IfExp):
        return _eval(node.body, env) if _eval(node.test, env) else _eval(node.orelse, env)
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise error(
                HED_HDN_UNSAFE,
                title="Arbitrary call rejected",
                explanation="Only registered pure helpers may be called.",
                remediation="Use a helper from the HDN pure helper registry.",
            )
        name = node.func.id
        if name == "__coalesce":
            if len(node.args) != 2:
                raise error(
                    HED_HDN_TYPE,
                    title="Invalid coalesce",
                    explanation="?? expects two operands.",
                )
            left = _eval(node.args[0], env)
            return left if left is not None else _eval(node.args[1], env)
        helper = PURE_HELPERS.get(name)
        if helper is None:
            raise error(
                HED_HDN_UNKNOWN_HELPER,
                title="Unknown HDN helper",
                explanation=f"Helper {name!r} is not registered.",
                remediation=f"Known helpers: {', '.join(sorted(PURE_HELPERS))}.",
            )
        if node.keywords:
            raise error(
                HED_HDN_UNSAFE,
                title="Keyword arguments rejected",
                explanation="HDN helpers do not accept keyword arguments.",
            )
        args = [_eval(a, env) for a in node.args]
        return helper(*args)
    if isinstance(node, ast.List):
        return [_eval(elt, env) for elt in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(_eval(elt, env) for elt in node.elts)
    if isinstance(node, ast.Dict):
        raise error(
            HED_HDN_UNSAFE,
            title="Dict literals rejected",
            explanation="Dict literals are not supported in HDN expressions.",
            remediation="Pass mappings from the Python scope instead.",
        )
    raise error(
        HED_HDN_UNSAFE,
        title="Unsupported expression node",
        explanation=f"Expression node {type(node).__name__} is not allowed.",
        remediation="Simplify the expression to supported HDN forms.",
    )
