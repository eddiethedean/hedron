"""Closed 0.44 Control.kind → Supported hedron-elements tags (opt-in)."""

from __future__ import annotations

from collections.abc import Mapping

from hedron_core.component import NodeLike
from hedron_core.diagnostics import HedronError

TEXT_LIKE = frozenset(
    {"text", "textarea", "password", "number", "email", "url", "date", "time", "datetime-local"}
)
CHOICE_LIKE = frozenset({"checkbox", "select", "radio"})
FILE_LIKE = frozenset({"file"})

CONTROL_ELEMENT_MAP: Mapping[str, str] = {
    "text": "hedron-field-text",
    "textarea": "hedron-field-text",
    "password": "hedron-field-text",
    "number": "hedron-field-text",
    "email": "hedron-field-text",
    "url": "hedron-field-text",
    "date": "hedron-field-text",
    "time": "hedron-field-text",
    "datetime-local": "hedron-field-text",
    "checkbox": "hedron-field-choice",
    "select": "hedron-field-choice",
    "radio": "hedron-field-choice",
    "file": "hedron-field-file",
}

ASYNC_STATE_TAG = "hedron-action-async"

__all__ = [
    "ASYNC_STATE_TAG",
    "CHOICE_LIKE",
    "CONTROL_ELEMENT_MAP",
    "FILE_LIKE",
    "TEXT_LIKE",
    "element_tag_for_kind",
    "enhanced_control",
]


def element_tag_for_kind(kind: str | None) -> str | None:
    if not kind:
        return None
    return CONTROL_ELEMENT_MAP.get(kind)


def enhanced_control(
    kind: str, native: NodeLike, *, name: str, value: object = "", **kwargs: object
) -> NodeLike:
    """Wrap a native control in the matching element; fall back to native."""
    tag = element_tag_for_kind(kind)
    if tag is None:
        return native
    try:
        from hedron_core.html import html

        return html.tag(tag)(
            native,
            **{
                "data-hedron-element": tag,
                "data-hedron-abi": "1",
            },
        )
    except (HedronError, TypeError, AttributeError, ImportError):
        return native
