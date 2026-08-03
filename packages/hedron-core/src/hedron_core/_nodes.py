"""Private normalized node algebra for the renderer."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class TextNode:
    text: str


@dataclass(frozen=True, slots=True)
class TrustedHtmlNode:
    html: str
    source: str


@dataclass(frozen=True, slots=True)
class CommentNode:
    text: str


@dataclass(frozen=True, slots=True)
class EmptyNode:
    pass


@dataclass(frozen=True, slots=True)
class FragmentNode:
    children: tuple[Node, ...]


@dataclass(frozen=True, slots=True)
class ElementNode:
    tag: str
    attributes: Mapping[str, Any]
    children: tuple[Node, ...]
    void: bool = False


@dataclass(frozen=True, slots=True)
class ComponentBoundaryNode:
    logical_id: str
    instance_id: str | None
    children: tuple[Node, ...]
    props_summary: Mapping[str, Any] = field(default_factory=dict)


Node = (
    TextNode
    | TrustedHtmlNode
    | CommentNode
    | EmptyNode
    | FragmentNode
    | ElementNode
    | ComponentBoundaryNode
)


def flatten_nodes(nodes: Sequence[Node]) -> tuple[Node, ...]:
    out: list[Node] = []
    for node in nodes:
        if isinstance(node, EmptyNode):
            continue
        if isinstance(node, FragmentNode):
            out.extend(flatten_nodes(node.children))
        else:
            out.append(node)
    return tuple(out)
