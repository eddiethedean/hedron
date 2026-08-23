"""Semantic-preserving bounded overflow primitive (phase 0.60)."""

from __future__ import annotations

from typing import Any, Literal

from hedron_core.builtins._base import ElementProps, class_names, collect_children, mark_data
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.typing_aliases import HtmlAttrValue

__all__ = ["ScrollRegion", "ScrollRegionProps"]


class ScrollRegionProps(ElementProps):
    axis: Literal["block", "inline", "both"] = "block"
    size: Literal["sm", "md", "lg"] = "md"
    affordance: Literal["auto", "always"] = "auto"
    label: str | None = None


class ScrollRegion(Component[ScrollRegionProps]):
    """Bound a list, log, timeline, or arbitrary children without rewriting them."""

    props_type = ScrollRegionProps
    logical_name = "ScrollRegion"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        axis: Literal["block", "inline", "both"] = "block",
        size: Literal["sm", "md", "lg"] = "md",
        affordance: Literal["auto", "always"] = "auto",
        label: str | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        if axis not in ("block", "inline", "both"):
            raise ValueError("ScrollRegion axis must be block, inline, or both")
        if size not in ("sm", "md", "lg"):
            raise ValueError("ScrollRegion size must be sm, md, or lg")
        if affordance not in ("auto", "always"):
            raise ValueError("ScrollRegion affordance must be auto or always")
        if label is not None and not label.strip():
            raise ValueError("ScrollRegion label must be non-empty when provided")
        super().__init__(
            ScrollRegionProps(
                axis=axis,
                size=size,
                affordance=affordance,
                label=label,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names("hedron-scroll-region", self.props.class_),
            "data": {
                "hedron-scroll-region": "true",
                "hedron-scroll-axis": self.props.axis,
                "hedron-scroll-size": self.props.size,
                "hedron-scroll-affordance": self.props.affordance,
                **mark_data(self.props.mark),
            },
        }
        if self.props.label:
            attrs["role"] = "region"
            attrs["aria"] = {"label": self.props.label}
        return html.div(*self._children, **attrs)
