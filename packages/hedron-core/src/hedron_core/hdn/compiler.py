"""HDN compiler: AST → render program."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from hedron_core.hdn.ast import (
    ElementNode,
    ExprNode,
    ForNode,
    FragmentNode,
    HtmlRawNode,
    IfNode,
    Node,
    SlotNode,
    TextNode,
)
from hedron_core.hdn.expr import parse_expr
from hedron_core.hdn.parser import parse_hdn
from hedron_core.hdn.runtime import Op, RenderProgram
from hedron_core.identifiers import content_digest

__all__ = ["HDN_FORMAT_VERSION", "HdnCompileResult", "compile_hdn"]

HDN_FORMAT_VERSION = 1


@dataclass(frozen=True, slots=True)
class HdnCompileResult:
    program: RenderProgram
    digest: str
    source_map: tuple[Mapping[str, Any], ...]


def compile_hdn(source: str) -> HdnCompileResult:
    doc = parse_hdn(source)
    ops: list[Op] = []
    source_map: list[dict[str, Any]] = []
    deps: set[str] = set()
    _lower_nodes(doc.body, ops, source_map, deps)
    program = RenderProgram(
        format_version=HDN_FORMAT_VERSION,
        ops=tuple(ops),
        source_map=tuple(source_map),
        dependencies=tuple(sorted(deps)),
    )
    digest = content_digest(source)
    return HdnCompileResult(program=program, digest=digest, source_map=tuple(source_map))


def _lower_nodes(
    nodes: list[Node],
    ops: list[Op],
    source_map: list[dict[str, Any]],
    deps: set[str],
) -> None:
    for node in nodes:
        _lower_node(node, ops, source_map, deps)


def _lower_node(
    node: Node,
    ops: list[Op],
    source_map: list[dict[str, Any]],
    deps: set[str],
) -> None:
    span = {"line": node.span.line, "column": node.span.column, "index": node.span.index}
    if isinstance(node, TextNode):
        # Skip pure-whitespace-only between tags? Keep as-is for fidelity.
        ops.append(Op("text", {"value": node.value}))
        source_map.append({**span, "op": "text"})
        return
    if isinstance(node, ExprNode):
        parse_expr(node.source)  # typecheck/parse early
        ops.append(Op("expr", {"source": node.source}))
        source_map.append({**span, "op": "expr"})
        return
    if isinstance(node, HtmlRawNode):
        parse_expr(node.expression)
        ops.append(Op("raw_html", {"source": node.expression}))
        source_map.append({**span, "op": "raw_html"})
        return
    if isinstance(node, FragmentNode):
        start = len(ops)
        ops.append(Op("fragment", {"child_count": 0}))
        source_map.append({**span, "op": "fragment"})
        child_ops: list[Op] = []
        child_map: list[dict[str, Any]] = []
        _lower_nodes(node.children, child_ops, child_map, deps)
        ops[start] = Op("fragment", {"child_count": len(child_ops)})
        ops.extend(child_ops)
        source_map.extend(child_map)
        return
    if isinstance(node, IfNode):
        parse_expr(node.condition)
        then_ops: list[Op] = []
        then_map: list[dict[str, Any]] = []
        else_ops: list[Op] = []
        else_map: list[dict[str, Any]] = []
        _lower_nodes(node.then_body, then_ops, then_map, deps)
        _lower_nodes(node.else_body, else_ops, else_map, deps)
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
        parse_expr(node.iterable)
        body_ops: list[Op] = []
        body_map: list[dict[str, Any]] = []
        _lower_nodes(node.body, body_ops, body_map, deps)
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
        # Slots lower as fragments for MVP; named slots recorded as dependency metadata.
        deps.add(f"slot:{node.name}")
        start = len(ops)
        ops.append(Op("fragment", {"child_count": 0}))
        source_map.append({**span, "op": "slot", "name": node.name})
        child_ops = []
        child_map = []
        _lower_nodes(node.children, child_ops, child_map, deps)
        ops[start] = Op("fragment", {"child_count": len(child_ops)})
        ops.extend(child_ops)
        source_map.extend(child_map)
        return
    if isinstance(node, ElementNode):
        if node.tag[:1].isupper():
            deps.add(node.tag)
        attr_specs: list[dict[str, Any]] = []
        for name, value in node.attrs.items():
            if isinstance(value, ExprNode):
                parse_expr(value.source)
                attr_specs.append({"name": name, "kind": "expr", "source": value.source})
            else:
                attr_specs.append({"name": name, "kind": "static", "value": value})
        start = len(ops)
        ops.append(Op("element", {"tag": node.tag, "attrs": attr_specs, "child_count": 0}))
        source_map.append({**span, "op": "element", "tag": node.tag})
        child_ops = []
        child_map = []
        _lower_nodes(node.children, child_ops, child_map, deps)
        ops[start] = Op(
            "element",
            {"tag": node.tag, "attrs": attr_specs, "child_count": len(child_ops)},
        )
        ops.extend(child_ops)
        source_map.extend(child_map)
        return
    raise TypeError(f"Unknown HDN node: {type(node)}")
