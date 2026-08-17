"""Portable SseRegion / SseTrigger authoring over existing SSE framing (0.48)."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import ClassVar

from hedron_core.builtins._base import collect_children
from hedron_core.codes import HED_EXT_0010
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.htmx_extensions import require_htmx_extension
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue

__all__ = [
    "SseRegion",
    "SseTrigger",
    "parse_last_event_id",
    "validate_sse_event_token",
]

_EVENT_TOKEN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
_LAST_EVENT_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def validate_sse_event_token(value: str, *, field: str = "sse-swap") -> str:
    token = str(value).strip()
    if not token or _EVENT_TOKEN.fullmatch(token) is None:
        raise error(
            HED_EXT_0010,
            title="Invalid SSE event token",
            explanation=f"{field} {value!r} is not a closed event-name token.",
            remediation="Use a letter-prefixed alphanumeric token such as message or job-status.",
        )
    return token


def parse_last_event_id(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    token = str(value).strip()
    if _LAST_EVENT_ID.fullmatch(token) is None:
        raise error(
            HED_EXT_0010,
            title="Invalid Last-Event-ID",
            explanation=f"Last-Event-ID {value!r} failed the closed token grammar.",
            remediation="Send a bounded alphanumeric Last-Event-ID or omit the header.",
        )
    return token


class SseRegionProps(Props):
    connect: SafeUrl
    swap: str = "message"
    close: str | None = None


class SseRegion(Component[SseRegionProps]):
    """Typed SSE host. Polling remains the Supported production fallback."""

    props_type = SseRegionProps
    logical_name: ClassVar[str | None] = "SseRegion"
    distribution: ClassVar[str] = "hedron-core"

    def __init__(
        self,
        *children: NodeLike,
        connect: SafeUrl | str,
        swap: str = "message",
        close: str | None = None,
        id: str | None = None,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        url = (
            connect
            if isinstance(connect, SafeUrl)
            else SafeUrl.parse(str(connect), purpose=UrlPurpose.NAVIGATION)
        )
        swap_token = validate_sse_event_token(swap, field="sse-swap")
        close_token = (
            validate_sse_event_token(close, field="sse-close") if close is not None else None
        )
        super().__init__(SseRegionProps(connect=url, swap=swap_token, close=close_token, **kwargs))
        self._children = collect_children(*children)
        self._id = id
        self._class = class_

    def render(self) -> NodeLike:
        require_htmx_extension("sse")
        attrs: dict[str, HtmlAttrValue] = {
            "hx-ext": "sse",
            "sse-connect": self.props.connect,
            "sse-swap": self.props.swap,
        }
        if self.props.close:
            attrs["sse-close"] = self.props.close
        if self._id:
            attrs["id"] = self._id
        if self._class:
            attrs["class_"] = self._class
        return html.div(*self._children, **attrs)


class SseTriggerProps(Props):
    event: str
    href: SafeUrl | None = None
    target: str | None = None
    swap: str = "innerHTML"


class SseTrigger(Component[SseTriggerProps]):
    """Request a server-canonical fragment when an SSE event name fires."""

    props_type = SseTriggerProps
    logical_name: ClassVar[str | None] = "SseTrigger"
    distribution: ClassVar[str] = "hedron-core"

    def __init__(
        self,
        *children: NodeLike,
        event: str,
        href: SafeUrl | str | None = None,
        target: str | None = None,
        swap: str = "innerHTML",
        **kwargs: object,
    ) -> None:
        token = validate_sse_event_token(event, field="sse-trigger")
        url = None
        if href is not None:
            url = (
                href
                if isinstance(href, SafeUrl)
                else SafeUrl.parse(str(href), purpose=UrlPurpose.NAVIGATION)
            )
        super().__init__(SseTriggerProps(event=token, href=url, target=target, swap=swap, **kwargs))
        self._children: Sequence[NodeLike] = collect_children(*children)

    def render(self) -> NodeLike:
        require_htmx_extension("sse")
        attrs: dict[str, HtmlAttrValue] = {"hx-trigger": f"sse:{self.props.event}"}
        if self.props.href is not None:
            attrs["hx-get"] = self.props.href
        if self.props.target:
            attrs["hx-target"] = self.props.target
        if self.props.swap:
            attrs["hx-swap"] = self.props.swap
        return html.div(*self._children, **attrs)
