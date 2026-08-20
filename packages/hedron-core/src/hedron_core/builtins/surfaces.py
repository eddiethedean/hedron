"""Surface and status built-ins."""

from __future__ import annotations

from typing import Any, ClassVar, Literal

from hedron_core.builtins._base import ElementProps, class_names, collect_children, mark_data
from hedron_core.builtins.appearance import STATE_KINDS, StateKind, require_choice
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.typing_aliases import HtmlAttrValue


class CardProps(ElementProps):
    title: str | None = None


class Card(Component[CardProps]):
    props_type = CardProps
    slots: ClassVar[dict[str, str]] = {"header": "optional", "footer": "optional"}

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        title: str | None = None,
        header: NodeLike = None,
        footer: NodeLike = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(CardProps(title=title, id=id, class_=class_, mark=mark, **kwargs))
        self._children = collect_children(*nodes, children=children)
        if header is not None:
            self._slot_values["header"] = header
        if footer is not None:
            self._slot_values["footer"] = footer

    def render(self) -> NodeLike:
        parts: list[NodeLike] = []
        if "header" in self._slot_values:
            parts.append(html.div(self._slot_values["header"], class_="hedron-card-header"))
        elif self.props.title:
            parts.append(html.div(html.h3(self.props.title), class_="hedron-card-header"))
        parts.append(html.div(*self._children, class_="hedron-card-body"))
        if "footer" in self._slot_values:
            parts.append(html.div(self._slot_values["footer"], class_="hedron-card-footer"))
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names("hedron-card", self.props.class_),
        }
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.article(*parts, **attrs)


class BadgeProps(Props):
    text: str
    tone: Literal["neutral", "info", "success", "warning", "danger"] = "neutral"
    class_: str | None = None


class Badge(Component[BadgeProps]):
    props_type = BadgeProps

    def __init__(
        self,
        text: str,
        *,
        tone: Literal["neutral", "info", "success", "warning", "danger"] = "neutral",
        class_: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(BadgeProps(text=text, tone=tone, class_=class_, **kwargs))

    def render(self) -> NodeLike:
        return html.span(
            self.props.text,
            class_=class_names(f"hedron-badge hedron-badge-{self.props.tone}", self.props.class_),
        )


class AlertProps(Props):
    message: str
    tone: Literal["info", "success", "warning", "danger"] = "info"
    title: str | None = None
    class_: str | None = None


class Alert(Component[AlertProps]):
    props_type = AlertProps

    def __init__(
        self,
        message: str,
        *,
        tone: Literal["info", "success", "warning", "danger"] = "info",
        title: str | None = None,
        class_: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            AlertProps(message=message, tone=tone, title=title, class_=class_, **kwargs)
        )

    def render(self) -> NodeLike:
        role = "alert" if self.props.tone == "danger" else "status"
        parts: list[NodeLike] = []
        if self.props.title:
            parts.append(html.strong(self.props.title))
        parts.append(html.span(self.props.message))
        return html.div(
            *parts,
            class_=class_names(f"hedron-alert hedron-alert-{self.props.tone}", self.props.class_),
            role=role,
        )


class SkeletonProps(Props):
    lines: int = 3


class Skeleton(Component[SkeletonProps]):
    props_type = SkeletonProps

    def __init__(self, *, lines: int = 3, **kwargs: Any) -> None:
        super().__init__(SkeletonProps(lines=lines, **kwargs))

    def render(self) -> NodeLike:
        return html.div(
            *[
                html.div(class_="hedron-skeleton-line", aria={"hidden": "true"})
                for _ in range(self.props.lines)
            ],
            class_="hedron-skeleton",
            aria={"busy": "true"},
        )


# Blocking states announce themselves as alerts; the rest are polite statuses.
_STATE_ROLES: dict[str, str] = {
    "loading": "status",
    "empty": "status",
    "error": "alert",
    "permission": "alert",
    "offline": "alert",
    "success": "status",
}


class StateViewProps(ElementProps):
    kind: StateKind
    title: str
    description: str | None = None
    detail: str | None = None


class StateView(Component[StateViewProps]):
    """Unified loading / empty / error / permission / offline / success surface.

    Each state renders its own live-region role and a text label, so the state is
    never communicated by color or an icon alone.
    """

    props_type = StateViewProps
    logical_name = "StateView"
    slots: ClassVar[dict[str, str]] = {"actions": "optional"}

    def __init__(
        self,
        title: str,
        *nodes: NodeLike,
        children: NodeLike = None,
        kind: StateKind = "empty",
        description: str | None = None,
        detail: str | None = None,
        actions: NodeLike = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        require_choice(kind, STATE_KINDS, label="kind")
        super().__init__(
            StateViewProps(
                kind=kind,
                title=title,
                description=description,
                detail=detail,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)
        if actions is not None:
            self._slot_values["actions"] = actions

    def render(self) -> NodeLike:
        kind = self.props.kind
        parts: list[NodeLike] = [
            html.p(kind.capitalize(), class_="hedron-state-view-kind"),
            html.p(self.props.title, class_="hedron-state-view-title"),
        ]
        if self.props.description:
            parts.append(html.p(self.props.description, class_="hedron-state-view-description"))
        if self.props.detail:
            parts.append(html.p(self.props.detail, class_="hedron-state-view-detail"))
        if self._children:
            parts.append(html.div(*self._children, class_="hedron-state-view-body"))
        if "actions" in self._slot_values:
            parts.append(html.div(self._slot_values["actions"], class_="hedron-state-view-actions"))
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names(f"hedron-state-view hedron-state-{kind}", self.props.class_),
            "role": _STATE_ROLES[kind],
            "data": {
                "hedron-state-view": kind,
                **mark_data(self.props.mark),
            },
        }
        aria: dict[str, str | bool | int | float | None] = {}
        if kind == "loading":
            aria["busy"] = "true"
            aria["live"] = "polite"
        elif kind in {"error", "permission", "offline"}:
            aria["live"] = "assertive"
        elif kind in {"empty", "success"}:
            aria["live"] = "polite"
        if aria:
            attrs["aria"] = aria
        return html.div(*parts, **attrs)
