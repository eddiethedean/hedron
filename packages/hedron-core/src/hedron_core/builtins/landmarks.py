"""Landmark built-ins — real typed classes with allowlisted safe attrs (LANDMARK-019)."""

from __future__ import annotations

from typing import Any, Literal

from hedron_core.builtins._base import collect_children
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.typing_aliases import HtmlAttrValue

__all__ = ["Aside", "Footer", "Header", "LandmarkProps", "Main", "Nav", "Section"]

_LANDMARK_SAFE_KEYS = frozenset(
    {
        "class_",
        "id",
        "lang",
        "dir",
        "role",
        "title",
        "tabindex",
        "aria",
        "data",
        "hidden",
    }
)

# Roles that strip or override landmark semantics — rejected on landmark surfaces.
_LANDMARK_HOSTILE_ROLES = frozenset({"presentation", "none"})


class LandmarkProps(Props):
    """Shared props for semantic landmark surfaces."""

    class_: str | None = None
    id: str | None = None
    lang: str | None = None
    dir: Literal["ltr", "rtl", "auto"] | None = None
    role: str | None = None
    title: str | None = None
    tabindex: int | None = None
    aria: dict[str, str | bool | int | float | None] | None = None
    data: dict[str, str | bool | int | float | None] | None = None
    hidden: bool | None = None


def _landmark_attrs(props: LandmarkProps) -> dict[str, HtmlAttrValue]:
    attrs: dict[str, HtmlAttrValue] = {}
    if props.class_:
        attrs["class_"] = props.class_
    if props.id:
        attrs["id"] = props.id
    if props.lang:
        attrs["lang"] = props.lang
    if props.dir:
        attrs["dir"] = props.dir
    if props.role:
        attrs["role"] = props.role
    if props.title:
        attrs["title"] = props.title
    if props.tabindex is not None:
        attrs["tabindex"] = props.tabindex
    if props.aria:
        attrs["aria"] = props.aria
    if props.data:
        attrs["data"] = props.data
    if props.hidden:
        attrs["hidden"] = True
    return attrs


def _filter_landmark_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    unknown = set(kwargs) - _LANDMARK_SAFE_KEYS - set(LandmarkProps.model_fields)
    if unknown:
        raise TypeError(
            f"Unsupported landmark attribute(s): {sorted(unknown)}. "
            f"Allowlisted: {sorted(_LANDMARK_SAFE_KEYS)}."
        )
    role = kwargs.get("role")
    if isinstance(role, str) and role.lower() in _LANDMARK_HOSTILE_ROLES:
        raise TypeError(
            f"Landmark-hostile role={role!r} is not allowed on landmark components "
            f"(rejected: {sorted(_LANDMARK_HOSTILE_ROLES)})."
        )
    return {
        k: v
        for k, v in kwargs.items()
        if k in LandmarkProps.model_fields or k in _LANDMARK_SAFE_KEYS
    }


class Header(Component[LandmarkProps]):
    """Document or section header landmark (`<header>`)."""

    props_type = LandmarkProps
    logical_name = "Header"

    def __init__(self, *nodes: NodeLike, children: NodeLike = None, **kwargs: object) -> None:
        super().__init__(LandmarkProps(**_filter_landmark_kwargs(dict(kwargs))))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return html.header(*self._children, **_landmark_attrs(self.props))


class Main(Component[LandmarkProps]):
    """Main content landmark (`<main>`)."""

    props_type = LandmarkProps
    logical_name = "Main"

    def __init__(self, *nodes: NodeLike, children: NodeLike = None, **kwargs: object) -> None:
        super().__init__(LandmarkProps(**_filter_landmark_kwargs(dict(kwargs))))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return html.main(*self._children, **_landmark_attrs(self.props))


class Nav(Component[LandmarkProps]):
    """Navigation landmark (`<nav>`)."""

    props_type = LandmarkProps
    logical_name = "Nav"

    def __init__(self, *nodes: NodeLike, children: NodeLike = None, **kwargs: object) -> None:
        super().__init__(LandmarkProps(**_filter_landmark_kwargs(dict(kwargs))))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return html.nav(*self._children, **_landmark_attrs(self.props))


class Aside(Component[LandmarkProps]):
    """Complementary landmark (`<aside>`)."""

    props_type = LandmarkProps
    logical_name = "Aside"

    def __init__(self, *nodes: NodeLike, children: NodeLike = None, **kwargs: object) -> None:
        super().__init__(LandmarkProps(**_filter_landmark_kwargs(dict(kwargs))))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return html.aside(*self._children, **_landmark_attrs(self.props))


class Footer(Component[LandmarkProps]):
    """Contentinfo landmark (`<footer>`)."""

    props_type = LandmarkProps
    logical_name = "Footer"

    def __init__(self, *nodes: NodeLike, children: NodeLike = None, **kwargs: object) -> None:
        super().__init__(LandmarkProps(**_filter_landmark_kwargs(dict(kwargs))))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return html.footer(*self._children, **_landmark_attrs(self.props))


class Section(Component[LandmarkProps]):
    """Generic section landmark (`<section>`)."""

    props_type = LandmarkProps
    logical_name = "Section"

    def __init__(self, *nodes: NodeLike, children: NodeLike = None, **kwargs: object) -> None:
        super().__init__(LandmarkProps(**_filter_landmark_kwargs(dict(kwargs))))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return html.section(*self._children, **_landmark_attrs(self.props))
