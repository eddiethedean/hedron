"""Surface chrome built-ins for phase 0.15 (RFC-0035)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from hedron_core.builtins._base import (
    ElementProps,
    class_names,
    collect_children,
    dom_id_part,
    mark_data,
)
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue


class CarouselProps(ElementProps):
    label: str = "Carousel"


class Carousel(Component[CarouselProps]):
    """No-JS carousel: all slides as a list with prev/next fragment links."""

    props_type = CarouselProps
    logical_name = "Carousel"

    def __init__(
        self,
        slides: Sequence[tuple[str, NodeLike] | NodeLike],
        *,
        id: str | None = None,
        label: str = "Carousel",
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(CarouselProps(id=id, label=label, class_=class_, mark=mark, **kwargs))
        normalized: list[tuple[str, NodeLike]] = []
        for index, slide in enumerate(slides):
            if isinstance(slide, tuple) and len(slide) == 2 and isinstance(slide[0], str):
                normalized.append((slide[0], slide[1]))
            else:
                normalized.append((f"slide-{index + 1}", slide))  # type: ignore[arg-type]
        if not normalized:
            raise ValueError("Carousel requires at least one slide")
        self._slides = tuple(normalized)

    def render(self) -> NodeLike:
        carousel_id = self.props.id or f"carousel-{self.render_instance_id()[2:10]}"
        items: list[NodeLike] = []
        slide_ids: list[str] = []
        for slide_key, content in self._slides:
            slide_id = f"{carousel_id}-{dom_id_part(slide_key)}"
            slide_ids.append(slide_id)
            items.append(html.li(content, id=slide_id, class_="hedron-carousel-slide"))
        nav_links: list[NodeLike] = []
        for index, slide_id in enumerate(slide_ids):
            prev_id = slide_ids[(index - 1) % len(slide_ids)]
            next_id = slide_ids[(index + 1) % len(slide_ids)]
            nav_links.append(
                html.li(
                    html.a(
                        "Previous",
                        href=SafeUrl.parse(f"#{prev_id}", purpose=UrlPurpose.NAVIGATION),
                        class_="hedron-carousel-prev",
                        aria={"label": f"Previous slide from {slide_id}"},
                    ),
                    html.a(
                        "Next",
                        href=SafeUrl.parse(f"#{next_id}", purpose=UrlPurpose.NAVIGATION),
                        class_="hedron-carousel-next",
                        aria={"label": f"Next slide from {slide_id}"},
                    ),
                    class_="hedron-carousel-nav-item",
                    data={"for-slide": slide_id},
                )
            )
        attrs: dict[str, HtmlAttrValue] = {
            "id": carousel_id,
            "class_": class_names("hedron-carousel", self.props.class_),
            "aria": {"label": self.props.label},
            "data": {"hedron-carousel": "true", **mark_data(self.props.mark)},
        }
        return html.section(
            html.ul(*items, class_="hedron-carousel-slides"),
            html.nav(
                html.ul(*nav_links, class_="hedron-carousel-nav"),
                aria={"label": f"{self.props.label} controls"},
            ),
            **attrs,
        )


class TimelineProps(ElementProps):
    label: str = "Timeline"


class Timeline(Component[TimelineProps]):
    """Ordered timeline entries with time / label / body."""

    props_type = TimelineProps
    logical_name = "Timeline"

    def __init__(
        self,
        entries: Sequence[tuple[str, str, NodeLike] | dict[str, object]],
        *,
        id: str | None = None,
        label: str = "Timeline",
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(TimelineProps(id=id, label=label, class_=class_, mark=mark, **kwargs))
        normalized: list[tuple[str, str, NodeLike]] = []
        for entry in entries:
            if isinstance(entry, dict):
                normalized.append(
                    (
                        str(entry.get("time", "")),
                        str(entry.get("label", "")),
                        entry.get("body"),  # type: ignore[arg-type]
                    )
                )
            else:
                normalized.append((entry[0], entry[1], entry[2]))
        self._entries = tuple(normalized)

    def render(self) -> NodeLike:
        items: list[NodeLike] = []
        for _index, (time_text, label, body) in enumerate(self._entries):
            parts: list[NodeLike] = []
            if time_text:
                parts.append(html.time(time_text, class_="hedron-timeline-time"))
            if label:
                parts.append(html.span(label, class_="hedron-timeline-label"))
            if body is not None:
                parts.append(html.div(body, class_="hedron-timeline-body"))
            items.append(html.li(*parts, class_="hedron-timeline-entry"))
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names("hedron-timeline", self.props.class_),
            "aria": {"label": self.props.label},
        }
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.ol(*items, **attrs)


class ContextMenuProps(ElementProps):
    label: str = "Actions"
    overflow_label: str = "More actions"


class ContextMenu(Component[ContextMenuProps]):
    """Native popover/menu plus Required overflow-button alternative for the same actions."""

    props_type = ContextMenuProps
    logical_name = "ContextMenu"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        label: str = "Actions",
        overflow_label: str = "More actions",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            ContextMenuProps(
                label=label,
                overflow_label=overflow_label,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._actions = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        root_id = self.props.id or f"context-menu-{self.render_instance_id()[2:10]}"
        menu_id = f"{root_id}-menu"
        attrs: dict[str, HtmlAttrValue] = {
            "id": root_id,
            "class_": class_names("hedron-context-menu", self.props.class_),
            "data": {"hedron-context-menu": "true", **mark_data(self.props.mark)},
        }
        return html.div(
            html.button(
                self.props.label,
                type="button",
                popovertarget=menu_id,
                popovertargetaction="toggle",
                class_="hedron-context-menu-trigger",
                aria={"haspopup": "menu", "controls": menu_id},
            ),
            # Required non-pointer / overflow alternative for the same actions menu.
            html.button(
                self.props.overflow_label,
                type="button",
                popovertarget=menu_id,
                popovertargetaction="toggle",
                class_="hedron-context-menu-overflow",
                aria={
                    "haspopup": "menu",
                    "controls": menu_id,
                    "label": self.props.overflow_label,
                },
            ),
            html.menu(
                *self._actions,
                id=menu_id,
                popover="auto",
                class_="hedron-context-menu-panel",
            ),
            **attrs,
        )


class PopoverProps(ElementProps):
    label: str = "Open"
    mode: Literal["popover", "details"] = "popover"


class Popover(Component[PopoverProps]):
    """Wrapper using the popover attribute, with details/summary fallback."""

    props_type = PopoverProps
    logical_name = "Popover"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        label: str = "Open",
        mode: Literal["popover", "details"] = "popover",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            PopoverProps(label=label, mode=mode, id=id, class_=class_, mark=mark, **kwargs)
        )
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        root_id = self.props.id or f"popover-{self.render_instance_id()[2:10]}"
        panel_id = f"{root_id}-panel"
        data: dict[str, str | bool | int | float | None] = {
            "hedron-popover": "true",
            **mark_data(self.props.mark),
        }
        if self.props.mode == "details":
            return html.details(
                html.summary(self.props.label),
                html.div(*self._children, class_="hedron-popover-body"),
                id=root_id,
                class_=class_names("hedron-popover hedron-popover-details", self.props.class_),
                data=data,
            )
        return html.div(
            html.button(
                self.props.label,
                type="button",
                popovertarget=panel_id,
                popovertargetaction="toggle",
                class_="hedron-popover-trigger",
            ),
            html.div(
                *self._children,
                id=panel_id,
                popover="auto",
                class_="hedron-popover-panel",
            ),
            id=root_id,
            class_=class_names("hedron-popover", self.props.class_),
            data=data,
        )


class ActionDockProps(ElementProps):
    label: str = "Actions"
    placement: Literal["bottom", "aside"] = "bottom"


class ActionDock(Component[ActionDockProps]):
    """Sticky footer/aside region for persistent actions."""

    props_type = ActionDockProps
    logical_name = "ActionDock"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        label: str = "Actions",
        placement: Literal["bottom", "aside"] = "bottom",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            ActionDockProps(
                label=label,
                placement=placement,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        base = (
            "hedron-action-dock hedron-bottom-dock"
            if self.props.placement == "bottom"
            else "hedron-action-dock hedron-aside-dock"
        )
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names(base, self.props.class_),
            "aria": {"label": self.props.label},
            "data": {
                "hedron-dock": self.props.placement,
                **mark_data(self.props.mark),
            },
        }
        if self.props.placement == "aside":
            return html.aside(*self._children, **attrs)
        return html.footer(*self._children, **attrs)


class BottomDock(ActionDock):
    """Sticky bottom action dock (ActionDock placement=bottom)."""

    logical_name = "BottomDock"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        label: str = "Actions",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            *nodes,
            children=children,
            label=label,
            placement="bottom",
            id=id,
            class_=class_,
            mark=mark,
            **kwargs,
        )


class TooltipProps(ElementProps):
    text: str


class Tooltip(Component[TooltipProps]):
    """Native title tooltip wrapper around children."""

    props_type = TooltipProps
    logical_name = "Tooltip"

    def __init__(
        self,
        text: str,
        *nodes: NodeLike,
        children: NodeLike = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(TooltipProps(text=text, id=id, class_=class_, mark=mark, **kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names("hedron-tooltip", self.props.class_),
            "title": self.props.text,
        }
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.span(*self._children, **attrs)


class HelpProps(ElementProps):
    text: str
    for_: str | None = None


class Help(Component[HelpProps]):
    """Visible help text intended for ``aria-describedby`` pairing."""

    props_type = HelpProps
    logical_name = "Help"

    def __init__(
        self,
        text: str,
        *,
        id: str | None = None,
        for_: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(HelpProps(text=text, id=id, for_=for_, class_=class_, mark=mark, **kwargs))

    def render(self) -> NodeLike:
        help_id = self.props.id or (
            f"help-{dom_id_part(self.props.for_ or 'hint')}-{self.render_instance_id()[2:10]}"
        )
        data = mark_data(self.props.mark)
        if self.props.for_:
            data = {**data, "for": self.props.for_}
        attrs: dict[str, HtmlAttrValue] = {
            "id": help_id,
            "class_": class_names("hedron-help", self.props.class_),
            "role": "note",
        }
        if data:
            attrs["data"] = data
        return html.p(self.props.text, **attrs)


class ConfirmButtonProps(Props):
    label: str
    confirm: str
    type: Literal["button", "submit", "reset"] = "button"
    disabled: bool = False
    variant: Literal["primary", "secondary", "danger"] = "danger"
    mark: str | None = None


class ConfirmButton(Component[ConfirmButtonProps]):
    """Button with hx-confirm / data-confirm. Confirmation is not authorization."""

    props_type = ConfirmButtonProps
    logical_name = "ConfirmButton"

    def __init__(
        self,
        label: str,
        *,
        confirm: str,
        type: Literal["button", "submit", "reset"] = "button",
        disabled: bool = False,
        variant: Literal["primary", "secondary", "danger"] = "danger",
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            ConfirmButtonProps(
                label=label,
                confirm=confirm,
                type=type,
                disabled=disabled,
                variant=variant,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "type": self.props.type,
            "disabled": self.props.disabled or None,
            "class_": f"hedron-button hedron-button-{self.props.variant} hedron-confirm-button",
            "hx-confirm": self.props.confirm,
            "data": {
                "confirm": self.props.confirm,
                "hedron-confirm": "true",
                **mark_data(self.props.mark),
            },
        }
        return html.button(self.props.label, **attrs)


class ClipboardCopyProps(Props):
    text: str
    label: str = "Copy"
    mark: str | None = None


class ClipboardCopy(Component[ClipboardCopyProps]):
    """Copy-to-clipboard button via data attribute (write-only; no clipboard read)."""

    props_type = ClipboardCopyProps
    logical_name = "ClipboardCopy"

    def __init__(
        self,
        text: str,
        *,
        label: str = "Copy",
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        if len(text) > 100_000:
            raise ValueError("ClipboardCopy text exceeds 100000 character budget")
        super().__init__(ClipboardCopyProps(text=text, label=label, mark=mark, **kwargs))

    def render(self) -> NodeLike:
        return html.button(
            self.props.label,
            type="button",
            class_="hedron-clipboard-copy",
            data={
                "copy-text": self.props.text,
                "hedron-clipboard-copy": "true",
                **mark_data(self.props.mark),
            },
            aria={"label": self.props.label},
        )
