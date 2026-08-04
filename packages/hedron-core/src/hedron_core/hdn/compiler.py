"""HDN compiler: AST → render program."""

from __future__ import annotations

import ast
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from hedron_core.codes import (
    HED_HDN_PARSE,
    HED_HDN_UNKNOWN_COMPONENT,
    HED_HDN_UNKNOWN_HELPER,
    HED_HDN_UNSAFE,
)
from hedron_core.diagnostics import error
from hedron_core.hdn.ast import (
    ElementNode,
    ExprNode,
    ForNode,
    FragmentNode,
    HtmlRawNode,
    IfNode,
    ImportNode,
    Node,
    SlotNode,
    TextNode,
)
from hedron_core.hdn.expr import PURE_HELPERS, parse_expr
from hedron_core.hdn.parser import parse_hdn
from hedron_core.hdn.runtime import HDN_FORMAT_VERSION, Op, RenderProgram
from hedron_core.identifiers import content_digest

__all__ = ["HDN_FORMAT_VERSION", "HdnCompileResult", "compile_hdn", "validate_expr"]


@dataclass(frozen=True, slots=True)
class HdnCompileResult:
    program: RenderProgram
    digest: str
    source_map: tuple[Mapping[str, Any], ...]


def validate_expr(source: str) -> ast.AST:
    """Parse and reject arbitrary calls at compile time."""
    node = parse_expr(source)
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if not isinstance(child.func, ast.Name):
                raise error(
                    HED_HDN_UNSAFE,
                    title="Arbitrary call rejected",
                    explanation="Only registered pure helpers may be called.",
                    remediation="Use a helper from the HDN pure helper registry.",
                    context={"expression": source},
                )
            name = child.func.id
            if name != "__coalesce" and name not in PURE_HELPERS:
                raise error(
                    HED_HDN_UNKNOWN_HELPER,
                    title="Unknown HDN helper",
                    explanation=f"Helper {name!r} is not registered.",
                    remediation=f"Known helpers: {', '.join(sorted(PURE_HELPERS))}.",
                    context={"expression": source},
                )
    return node


def _rewrite_class_value(value: str, style_symbols: Mapping[str, str]) -> str:
    parts = []
    for token in value.split():
        parts.append(style_symbols.get(token, token))
    return " ".join(parts)


def compile_hdn(
    source: str,
    *,
    style_symbols: Mapping[str, str] | None = None,
) -> HdnCompileResult:
    from hedron_core.compile_gate import assert_runtime_compile_allowed
    from hedron_core.manifests import canonical_json

    assert_runtime_compile_allowed(what="HDN")
    doc = parse_hdn(source)
    ops: list[Op] = []
    source_map: list[dict[str, Any]] = []
    component_imports: dict[str, str] = {}
    for node in doc.body:
        if not isinstance(node, ImportNode):
            continue
        previous = component_imports.get(node.local_name)
        if previous is not None:
            raise error(
                HED_HDN_PARSE,
                title="Duplicate component import",
                explanation=(
                    f"Component name {node.local_name!r} is already imported from {previous!r}."
                ),
                remediation="Remove the duplicate import or choose a distinct local name.",
                context={"line": node.span.line, "column": node.span.column},
            )
        component_imports[node.local_name] = node.component_ref
    body: list[Node] = []
    saw_content = False
    for node in doc.body:
        if isinstance(node, ImportNode):
            continue
        if (
            component_imports
            and not saw_content
            and isinstance(node, TextNode)
            and not node.value.strip()
        ):
            continue
        saw_content = True
        body.append(node)
    deps: set[str] = set(component_imports.values())
    symbols = dict(style_symbols or {})
    _lower_nodes(body, ops, source_map, deps, symbols, component_imports)
    program = RenderProgram(
        format_version=HDN_FORMAT_VERSION,
        ops=tuple(ops),
        source_map=tuple(source_map),
        dependencies=tuple(sorted(deps)),
        component_imports=component_imports,
    )
    digest = content_digest(source + "\0" + canonical_json(symbols))
    return HdnCompileResult(program=program, digest=digest, source_map=tuple(source_map))


def _lower_nodes(
    nodes: list[Node],
    ops: list[Op],
    source_map: list[dict[str, Any]],
    deps: set[str],
    style_symbols: dict[str, str],
    component_imports: Mapping[str, str],
) -> None:
    for node in nodes:
        _lower_node(node, ops, source_map, deps, style_symbols, component_imports)


def _lower_node(
    node: Node,
    ops: list[Op],
    source_map: list[dict[str, Any]],
    deps: set[str],
    style_symbols: dict[str, str],
    component_imports: Mapping[str, str],
) -> None:
    span = {"line": node.span.line, "column": node.span.column, "index": node.span.index}
    if isinstance(node, TextNode):
        ops.append(Op("text", {"value": node.value}))
        source_map.append({**span, "op": "text"})
        return
    if isinstance(node, ExprNode):
        validate_expr(node.source)
        ops.append(Op("expr", {"source": node.source}))
        source_map.append({**span, "op": "expr"})
        return
    if isinstance(node, HtmlRawNode):
        validate_expr(node.expression)
        ops.append(Op("raw_html", {"source": node.expression}))
        source_map.append({**span, "op": "raw_html"})
        return
    if isinstance(node, FragmentNode):
        start = len(ops)
        ops.append(Op("fragment", {"child_count": 0}))
        source_map.append({**span, "op": "fragment"})
        child_ops: list[Op] = []
        child_map: list[dict[str, Any]] = []
        _lower_nodes(node.children, child_ops, child_map, deps, style_symbols, component_imports)
        ops[start] = Op("fragment", {"child_count": len(child_ops)})
        ops.extend(child_ops)
        source_map.extend(child_map)
        return
    if isinstance(node, IfNode):
        validate_expr(node.condition)
        then_ops: list[Op] = []
        then_map: list[dict[str, Any]] = []
        else_ops: list[Op] = []
        else_map: list[dict[str, Any]] = []
        _lower_nodes(node.then_body, then_ops, then_map, deps, style_symbols, component_imports)
        _lower_nodes(node.else_body, else_ops, else_map, deps, style_symbols, component_imports)
        ops.append(
            Op(
                "if",
                {
                    "condition": node.condition,
                    "then_count": len(then_ops),
                    "else_count": len(else_ops),
                },
            )
        )
        source_map.append({**span, "op": "if"})
        ops.extend(then_ops)
        source_map.extend(then_map)
        ops.extend(else_ops)
        source_map.extend(else_map)
        return
    if isinstance(node, ForNode):
        validate_expr(node.iterable)
        body_ops: list[Op] = []
        body_map: list[dict[str, Any]] = []
        _lower_nodes(node.body, body_ops, body_map, deps, style_symbols, component_imports)
        ops.append(
            Op(
                "for",
                {
                    "item": node.item,
                    "iterable": node.iterable,
                    "body_count": len(body_ops),
                },
            )
        )
        source_map.append({**span, "op": "for"})
        ops.extend(body_ops)
        source_map.extend(body_map)
        return
    if isinstance(node, SlotNode):
        deps.add(f"slot:{node.name}")
        start = len(ops)
        ops.append(Op("fragment", {"child_count": 0}))
        source_map.append({**span, "op": "slot", "name": node.name})
        child_ops: list[Op] = []
        child_map: list[dict[str, Any]] = []
        _lower_nodes(node.children, child_ops, child_map, deps, style_symbols, component_imports)
        ops[start] = Op("fragment", {"child_count": len(child_ops)})
        ops.extend(child_ops)
        source_map.extend(child_map)
        return
    if isinstance(node, ElementNode):
        component_ref: str | None = None
        if node.tag[:1].isupper():
            if component_imports:
                component_ref = component_imports.get(node.tag)
                if component_ref is None:
                    raise error(
                        HED_HDN_UNKNOWN_COMPONENT,
                        title="Component is not imported",
                        explanation=(
                            f"Component tag <{node.tag}> has no matching {{@import ...}} "
                            "declaration."
                        ),
                        remediation=(
                            f'Add {{@import {node.tag} from "component-logical-id"}} at '
                            "the top of the template."
                        ),
                        context={"line": node.span.line, "column": node.span.column},
                    )
            else:
                component_ref = node.tag
            deps.add(component_ref)
        attr_specs: list[dict[str, Any]] = []
        for name, value in node.attrs.items():
            if isinstance(value, ExprNode):
                validate_expr(value.source)
                attr_specs.append({"name": name, "kind": "expr", "source": value.source})
            else:
                static_value = value
                if name == "class" and isinstance(value, str) and style_symbols:
                    static_value = _rewrite_class_value(value, style_symbols)
                attr_specs.append({"name": name, "kind": "static", "value": static_value})
        start = len(ops)
        element_data: dict[str, Any] = {
            "tag": node.tag,
            "attrs": attr_specs,
            "child_count": 0,
        }
        if component_ref is not None:
            element_data["component_ref"] = component_ref
        ops.append(Op("element", element_data))
        source_map.append({**span, "op": "element", "tag": node.tag})
        child_ops = []
        child_map = []
        _lower_nodes(node.children, child_ops, child_map, deps, style_symbols, component_imports)
        element_data = {
            "tag": node.tag,
            "attrs": attr_specs,
            "child_count": len(child_ops),
        }
        if component_ref is not None:
            element_data["component_ref"] = component_ref
        ops[start] = Op(
            "element",
            element_data,
        )
        ops.extend(child_ops)
        source_map.extend(child_map)
        return
    raise TypeError(f"Unknown HDN node: {type(node)}")
