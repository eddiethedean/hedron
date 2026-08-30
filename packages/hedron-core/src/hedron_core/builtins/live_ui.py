"""Phase 0.10 interaction built-ins: Dialog and ChatMessage."""

from __future__ import annotations

import itertools
import re
from typing import ClassVar, Literal

from hedron_core.alpine import AlpineAttrs, AlpineDirective, AlpineExpression
from hedron_core.builtins._base import collect_children
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.typing_aliases import HtmlAttrValue

_DIALOG_ID_SEQ = itertools.count(1)
_DIALOG_ID_RE = re.compile(r"^[A-Za-z][\w:.-]*$")


class DialogProps(Props):
    title: str
    open: bool = False
    modal: bool = True
    id: str | None = None


class Dialog(Component[DialogProps]):
    """Native ``<dialog>`` with focus-friendly defaults (no app-wide rerun)."""

    props_type = DialogProps
    logical_name = "Dialog"
    slots: ClassVar[dict[str, str]] = {"body": "optional", "actions": "optional"}

    def __init__(
        self,
        title: str,
        *nodes: NodeLike,
        children: NodeLike = None,
        open: bool = False,
        modal: bool = True,
        id: str | None = None,
        element_id: str | None = None,
        **kwargs: object,
    ) -> None:
        # ``element_id`` remains accepted as a compatibility alias for ``id``.
        resolved_id = id if id is not None else element_id
        if resolved_id is not None and not str(resolved_id).strip():
            resolved_id = None
        if resolved_id is None:
            resolved_id = f"hedron-dialog-{next(_DIALOG_ID_SEQ)}"
        elif not _DIALOG_ID_RE.fullmatch(str(resolved_id)):
            raise ValueError(
                f"Dialog id {resolved_id!r} must match /^[A-Za-z][\\w:.-]*$/ "
                "(required by hedron-ui dialog openers)."
            )
        super().__init__(DialogProps(title=title, open=open, modal=modal, id=resolved_id, **kwargs))
        self._body = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        body = self._slot_values.get("body", self._body)
        if not isinstance(body, tuple):
            body = (body,)
        actions = self._slot_values.get("actions", ())
        if not isinstance(actions, tuple):
            actions = (actions,)
        dialog_id = self.props.id or f"hedron-dialog-{next(_DIALOG_ID_SEQ)}"
        title_id = f"{dialog_id}-title"
        attrs: dict[str, HtmlAttrValue] = {
            "id": dialog_id,
            "class_": "hedron-dialog",
            "data": {"hedron-dialog": "true", "modal": "true" if self.props.modal else "false"},
            "aria": {
                "labelledby": title_id,
                "modal": "true" if self.props.modal else "false",
            },
        }
        if self.props.open:
            attrs["open"] = True
        close = html.form(
            html.button("Close", type="submit", value="cancel", formmethod="dialog"),
            method="dialog",
            class_="hedron-dialog-close",
        )
        parts: list[NodeLike] = [
            html.header(
                html.h2(self.props.title, id=title_id),
                close,
                class_="hedron-dialog-header",
            ),
            html.div(*body, class_="hedron-dialog-body"),
        ]
        if actions:
            parts.append(html.footer(*actions, class_="hedron-dialog-actions"))
        return html.dialog(
            *parts,
            alpine=AlpineAttrs(
                state={"open": self.props.open},
                directives=(
                    AlpineDirective("x-bind:open", AlpineExpression.name("open")),
                    AlpineDirective(
                        "x-on:close",
                        AlpineExpression.assign("open", AlpineExpression.literal(False)),
                    ),
                    AlpineDirective(
                        "x-on:cancel",
                        AlpineExpression.assign("open", AlpineExpression.literal(False)),
                    ),
                    AlpineDirective(
                        "x-on:hedron-dialog-open",
                        AlpineExpression.assign("open", AlpineExpression.literal(True)),
                    ),
                    AlpineDirective(
                        "x-on:hedron-dialog-close",
                        AlpineExpression.assign("open", AlpineExpression.literal(False)),
                    ),
                ),
                features=("focus",),
                source=f"component:Dialog:{dialog_id}",
            ),
            **attrs,
        )


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
        **kwargs: object,
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

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "class_": f"hedron-chat-message hedron-chat-{self.props.role}",
            "data": {"role": self.props.role},
        }
        if self.props.message_id:
            attrs["id"] = self.props.message_id
        if self.props.role == "status":
            attrs["role"] = "status"
            attrs["aria"] = {"live": "polite"}
        kids: list[NodeLike] = [html.div(self.props.content, class_="hedron-chat-content")]
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
