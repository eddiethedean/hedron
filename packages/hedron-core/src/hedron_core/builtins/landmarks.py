"""Landmark built-ins."""

from __future__ import annotations

from typing import Any

from hedron_core.builtins._base import collect_children
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.typing_aliases import HtmlAttrValue


class _LandmarkProps(Props):
    class_: str | None = None
    id: str | None = None


def _landmark(tag: str):
    class Landmark(Component[_LandmarkProps]):
        props_type = _LandmarkProps

        def __init__(
            self,
            *nodes: NodeLike,
            children: NodeLike = None,
            class_: str | None = None,
            id: str | None = None,
            **kwargs: Any,
        ) -> None:
            super().__init__(_LandmarkProps(class_=class_, id=id, **kwargs))
            self._children = collect_children(*nodes, children=children)
            self._tag = tag

        def render(self) -> NodeLike:
            attrs: dict[str, HtmlAttrValue] = {}
            if self.props.class_:
                attrs["class_"] = self.props.class_
            if self.props.id:
                attrs["id"] = self.props.id
            return getattr(html, self._tag)(*self._children, **attrs)

    Landmark.__name__ = tag.capitalize() if tag != "nav" else "Nav"
    Landmark.__qualname__ = Landmark.__name__
    Landmark.logical_name = Landmark.__name__
    return Landmark


Header = _landmark("header")
Main = _landmark("main")
Nav = _landmark("nav")
Aside = _landmark("aside")
Footer = _landmark("footer")
Section = _landmark("section")
