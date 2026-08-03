"""HDN formatter (idempotent pretty-printer)."""

from __future__ import annotations

from hedron_core.hdn.ast import (
    Document,
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
from hedron_core.hdn.parser import parse_hdn

__all__ = ["format_hdn"]


def format_hdn(source: str) -> str:
    doc = parse_hdn(source)
    return _format_document(doc)


def _format_document(doc: Document) -> str:
    parts = [_format_node(n, 0) for n in doc.body]
    text = "\n".join(p for p in parts if p is not None and p != "")
    return text.rstrip() + "\n"


def _indent(level: int) -> str:
    return "  " * level


def _format_node(node: Node, level: int) -> str:
    pad = _indent(level)
    if isinstance(node, TextNode):
        text = node.value.strip()
        return f"{pad}{text}" if text else ""
    if isinstance(node, ExprNode):
        return f"{pad}{{{node.source}}}"
    if isinstance(node, HtmlRawNode):
        return f"{pad}{{@html {node.expression}}}"
    if isinstance(node, IfNode):
        lines = [f"{pad}{{#if {node.condition}}}"]
        for child in node.then_body:
            rendered = _format_node(child, level + 1)
            if rendered:
                lines.append(rendered)
        if node.else_body:
            lines.append(f"{pad}{{:else}}")
            for child in node.else_body:
                rendered = _format_node(child, level + 1)
                if rendered:
                    lines.append(rendered)
        lines.append(f"{pad}{{/if}}")
        return "\n".join(lines)
    if isinstance(node, ForNode):
        lines = [f"{pad}{{#for {node.item} in {node.iterable}}}"]
        for child in node.body:
            rendered = _format_node(child, level + 1)
            if rendered:
                lines.append(rendered)
        lines.append(f"{pad}{{/for}}")
        return "\n".join(lines)
    if isinstance(node, FragmentNode):
        lines = [f"{pad}<>"]
        for child in node.children:
            rendered = _format_node(child, level + 1)
            if rendered:
                lines.append(rendered)
        lines.append(f"{pad}</>")
        return "\n".join(lines)
    if isinstance(node, SlotNode):
        open_tag = f'{pad}<slot name="{node.name}">'
        if not node.children:
            return f'{pad}<slot name="{node.name}" />'
        lines = [open_tag]
        for child in node.children:
            rendered = _format_node(child, level + 1)
            if rendered:
                lines.append(rendered)
        lines.append(f"{pad}</slot>")
        return "\n".join(lines)
    if isinstance(node, ElementNode):
        attrs = []
        for key, value in node.attrs.items():
            if value is True:
                attrs.append(key)
            elif isinstance(value, ExprNode):
                attrs.append(f"{key}={{{value.source}}}")
            else:
                attrs.append(f'{key}="{value}"')
        attr_str = (" " + " ".join(attrs)) if attrs else ""
        if node.self_closing or not node.children:
            return f"{pad}<{node.tag}{attr_str} />"
        lines = [f"{pad}<{node.tag}{attr_str}>"]
        for child in node.children:
            rendered = _format_node(child, level + 1)
            if rendered:
                lines.append(rendered)
        lines.append(f"{pad}</{node.tag}>")
        return "\n".join(lines)
    return ""
