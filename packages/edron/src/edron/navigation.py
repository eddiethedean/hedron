"""Typed navigation targets and shared native layout recipes (phase 0.6)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal, cast

import hedron

LayoutKind = Literal["stack", "grid", "plain", "container"]
LAYOUT_KINDS: tuple[LayoutKind, ...] = ("stack", "grid", "plain", "container")
MAX_LAYOUT_CHILDREN = 256


class NavigationError(ValueError):
    """A navigation target is invalid or belongs to another app."""


@dataclass(frozen=True, slots=True)
class NavigationTarget:
    """An app-owned, typed reference to a registered native route."""

    app_id: str
    name: str
    path: str
    title: str
    source_kind: str = "page"

    @property
    def logical_id(self) -> str:
        return f"navigation:{self.name}"

    def link(self, label: str | None = None, **kwargs: Any) -> Any:
        """Lower to the native ``NavLink`` with all safety checks intact."""
        return hedron.NavLink(label or self.title, self.path, **kwargs)

    def as_mapping(self) -> dict[str, str]:
        return {
            "logical_id": self.logical_id,
            "name": self.name,
            "path": self.path,
            "title": self.title,
            "kind": self.source_kind,
        }


@dataclass(frozen=True, slots=True)
class LayoutSpec:
    """Bounded composition metadata that lowers to one native layout node."""

    kind: LayoutKind = "stack"
    gap: str = "1rem"
    columns: int | Mapping[str, int] = 2
    max_width: str | None = None
    align: str | None = None
    padding: str | None = None

    def __post_init__(self) -> None:
        if self.kind not in LAYOUT_KINDS:
            raise NavigationError(f"layout kind must be one of {LAYOUT_KINDS}")
        if not isinstance(self.gap, str) or not self.gap.strip() or len(self.gap) > 32:
            raise NavigationError("layout gap must be a bounded non-empty token")
        if isinstance(self.columns, int) and not 1 <= self.columns <= 6:
            raise NavigationError("layout columns must be between 1 and 6")
        if isinstance(self.columns, Mapping):
            if not self.columns or len(self.columns) > 8:
                raise NavigationError("responsive layout columns must contain 1-8 entries")
            if any(
                not isinstance(value, int) or not 1 <= value <= 6 for value in self.columns.values()
            ):
                raise NavigationError("responsive layout columns must be integers between 1 and 6")
        for label, value in (
            ("max_width", self.max_width),
            ("align", self.align),
            ("padding", self.padding),
        ):
            if value is not None and (not isinstance(value, str) or len(value) > 32):
                raise NavigationError(f"layout {label} must be a bounded token")

    def compose(self, nodes: Sequence[Any]) -> Any:
        """Create the corresponding native layout component."""
        if len(nodes) > MAX_LAYOUT_CHILDREN:
            raise NavigationError(f"layout accepts at most {MAX_LAYOUT_CHILDREN} children")
        if self.kind == "plain":
            return nodes[0] if len(nodes) == 1 else list(nodes)
        if self.kind == "grid":
            return hedron.Grid(*nodes, columns=self.columns, gap=self.gap)
        if self.kind == "container":
            return hedron.Container(
                *nodes,
                max_width=cast(Any, self.max_width),
                align=cast(Any, self.align),
                padding=self.padding,
            )
        return hedron.Stack(*nodes, gap=self.gap)

    def as_mapping(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "gap": self.gap,
            "columns": dict(self.columns) if isinstance(self.columns, Mapping) else self.columns,
            "max_width": self.max_width,
            "align": self.align,
            "padding": self.padding,
        }


def layout(kind: LayoutKind = "stack", **kwargs: Any) -> LayoutSpec:
    """Return a validated shared layout declaration."""
    return LayoutSpec(kind=kind, **kwargs)


__all__ = [
    "LAYOUT_KINDS",
    "LayoutKind",
    "LayoutSpec",
    "MAX_LAYOUT_CHILDREN",
    "NavigationError",
    "NavigationTarget",
    "layout",
]
