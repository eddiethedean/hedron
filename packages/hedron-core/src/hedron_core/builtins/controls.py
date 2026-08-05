"""Control built-ins."""

from __future__ import annotations

from typing import Any, Literal

from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose


class ButtonProps(Props):
    label: str
    type: Literal["button", "submit", "reset"] = "button"
    disabled: bool = False
    variant: Literal["primary", "secondary", "danger"] = "primary"


class Button(Component[ButtonProps]):
    props_type = ButtonProps

    def __init__(
        self,
        label: str,
        *,
        type: Literal["button", "submit", "reset"] = "button",
        disabled: bool = False,
        variant: Literal["primary", "secondary", "danger"] = "primary",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            ButtonProps(label=label, type=type, disabled=disabled, variant=variant, **kwargs)
        )

    def render(self) -> NodeLike:
        return html.button(
            self.props.label,
            type=self.props.type,
            disabled=self.props.disabled or None,
            class_=f"hedron-button hedron-button-{self.props.variant}",
        )


class LinkButtonProps(Props):
    label: str
    href: SafeUrl


class LinkButton(Component[LinkButtonProps]):
    props_type = LinkButtonProps

    def __init__(self, label: str, href: SafeUrl | str, **kwargs: Any) -> None:
        url = (
            href
            if isinstance(href, SafeUrl)
            else SafeUrl.parse(href, purpose=UrlPurpose.NAVIGATION)
        )
        super().__init__(LinkButtonProps(label=label, href=url, **kwargs))

    def render(self) -> NodeLike:
        return html.a(
            self.props.label,
            href=self.props.href,
            class_="hedron-button hedron-button-secondary",
            role="button",
        )


class IconButtonProps(Props):
    label: str
    icon: str
    type: Literal["button", "submit", "reset"] = "button"
    disabled: bool = False


class IconButton(Component[IconButtonProps]):
    props_type = IconButtonProps

    def __init__(
        self,
        label: str,
        *,
        icon: str,
        type: Literal["button", "submit", "reset"] = "button",
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            IconButtonProps(label=label, icon=icon, type=type, disabled=disabled, **kwargs)
        )

    def render(self) -> NodeLike:
        return html.button(
            html.span(self.props.icon, aria={"hidden": "true"}),
            type=self.props.type,
            disabled=self.props.disabled or None,
            class_="hedron-icon-button",
            aria={"label": self.props.label},
        )
