"""Surface and status built-ins."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, Literal

from hedron_core.builtins._base import ElementProps, class_names, collect_children, mark_data
from hedron_core.builtins.appearance import (
    STATE_KINDS,
    Appearance,
    Density,
    Elevation,
    Padding,
    Size,
    StateKind,
    appearance_data,
    require_choice,
)
from hedron_core.builtins.style_scope import presentation_data
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.presentation_064 import application_style_hook_data
from hedron_core.typing_aliases import HtmlAttrValue


class SurfaceProps(ElementProps):
    appearance: Appearance | None = None
    density: Density | None = None
    padding: Padding | None = None
    elevation: Elevation | None = None


class Surface(Component[SurfaceProps]):
    """Visual grouping surface (not a landmark). Prefer Section for landmarks."""

    props_type = SurfaceProps
    logical_name = "Surface"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        appearance: Appearance | None = None,
        density: Density | None = None,
        padding: Padding | None = None,
        elevation: Elevation | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        if appearance is not None:
            require_choice(appearance, ("plain", "raised"), label="appearance")
        super().__init__(
            SurfaceProps(
                appearance=appearance,
                density=density,
                padding=padding,
                elevation=elevation,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        data = {
            "hedron-surface": "true",
            **appearance_data(
                appearance=self.props.appearance,
                density=self.props.density,
                padding=self.props.padding,
                elevation=self.props.elevation,
            ),
            **mark_data(self.props.mark),
        }
        return html.div(
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-surface", self.props.class_),
            data=data,
        )


@dataclass(frozen=True, slots=True)
class AmbientLayer:
    """A bounded, decorative layer for an :class:`AmbientCanvas`.

    Layers are data-only and are always rendered behind semantic children. The
    finite vocabulary keeps the resulting CSS token-addressable and exportable.
    """

    pattern: Literal["radial", "dots", "grid", "mesh"] = "radial"
    tone: Literal["accent", "muted", "neutral"] = "accent"
    intensity: Literal["subtle", "soft"] = "subtle"
    placement: Literal["flow", "surface", "fixed-canvas"] = "surface"
    order: int = 0
    scale: Literal["sm", "md", "lg"] = "md"

    def __post_init__(self) -> None:
        for value, choices, label in (
            (self.pattern, ("radial", "dots", "grid", "mesh"), "pattern"),
            (self.tone, ("accent", "muted", "neutral"), "tone"),
            (self.intensity, ("subtle", "soft"), "intensity"),
            (self.placement, ("flow", "surface", "fixed-canvas"), "placement"),
            (self.scale, ("sm", "md", "lg"), "scale"),
        ):
            require_choice(value, choices, label=label)
        if isinstance(self.order, bool) or not 0 <= self.order <= 8:
            raise ValueError("AmbientLayer order must be an integer between 0 and 8")


class AmbientBackdropProps(ElementProps):
    pattern: Literal["radial", "dots", "grid", "mesh"] = "radial"
    tone: Literal["accent", "muted", "neutral"] = "accent"
    intensity: Literal["subtle", "soft"] = "subtle"


class AmbientBackdrop(Component[AmbientBackdropProps]):
    """Finite, decorative page/surface treatment with semantic content above it."""

    props_type = AmbientBackdropProps
    logical_name = "AmbientBackdrop"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        pattern: Literal["radial", "dots", "grid", "mesh"] = "radial",
        tone: Literal["accent", "muted", "neutral"] = "accent",
        intensity: Literal["subtle", "soft"] = "subtle",
        layers: Sequence[AmbientLayer] | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        require_choice(pattern, ("radial", "dots", "grid", "mesh"), label="pattern")
        require_choice(tone, ("accent", "muted", "neutral"), label="tone")
        require_choice(intensity, ("subtle", "soft"), label="intensity")
        resolved_layers = tuple(layers or ())
        if not resolved_layers:
            resolved_layers = (AmbientLayer(pattern=pattern, tone=tone, intensity=intensity),)
        super().__init__(
            AmbientBackdropProps(
                pattern=pattern,
                tone=tone,
                intensity=intensity,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._layers = tuple(sorted(resolved_layers, key=lambda layer: layer.order))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        decorations = tuple(
            html.div(
                aria={"hidden": "true"},
                class_="hedron-ambient-backdrop-decoration",
                data={
                    "hedron-ambient-layer": str(index),
                    "hedron-ambient-pattern": layer.pattern,
                    "hedron-ambient-tone": layer.tone,
                    "hedron-ambient-intensity": layer.intensity,
                    "hedron-ambient-placement": layer.placement,
                    "hedron-ambient-order": layer.order,
                    "hedron-ambient-scale": layer.scale,
                },
            )
            for index, layer in enumerate(self._layers)
        )
        return html.div(
            *decorations,
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-ambient-backdrop", self.props.class_),
            data={"hedron-ambient-backdrop": "true", "hedron-mark": self.props.mark},
        )


class AmbientCanvas(AmbientBackdrop):
    """Document-level alias for composing ordered ambient layers."""

    logical_name = "AmbientCanvas"


class CardProps(ElementProps):
    title: str | None = None
    appearance: Appearance | None = None
    density: Density | None = None
    padding: Padding | None = None
    elevation: Elevation | None = None


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
        appearance: Appearance | None = None,
        density: Density | None = None,
        padding: Padding | None = None,
        elevation: Elevation | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            CardProps(
                title=title,
                appearance=appearance,
                density=density,
                padding=padding,
                elevation=elevation,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)
        if header is not None:
            self._slot_values["header"] = header
        if footer is not None:
            self._slot_values["footer"] = footer

    def render(self) -> NodeLike:
        parts: list[NodeLike] = []
        if "header" in self._slot_values:
            parts.append(
                html.div(
                    self._slot_values["header"],
                    class_="hedron-card-header",
                    data={
                        **application_style_hook_data("Card", "heading", state="default"),
                        **presentation_data("Card.heading"),
                    },
                )
            )
        elif self.props.title:
            parts.append(
                html.div(
                    html.h3(self.props.title),
                    class_="hedron-card-header",
                    data={
                        **application_style_hook_data("Card", "heading", state="default"),
                        **presentation_data("Card.heading"),
                    },
                )
            )
        parts.append(
            html.div(
                *self._children,
                class_="hedron-card-body",
                data={
                    **application_style_hook_data("Card", "supporting-copy", state="default"),
                    **presentation_data("Card.supporting-copy"),
                },
            )
        )
        if "footer" in self._slot_values:
            parts.append(
                html.div(
                    self._slot_values["footer"],
                    class_="hedron-card-footer",
                    data={
                        **application_style_hook_data("Card", "metadata", state="default"),
                        **presentation_data("Card.metadata"),
                    },
                )
            )
        data = {
            **appearance_data(
                appearance=self.props.appearance,
                density=self.props.density,
                padding=self.props.padding,
                elevation=self.props.elevation,
            ),
            **mark_data(self.props.mark),
        }
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names("hedron-card", self.props.class_),
        }
        if data:
            attrs["data"] = data
        return html.article(*parts, **attrs)


class BadgeProps(Props):
    text: str
    tone: Literal["neutral", "info", "success", "warning", "danger"] = "neutral"
    size: Size | None = None
    appearance: Appearance | None = None
    class_: str | None = None


class Badge(Component[BadgeProps]):
    props_type = BadgeProps

    def __init__(
        self,
        text: str,
        *,
        tone: Literal["neutral", "info", "success", "warning", "danger"] = "neutral",
        size: Size | None = None,
        appearance: Appearance | None = None,
        class_: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            BadgeProps(
                text=text,
                tone=tone,
                size=size,
                appearance=appearance,
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        data = appearance_data(
            size=self.props.size,
            appearance=self.props.appearance,
            tone=self.props.tone,
        )
        return html.span(
            self.props.text,
            class_=class_names(f"hedron-badge hedron-badge-{self.props.tone}", self.props.class_),
            data=data or None,
        )


class AlertProps(Props):
    message: str
    tone: Literal["info", "success", "warning", "danger"] = "info"
    title: str | None = None
    size: Size | None = None
    appearance: Appearance | None = None
    class_: str | None = None


class Alert(Component[AlertProps]):
    props_type = AlertProps

    def __init__(
        self,
        message: str,
        *,
        tone: Literal["info", "success", "warning", "danger"] = "info",
        title: str | None = None,
        size: Size | None = None,
        appearance: Appearance | None = None,
        class_: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            AlertProps(
                message=message,
                tone=tone,
                title=title,
                size=size,
                appearance=appearance,
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        role = "alert" if self.props.tone == "danger" else "status"
        parts: list[NodeLike] = []
        if self.props.title:
            parts.append(html.strong(self.props.title))
        parts.append(html.span(self.props.message))
        data = appearance_data(
            size=self.props.size,
            appearance=self.props.appearance,
            tone=self.props.tone,
        )
        return html.div(
            *parts,
            class_=class_names(f"hedron-alert hedron-alert-{self.props.tone}", self.props.class_),
            role=role,
            data=data or None,
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
