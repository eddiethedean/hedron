"""Icon built-in backed by the trusted icon registry (phase 0.54 / RFC-0081)."""

from __future__ import annotations

from typing import Any

from hedron_core.builtins._base import ElementProps, class_names, mark_data
from hedron_core.builtins.appearance import SIZES, Size, require_choice
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.icons import get_icon
from hedron_core.typing_aliases import HtmlAttrValue

__all__ = ["Icon"]


class IconProps(ElementProps):
    name: str
    size: Size = "md"
    title: str | None = None
    decorative: bool = False


class Icon(Component[IconProps]):
    """Render a registered trusted SVG with a bounded size vocabulary.

    Icons are decorative by default only when ``decorative=True``; otherwise the
    registry title (or an explicit ``title``) becomes the accessible name.
    """

    props_type = IconProps
    logical_name = "Icon"

    def __init__(
        self,
        name: str,
        *,
        size: Size = "md",
        title: str | None = None,
        decorative: bool = False,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        require_choice(size, SIZES, label="size")
        # Fail at construction time when the icon was never registered.
        get_icon(name)
        super().__init__(
            IconProps(
                name=name,
                size=size,
                title=title,
                decorative=decorative,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        entry = get_icon(self.props.name)
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names("hedron-icon", self.props.class_),
            "data": {
                "hedron-icon": entry.name,
                "hedron-size": self.props.size,
                **mark_data(self.props.mark),
            },
        }
        if self.props.decorative:
            attrs["aria"] = {"hidden": "true"}
        else:
            attrs["role"] = "img"
            attrs["aria"] = {"label": self.props.title or entry.title}
        return html.span(html.raw(entry.svg), **attrs)
