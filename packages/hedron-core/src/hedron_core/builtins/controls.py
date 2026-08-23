"""Control built-ins."""

from __future__ import annotations

import re
from collections.abc import Mapping
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
from hedron_core.typing_aliases import HtmlAttrValue

_VARIANT_MAP: dict[str, tuple[str, str]] = {
    "primary": ("primary", "solid"),
    "secondary": ("secondary", "outline"),
    "danger": ("danger", "solid"),
}

_ARIA_ATTR_RE = re.compile(r"^aria-[a-z][a-z0-9-]*$")
_DATA_ATTR_RE = re.compile(r"^data-[a-z0-9][a-z0-9_.:-]*$")
_APPROVED_HX_ATTRS = frozenset(
    {
        "hx-get",
        "hx-post",
        "hx-put",
        "hx-patch",
        "hx-delete",
        "hx-target",
        "hx-swap",
        "hx-trigger",
        "hx-indicator",
        "hx-select",
        "hx-select-oob",
        "hx-confirm",
        "hx-disabled-elt",
        "hx-include",
        "hx-validate",
        "hx-vals",
        "hx-headers",
        "hx-push-url",
        "hx-replace-url",
        "popovertarget",
        "popovertargetaction",
    }
)
_GLOBAL_ATTRS = frozenset(
    {
        "accesskey",
        "autocapitalize",
        "class",  # rejected below because the typed component owns it
        "contenteditable",
        "dir",
        "draggable",
        "enterkeyhint",
        "hidden",
        "inert",
        "lang",
        "part",
        "role",
        "slot",
        "spellcheck",
        "tabindex",
        "translate",
    }
)


def _validated_control_attrs(
    attrs: Mapping[str, HtmlAttrValue] | None,
    *,
    tag: str,
) -> dict[str, HtmlAttrValue]:
    """Validate the bounded attribute seam shared by typed controls.

    Final normalization remains owned by ``html.*``. This preflight prevents
    structural overrides and malformed ARIA/data/HTMX names from becoming an
    accidental escape hatch while retaining the common native attributes.
    """
    if attrs is None:
        return {}
    out: dict[str, HtmlAttrValue] = {}
    structural = {"type", "disabled", "href", "class", "id"}
    for raw_name, value in attrs.items():
        if not isinstance(raw_name, str):
            raise ValueError("typed control attribute names must be strings")
        name = raw_name.lower()
        if name in structural:
            raise ValueError(f"typed control attribute {raw_name!r} is owned by the component")
        if name.startswith("on") or name == "style" or name.startswith("hx-on"):
            raise ValueError(f"unsafe typed control attribute {raw_name!r}")
        if name.startswith("aria-"):
            if not _ARIA_ATTR_RE.fullmatch(name):
                raise ValueError(f"malformed ARIA attribute {raw_name!r}")
        elif name.startswith("data-"):
            if not _DATA_ATTR_RE.fullmatch(name):
                raise ValueError(f"malformed data attribute {raw_name!r}")
        elif name.startswith("hx-") and name not in _APPROVED_HX_ATTRS:
            raise ValueError(f"HTMX attribute {raw_name!r} is not allowlisted")
        elif (
            name not in _APPROVED_HX_ATTRS
            and name not in _GLOBAL_ATTRS
            and name
            not in {
                "title",
                "name",
                "value",
                "form",
                "formaction",
                "formmethod",
                "formtarget",
                "formnovalidate",
                "aria-label",
            }
        ):
            raise ValueError(f"typed control attribute {raw_name!r} is not allowlisted")
        out[raw_name] = value
    return out


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
    attrs: Mapping[str, HtmlAttrValue] | None = None


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
        attrs: Mapping[str, HtmlAttrValue] | None = None,
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
                attrs=attrs,
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
        attrs: dict[str, HtmlAttrValue] = {
            "type": self.props.type,
            "disabled": self.props.disabled or None,
            "id": self.props.id,
            "class_": class_names(f"hedron-button hedron-button-{variant}", self.props.class_),
            "data": data or None,
        }
        attrs.update(_validated_control_attrs(self.props.attrs, tag="button"))
        return html.button(*children, **attrs)


class LinkButtonProps(Props):
    label: str
    href: SafeUrl
    size: Size | None = None
    width: Width | None = None
    appearance: Appearance | None = None
    emphasis: Emphasis | None = None
    id: str | None = None
    class_: str | None = None
    attrs: Mapping[str, HtmlAttrValue] | None = None


class LinkButton(Component[LinkButtonProps]):
    props_type = LinkButtonProps

    def __init__(
        self,
        label: str,
        href: SafeUrl | str,
        *,
        size: Size | None = None,
        width: Width | None = None,
        appearance: Appearance | None = None,
        emphasis: Emphasis | None = None,
        id: str | None = None,
        class_: str | None = None,
        attrs: Mapping[str, HtmlAttrValue] | None = None,
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
                width=width,
                appearance=appearance,
                emphasis=emphasis,
                id=id,
                class_=class_,
                attrs=attrs,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        data = appearance_data(
            size=self.props.size,
            width=self.props.width,
            appearance=self.props.appearance or "outline",
            emphasis=self.props.emphasis or "secondary",
        )
        attrs: dict[str, HtmlAttrValue] = {
            "href": self.props.href,
            "id": self.props.id,
            "class_": class_names("hedron-button hedron-button-secondary", self.props.class_),
            "role": "button",
            "data": data or None,
        }
        attrs.update(_validated_control_attrs(self.props.attrs, tag="a"))
        return html.a(self.props.label, **attrs)


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
