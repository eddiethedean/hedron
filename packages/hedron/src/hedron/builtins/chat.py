"""Chat input built-in with explicit HTMX submit (phase 0.10)."""

from __future__ import annotations

from typing import Any, ClassVar

from hedron.htmx import _safe_css_selector
from hedron.routing.reverse import ComponentRef
from hedron_core.builtins.live_ui import ChatMessage
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props

__all__ = ["ChatInput", "ChatMessage"]


class ChatInputProps(Props):
    placeholder: str = "Message"
    submit_label: str = "Send"


class ChatInput(Component[ChatInputProps]):
    """Explicit chat submit control. Transcript history is application-owned."""

    logical_name: ClassVar[str | None] = "ChatInput"
    distribution: ClassVar[str] = "hedron"
    props_type = ChatInputProps

    def __init__(
        self,
        *,
        ref: ComponentRef | None = None,
        action: str | None = None,
        target: str | None = None,
        swap: str = "beforeend",
        placeholder: str = "Message",
        submit_label: str = "Send",
        name: str = "message",
        include_attachments: bool = False,
        csrf_token: str | None = None,
        csrf_form_field: str = "csrf_token",
        csrf_header_name: str = "X-CSRF-Token",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            ChatInputProps(placeholder=placeholder, submit_label=submit_label, **kwargs)
        )
        self.ref = ref
        self.action = action
        self.target = target if target is None or _safe_css_selector(target) else None
        if target is not None and self.target is None:
            raise ValueError(f"Unsafe HTMX target selector: {target!r}")
        self.swap = swap
        self.name = name
        self.include_attachments = include_attachments
        self.csrf_token = csrf_token
        self.csrf_form_field = csrf_form_field
        self.csrf_header_name = csrf_header_name

    def render(self) -> NodeLike:
        import json

        attrs: dict[str, Any] = {
            "class_": "hedron-chat-input",
            "method": "post",
        }
        if self.ref is not None:
            attrs.update(self.ref.hx_attrs())
        elif self.action is not None:
            attrs["hx-post"] = self.action
        if self.target:
            attrs["hx-target"] = self.target
        attrs["hx-swap"] = self.swap
        if self.csrf_token:
            attrs["hx-headers"] = json.dumps({self.csrf_header_name: self.csrf_token})
        kids: list[Any] = []
        if self.csrf_token:
            kids.append(
                html.input(
                    type="hidden",
                    name=self.csrf_form_field,
                    value=self.csrf_token,
                )
            )
        kids.append(
            html.label(
                "Message",
                html.textarea(
                    name=self.name,
                    placeholder=self.props.placeholder,
                    rows=2,
                    required=True,
                    class_="hedron-chat-textarea",
                ),
                class_="hedron-chat-label",
            )
        )
        if self.include_attachments:
            kids.append(
                html.input(
                    type="file",
                    name="attachment",
                    class_="hedron-chat-attachment",
                    aria={"label": "Attachment"},
                )
            )
        kids.append(html.button(self.props.submit_label, type="submit", class_="hedron-chat-send"))
        return html.form(*kids, **attrs)
