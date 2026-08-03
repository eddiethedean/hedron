"""HDN syntax tree nodes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SourceSpan:
    line: int
    column: int
    index: int


@dataclass
class Node:
    span: SourceSpan


@dataclass
class TextNode(Node):
    value: str = ""


@dataclass
class ExprNode(Node):
    source: str = ""


@dataclass
class ElementNode(Node):
    tag: str = ""
    attrs: dict[str, Any] = field(default_factory=dict)
    children: list[Node] = field(default_factory=list)
    self_closing: bool = False


@dataclass
class FragmentNode(Node):
    children: list[Node] = field(default_factory=list)


@dataclass
class IfNode(Node):
    condition: str = ""
    then_body: list[Node] = field(default_factory=list)
    else_body: list[Node] = field(default_factory=list)


@dataclass
class ForNode(Node):
    item: str = ""
    iterable: str = ""
    body: list[Node] = field(default_factory=list)


@dataclass
class HtmlRawNode(Node):
    expression: str = ""


@dataclass
class SlotNode(Node):
    name: str = "default"
    children: list[Node] = field(default_factory=list)


@dataclass
class Document:
    body: list[Node] = field(default_factory=list)
