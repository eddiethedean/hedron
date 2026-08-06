"""Shared helpers for built-in components."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from hedron_core.component import Component, NodeLike
from hedron_core.models import Props


class ChildrenProps(Props):
    """Marker props for components that primarily accept children via constructor."""


class ElementProps(Props):
    """Common addressability and theme-extension props for wrapper components."""

    id: str | None = None
    class_: str | None = None
    mark: str | None = None


def mark_data(mark: str | None) -> dict[str, str | bool | int | float | None]:
    """Emit ``data-hedron-mark`` via ``html.*(data=...)`` when ``mark`` is set."""
    return {"hedron-mark": mark} if mark else {}


_DOM_ID_PART_RE = re.compile(r"[^A-Za-z0-9_-]+")


def dom_id_part(value: object, *, fallback: str = "item") -> str:
    """Return a selector-friendly fragment for framework-generated DOM IDs."""
    normalized = _DOM_ID_PART_RE.sub("-", str(value)).strip("-")
    return normalized or fallback


def class_names(base: str, custom: str | None = None) -> str:
    """Keep a built-in's theme hook while allowing application-specific classes."""
    return " ".join(part for part in (base, custom) if part)


def collect_children(*nodes: NodeLike, children: NodeLike = None) -> tuple[NodeLike, ...]:
    """Normalize the two supported container-construction styles.

    Container-like built-ins accept either positional children or a ``children=``
    value. A sole positional sequence is flattened for parity with ``children=``.
    """
    collected: list[NodeLike] = []
    if (
        len(nodes) == 1
        and isinstance(nodes[0], Sequence)
        and not isinstance(nodes[0], (str, bytes))
    ):
        collected.extend(nodes[0])
    else:
        collected.extend(nodes)
    if children is not None:
        if isinstance(children, Sequence) and not isinstance(children, (str, bytes)):
            collected.extend(children)
        else:
            collected.append(children)
    return tuple(collected)


def take_children(
    component: Component[Any], *nodes: NodeLike, children: NodeLike = None
) -> tuple[NodeLike, ...]:
    """Backward-compatible helper that also includes fluent ``.children(...)`` values."""
    collected = list(collect_children(*nodes, children=children))
    if component._children:
        collected.extend(component._children)
    return tuple(collected)
