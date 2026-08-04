"""Surface and status built-ins."""

from __future__ import annotations

from typing import Any, Literal

from hedron_core.builtins._base import ElementProps, class_names, collect_children
from hedron_core.component import Component
from hedron_core.html import html
from hedron_core.models import Props


class CardProps(ElementProps):
    title: str | None = None


class Card(Component[CardProps]):
    props_type = CardProps
    slots = {"header": "optional", "footer": "optional"}

    def __init__(
        self,
        *nodes: Any,
        children: Any = None,
        title: str | None = None,
        header: Any = None,
        footer: Any = None,
        id: str | None = None,
        class_: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(CardProps(title=title, id=id, class_=class_, **kwargs))
        self._children = collect_children(*nodes, children=children)
        if header is not None:
            self._slot_values["header"] = header
        if footer is not None:
            self._slot_values["footer"] = footer

    def render(self) -> Any:
        parts: list[Any] = []
        if "header" in self._slot_values:
            parts.append(html.div(self._slot_values["header"], class_="hedron-card-header"))
        elif self.props.title:
            parts.append(html.div(html.h3(self.props.title), class_="hedron-card-header"))
        parts.append(html.div(*self._children, class_="hedron-card-body"))
        if "footer" in self._slot_values:
            parts.append(html.div(self._slot_values["footer"], class_="hedron-card-footer"))
        return html.article(
            *parts,
            id=self.props.id,
            class_=class_names("hedron-card", self.props.class_),
        )


class BadgeProps(Props):
    text: str
    tone: Literal["neutral", "info", "success", "warning", "danger"] = "neutral"


class Badge(Component[BadgeProps]):
    props_type = BadgeProps

    def __init__(
        self,
        text: str,
        *,
        tone: Literal["neutral", "info", "success", "warning", "danger"] = "neutral",
        **kwargs: Any,
    ) -> None:
        super().__init__(BadgeProps(text=text, tone=tone, **kwargs))

    def render(self) -> Any:
        return html.span(
            self.props.text,
            class_=f"hedron-badge hedron-badge-{self.props.tone}",
        )


class AlertProps(Props):
    message: str
    tone: Literal["info", "success", "warning", "danger"] = "info"
    title: str | None = None


class Alert(Component[AlertProps]):
    props_type = AlertProps

    def __init__(
        self,
        message: str,
        *,
        tone: Literal["info", "success", "warning", "danger"] = "info",
        title: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(AlertProps(message=message, tone=tone, title=title, **kwargs))

    def render(self) -> Any:
        role = "alert" if self.props.tone == "danger" else "status"
        parts: list[Any] = []
        if self.props.title:
            parts.append(html.strong(self.props.title))
        parts.append(html.span(self.props.message))
        return html.div(
            *parts,
            class_=f"hedron-alert hedron-alert-{self.props.tone}",
            role=role,
        )


class SkeletonProps(Props):
    lines: int = 3


class Skeleton(Component[SkeletonProps]):
    props_type = SkeletonProps

    def __init__(self, *, lines: int = 3, **kwargs: Any) -> None:
        super().__init__(SkeletonProps(lines=lines, **kwargs))

    def render(self) -> Any:
        return html.div(
            *[
                html.div(class_="hedron-skeleton-line", aria={"hidden": "true"})
                for _ in range(self.props.lines)
            ],
            class_="hedron-skeleton",
            aria={"busy": "true"},
        )
