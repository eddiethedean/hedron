"""Shared helpers for built-in components."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from hedron_core.component import Component
from hedron_core.models import Props


class ChildrenProps(Props):
    """Marker props for components that primarily accept children via constructor."""


def take_children(component: Component[Any], *nodes: Any, children: Any = None) -> tuple[Any, ...]:
    collected: list[Any] = list(nodes)
    if children is not None:
        if isinstance(children, Sequence) and not isinstance(children, (str, bytes)):
            collected.extend(children)
        else:
            collected.append(children)
    if component._children:
        collected.extend(component._children)
    return tuple(collected)
