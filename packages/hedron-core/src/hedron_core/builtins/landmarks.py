"""Landmark built-ins."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from hedron_core.component import Component
from hedron_core.html import html
from hedron_core.models import Props


class _LandmarkProps(Props):
    class_: str | None = None
    id: str | None = None


def _landmark(tag: str):
    class Landmark(Component[_LandmarkProps]):
        props_type = _LandmarkProps

        def __init__(
            self,
            *children: Any,
            class_: str | None = None,
            id: str | None = None,
            **kwargs: Any,
        ) -> None:
            # Allow passing a sequence as the sole positional child list
            if (
                len(children) == 1
                and isinstance(children[0], Sequence)
                and not isinstance(children[0], (str, bytes))
            ):
                kids = tuple(children[0])
            else:
                kids = children
            super().__init__(_LandmarkProps(class_=class_, id=id, **kwargs))
            self._children = kids
            self._tag = tag

        def render(self) -> Any:
            attrs: dict[str, Any] = {}
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
