"""Control built-ins."""

from __future__ import annotations

from typing import Literal

from hedron_core.builtins._base import class_names
from hedron_core.builtins.appearance import (
    Appearance,
    Emphasis,
    Size,
    Width,
    appearance_data,
    require_choice,
)
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose

_VARIANT_MAP: dict[str, tuple[str, str]] = {
    "primary": ("primary", "solid"),
    "secondary": ("secondary", "outline"),
    "danger": ("danger", "solid"),
}


def _button_emphasis_appearance(
    *,
    variant: str,
    emphasis: str | None,
    appearance: str | None,
) -> tuple[str, str, str]:
    """Return ``(variant_class, emphasis, appearance)`` with compat defaults."""
    mapped_emphasis, mapped_appearance = _VARIANT_MAP[variant]
    resolved_emphasis = emphasis or mapped_emphasis
    resolved_appearance = appearance or mapped_appearance
    require_choice(
        resolved_emphasis,
        ("primary", "secondary", "danger", "neutral"),
        label="emphasis",
    )
    require_choice(
        resolved_appearance,
        ("solid", "outline", "soft", "ghost", "plain", "raised"),
        label="appearance",
    )
    return variant, resolved_emphasis, resolved_appearance


class ButtonProps(Props):
    label: str
    type: Literal["button", "submit", "reset"] = "button"
    disabled: bool = False
    variant: Literal["primary", "secondary", "danger"] = "primary"
    size: Size | None = None
    appearance: Appearance | None = None
    emphasis: Emphasis | None = None
    width: Width | None = None
    leading_icon: str | None = None
    id: str | None = None
    class_: str | None = None


class Button(Component[ButtonProps]):
    props_type = ButtonProps

    def __init__(
        self,
        label: str,
        *,
        type: Literal["button", "submit", "reset"] = "button",
        disabled: bool = False,
        variant: Literal["primary", "secondary", "danger"] = "primary",
        size: Size | None = None,
        appearance: Appearance | None = None,
        emphasis: Emphasis | None = None,
        width: Width | None = None,
        leading_icon: str | None = None,
        id: str | None = None,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            ButtonProps(
                label=label,
                type=type,
                disabled=disabled,
                variant=variant,
                size=size,
                appearance=appearance,
                emphasis=emphasis,
                width=width,
                leading_icon=leading_icon,
                id=id,
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        children: list[NodeLike] = []
        if self.props.leading_icon:
            from hedron_core.builtins.icon import Icon

            children.append(Icon(self.props.leading_icon, size="sm", decorative=True))
            children.append(html.span(self.props.label, class_="hedron-button-label"))
        else:
            children.append(self.props.label)
        variant, emphasis, appearance = _button_emphasis_appearance(
            variant=self.props.variant,
            emphasis=self.props.emphasis,
            appearance=self.props.appearance,
        )
        data = appearance_data(
            size=self.props.size,
            appearance=appearance,
            emphasis=emphasis,
            width=self.props.width,
        )
        return html.button(
            *children,
            type=self.props.type,
            disabled=self.props.disabled or None,
            id=self.props.id,
            class_=class_names(f"hedron-button hedron-button-{variant}", self.props.class_),
            data=data or None,
        )


class LinkButtonProps(Props):
    label: str
    href: SafeUrl
    size: Size | None = None
    appearance: Appearance | None = None
    emphasis: Emphasis | None = None
    id: str | None = None
    class_: str | None = None


class LinkButton(Component[LinkButtonProps]):
    props_type = LinkButtonProps

    def __init__(
        self,
        label: str,
        href: SafeUrl | str,
        *,
        size: Size | None = None,
        appearance: Appearance | None = None,
        emphasis: Emphasis | None = None,
        id: str | None = None,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        url = (
            href
            if isinstance(href, SafeUrl)
            else SafeUrl.parse(href, purpose=UrlPurpose.NAVIGATION)
        )
        super().__init__(
            LinkButtonProps(
                label=label,
                href=url,
                size=size,
                appearance=appearance,
                emphasis=emphasis,
                id=id,
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        data = appearance_data(
            size=self.props.size,
            appearance=self.props.appearance or "outline",
            emphasis=self.props.emphasis or "secondary",
        )
        return html.a(
            self.props.label,
            href=self.props.href,
            id=self.props.id,
            class_=class_names("hedron-button hedron-button-secondary", self.props.class_),
            role="button",
            data=data or None,
        )


class IconButtonProps(Props):
    label: str
    icon: str
    type: Literal["button", "submit", "reset"] = "button"
    disabled: bool = False
    size: Size | None = None
    appearance: Appearance | None = None
    emphasis: Emphasis | None = None
    id: str | None = None
    class_: str | None = None


class IconButton(Component[IconButtonProps]):
    props_type = IconButtonProps

    def __init__(
        self,
        label: str,
        *,
        icon: str,
        type: Literal["button", "submit", "reset"] = "button",
        disabled: bool = False,
        size: Size | None = None,
        appearance: Appearance | None = None,
        emphasis: Emphasis | None = None,
        id: str | None = None,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            IconButtonProps(
                label=label,
                icon=icon,
                type=type,
                disabled=disabled,
                size=size,
                appearance=appearance,
                emphasis=emphasis,
                id=id,
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        data = appearance_data(
            size=self.props.size,
            appearance=self.props.appearance,
            emphasis=self.props.emphasis,
        )
        return html.button(
            html.span(self.props.icon, aria={"hidden": "true"}),
            type=self.props.type,
            disabled=self.props.disabled or None,
            id=self.props.id,
            class_=class_names("hedron-icon-button", self.props.class_),
            aria={"label": self.props.label},
            data=data or None,
        )
