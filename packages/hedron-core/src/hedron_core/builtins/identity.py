"""Avatar and identity presentation primitives (phase 0.57 / RFC-0084)."""

from __future__ import annotations

from typing import Any, Literal

from hedron_core.builtins._base import ElementProps, class_names, mark_data
from hedron_core.builtins.appearance import Appearance, Size, appearance_data
from hedron_core.codes import HED_HTML_0006
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue

__all__ = ["Avatar", "Identity"]


def _initials(name: str) -> str:
    parts = [part for part in name.replace(",", " ").split() if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


class AvatarProps(ElementProps):
    name: str
    src: SafeUrl | None = None
    size: Size | None = None
    appearance: Appearance | None = None
    shape: Literal["circle", "rounded", "square"] = "circle"


class Avatar(Component[AvatarProps]):
    """Person or entity avatar with image or initials fallback."""

    props_type = AvatarProps
    logical_name = "Avatar"

    def __init__(
        self,
        name: str,
        *,
        src: SafeUrl | str | None = None,
        size: Size | None = None,
        appearance: Appearance | None = None,
        shape: Literal["circle", "rounded", "square"] = "circle",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        if not name.strip():
            raise error(
                HED_HTML_0006,
                title="Avatar name is required",
                explanation="Avatars need a name for accessible text and initials.",
                remediation="Pass name='Ada Lovelace'.",
            )
        url = None
        if src is not None:
            url = src if isinstance(src, SafeUrl) else SafeUrl.parse(src, purpose=UrlPurpose.ASSET)
        super().__init__(
            AvatarProps(
                name=name,
                src=url,
                size=size,
                appearance=appearance,
                shape=shape,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        data = {
            "hedron-avatar": "true",
            "hedron-avatar-shape": self.props.shape,
            **appearance_data(size=self.props.size, appearance=self.props.appearance),
            **mark_data(self.props.mark),
        }
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names("hedron-avatar", self.props.class_),
            "data": data,
            "aria": {"label": self.props.name},
            "role": "img",
        }
        if self.props.src is not None:
            return html.span(
                html.img(
                    src=self.props.src,
                    alt="",
                    class_="hedron-avatar-image",
                ),
                **attrs,
            )
        return html.span(
            html.span(
                _initials(self.props.name),
                class_="hedron-avatar-initials",
                aria={"hidden": "true"},
            ),
            **attrs,
        )


class IdentityProps(ElementProps):
    name: str
    detail: str | None = None
    href: SafeUrl | None = None
    size: Size | None = None
    density: str | None = None


class Identity(Component[IdentityProps]):
    """Name + optional detail and avatar composition."""

    props_type = IdentityProps
    logical_name = "Identity"

    def __init__(
        self,
        name: str,
        *,
        detail: str | None = None,
        href: SafeUrl | str | None = None,
        avatar: NodeLike = None,
        image_src: SafeUrl | str | None = None,
        size: Size | None = None,
        density: str | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        if not name.strip():
            raise error(
                HED_HTML_0006,
                title="Identity name is required",
                explanation="Identity needs a discernible name.",
                remediation="Pass name='Ada Lovelace'.",
            )
        url = None
        if href is not None:
            url = (
                href
                if isinstance(href, SafeUrl)
                else SafeUrl.parse(href, purpose=UrlPurpose.NAVIGATION)
            )
        super().__init__(
            IdentityProps(
                name=name,
                detail=detail,
                href=url,
                size=size,
                density=density,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._avatar = avatar if avatar is not None else Avatar(name, src=image_src, size=size)

    def render(self) -> NodeLike:
        name_node: NodeLike
        if self.props.href is not None:
            name_node = html.a(self.props.name, href=self.props.href, class_="hedron-identity-name")
        else:
            name_node = html.span(self.props.name, class_="hedron-identity-name")
        text: list[NodeLike] = [name_node]
        if self.props.detail:
            text.append(html.span(self.props.detail, class_="hedron-identity-detail"))
        data = {
            "hedron-identity": "true",
            **appearance_data(size=self.props.size, density=self.props.density),
            **mark_data(self.props.mark),
        }
        return html.div(
            self._avatar,
            html.div(*text, class_="hedron-identity-text"),
            id=self.props.id,
            class_=class_names("hedron-identity", self.props.class_),
            data=data,
        )
