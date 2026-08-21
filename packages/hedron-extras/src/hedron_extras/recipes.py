"""Lightweight presentation recipes for phase 0.16."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from hedron_core.builtins._base import ElementProps, class_names, mark_data
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose


def _nav(href: str) -> SafeUrl:
    return SafeUrl.parse(href, purpose=UrlPurpose.NAVIGATION)


def _asset(src: str) -> SafeUrl:
    return SafeUrl.parse(src, purpose=UrlPurpose.ASSET)


class AvatarProfileProps(ElementProps):
    name: str
    image_src: SafeUrl | None = None
    caption: str | None = None
    href: SafeUrl | None = None


class AvatarProfile(Component[AvatarProfileProps]):
    props_type = AvatarProfileProps
    logical_name = "AvatarProfile"
    distribution = "hedron-extras"

    def __init__(
        self,
        name: str,
        *,
        image_src: str | None = None,
        caption: str | None = None,
        href: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            AvatarProfileProps(
                name=name,
                image_src=None if image_src is None else _asset(image_src),
                caption=caption,
                href=None if href is None else _nav(href),
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        from hedron_core.builtins.identity import Identity

        identity = Identity(
            self.props.name,
            detail=self.props.caption,
            href=self.props.href,
            image_src=self.props.image_src,
        )
        return html.div(
            identity,
            class_=class_names("hedron-avatar-profile", self.props.class_),
            id=self.props.id,
            data={**mark_data(self.props.mark), "hedron-recipe": "avatar"},
        )


class BadgeLinkProps(ElementProps):
    label: str
    href: SafeUrl
    tone: str = "neutral"


class BadgeLink(Component[BadgeLinkProps]):
    props_type = BadgeLinkProps
    logical_name = "BadgeLink"
    distribution = "hedron-extras"

    def __init__(self, label: str, href: str, *, tone: str = "neutral", **kwargs: Any) -> None:
        super().__init__(BadgeLinkProps(label=label, href=_nav(href), tone=tone, **kwargs))

    def render(self) -> NodeLike:
        return html.a(
            self.props.label,
            href=self.props.href,
            class_=class_names("hedron-badge-link", self.props.class_),
            id=self.props.id,
            data={**mark_data(self.props.mark), "tone": self.props.tone, "hedron-recipe": "badge"},
        )


class MetricCardProps(ElementProps):
    label: str
    value: str
    hint: str | None = None


class MetricCard(Component[MetricCardProps]):
    props_type = MetricCardProps
    logical_name = "MetricCard"
    distribution = "hedron-extras"

    def __init__(self, label: str, value: str, *, hint: str | None = None, **kwargs: Any) -> None:
        super().__init__(MetricCardProps(label=label, value=value, hint=hint, **kwargs))

    def render(self) -> NodeLike:
        parts: list[NodeLike] = [
            html.dt(self.props.label),
            html.dd(self.props.value),
        ]
        if self.props.hint:
            parts.append(html.dd(self.props.hint, class_="hedron-metric-hint"))
        return html.dl(
            *parts,
            class_=class_names("hedron-metric-card", self.props.class_),
            id=self.props.id,
            data={**mark_data(self.props.mark), "hedron-recipe": "metric"},
        )


class TodoItem(Props):
    id: str
    label: str
    done: bool = False


class TodoListProps(ElementProps):
    items: list[TodoItem]
    name: str = "todo"


class TodoList(Component[TodoListProps]):
    props_type = TodoListProps
    logical_name = "TodoList"
    distribution = "hedron-extras"

    def __init__(
        self,
        items: Sequence[TodoItem | dict[str, Any]],
        *,
        name: str = "todo",
        **kwargs: Any,
    ) -> None:
        parsed = [i if isinstance(i, TodoItem) else TodoItem.model_validate(i) for i in items]
        super().__init__(TodoListProps(items=parsed, name=name, **kwargs))

    def render(self) -> NodeLike:
        rows = [
            html.li(
                html.label(
                    html.input(
                        type="checkbox",
                        name=self.props.name,
                        value=item.id,
                        checked=item.done or None,
                    ),
                    html.span(item.label),
                )
            )
            for item in self.props.items
        ]
        return html.ul(
            *rows,
            class_=class_names("hedron-todo-list", self.props.class_),
            id=self.props.id,
            data={**mark_data(self.props.mark), "hedron-recipe": "todo"},
        )
