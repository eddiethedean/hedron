"""Phase 0.10 interaction built-ins: Dialog and ChatMessage."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from hedron_core.component import Component
from hedron_core.html import html
from hedron_core.models import Props


def _kids(*children: Any) -> tuple[Any, ...]:
    if (
        len(children) == 1
        and isinstance(children[0], Sequence)
        and not isinstance(children[0], (str, bytes))
    ):
        return tuple(children[0])
    return children


class DialogProps(Props):
    title: str
    open: bool = False
    modal: bool = True
    element_id: str | None = None


class Dialog(Component[DialogProps]):
    """Native ``<dialog>`` with focus-friendly defaults (no app-wide rerun)."""

    props_type = DialogProps
    logical_name = "Dialog"
    slots = {"body": "optional", "actions": "optional"}

    def __init__(
        self,
        title: str,
        *children: Any,
        open: bool = False,
        modal: bool = True,
        element_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            DialogProps(title=title, open=open, modal=modal, element_id=element_id, **kwargs)
        )
        self._body = _kids(*children)

    def render(self) -> Any:
        body = self._slot_values.get("body", self._body)
        if not isinstance(body, tuple):
            body = (body,)
        actions = self._slot_values.get("actions", ())
        if not isinstance(actions, tuple):
            actions = (actions,)
        attrs: dict[str, Any] = {
            "class_": "hedron-dialog",
            "data": {"hedron-dialog": "true", "modal": "true" if self.props.modal else "false"},
        }
        if self.props.element_id:
            attrs["id"] = self.props.element_id
        if self.props.open:
            attrs["open"] = True
        close = html.form(
            html.button("Close", type="submit", value="cancel", formmethod="dialog"),
            method="dialog",
            class_="hedron-dialog-close",
        )
        parts: list[Any] = [
            html.header(html.h2(self.props.title), close, class_="hedron-dialog-header"),
            html.div(*body, class_="hedron-dialog-body"),
        ]
        if actions:
            parts.append(html.footer(*actions, class_="hedron-dialog-actions"))
        return html.dialog(*parts, **attrs)


class ChatMessageProps(Props):
    role: Literal["user", "assistant", "system", "tool", "status"] = "assistant"
    content: str
    message_id: str | None = None
    status: str | None = None


class ChatMessage(Component[ChatMessageProps]):
    """Typed chat transcript item. History ownership stays with the application."""

    props_type = ChatMessageProps
    logical_name = "ChatMessage"

    def __init__(
        self,
        content: str,
        *,
        role: Literal["user", "assistant", "system", "tool", "status"] = "assistant",
        message_id: str | None = None,
        status: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            ChatMessageProps(
                content=content,
                role=role,
                message_id=message_id,
                status=status,
                **kwargs,
            )
        )

    def render(self) -> Any:
        attrs: dict[str, Any] = {
            "class_": f"hedron-chat-message hedron-chat-{self.props.role}",
            "data": {"role": self.props.role},
        }
        if self.props.message_id:
            attrs["id"] = self.props.message_id
        if self.props.role == "status":
            attrs["role"] = "status"
            attrs["aria"] = {"live": "polite"}
        kids: list[Any] = [html.div(self.props.content, class_="hedron-chat-content")]
        if self.props.status:
            kids.append(
                html.div(
                    self.props.status,
                    class_="hedron-chat-status",
                    role="status",
                    aria={"live": "polite"},
                )
            )
        return html.article(*kids, **attrs)
