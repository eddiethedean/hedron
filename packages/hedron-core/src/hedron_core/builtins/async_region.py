"""Server-first async presentation boundary for phase 0.61."""

from __future__ import annotations

from typing import Any, ClassVar, Literal, cast

from hedron_core.action_state import ActionPhase, AsyncPhase
from hedron_core.builtins._base import ElementProps, class_names, collect_children
from hedron_core.component import Component, NodeLike
from hedron_core.html import html

__all__ = ["AsyncRegion", "AsyncRegionProps"]


class AsyncRegionProps(ElementProps):
    state: AsyncPhase = "idle"
    label: str | None = None
    fallback: Literal["fragment", "page"] = "fragment"


class AsyncRegion(Component[AsyncRegionProps]):
    """Render one named lifecycle state with an ordinary HTML fallback.

    The component is deliberately server-authored: it selects a presentation
    slot during rendering and does not suspend Python execution or require a
    browser runtime.
    """

    props_type = AsyncRegionProps
    logical_name = "AsyncRegion"
    slots: ClassVar[dict[str, str]] = {
        "initial": "optional",
        "pending": "optional",
        "empty": "optional",
        "success": "optional",
        "error": "optional",
        "timeout": "optional",
        "cancelled": "optional",
        "stale": "optional",
        "retry": "optional",
        "conflict": "optional",
    }

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        state: AsyncPhase | ActionPhase = "idle",
        initial: NodeLike = None,
        pending: NodeLike = None,
        empty: NodeLike = None,
        success: NodeLike = None,
        error: NodeLike = None,
        timeout: NodeLike = None,
        cancelled: NodeLike = None,
        stale: NodeLike = None,
        retry: NodeLike = None,
        conflict: NodeLike = None,
        label: str | None = None,
        fallback: Literal["fragment", "page"] = "fragment",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        normalized_state = cast(
            AsyncPhase, ActionPhase(state).value if isinstance(state, ActionPhase) else str(state)
        )
        allowed = {
            "idle",
            "pending",
            "success",
            "error",
            "cancelled",
            "stale",
            "conflict",
            "empty",
            "timeout",
        }
        if normalized_state not in allowed:
            raise ValueError(f"Unsupported async region state: {normalized_state!r}")
        super().__init__(
            AsyncRegionProps(
                state=normalized_state,
                label=label,
                fallback=fallback,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._content = collect_children(*nodes, children=children)
        for name, value in {
            "initial": initial,
            "pending": pending,
            "empty": empty,
            "success": success,
            "error": error,
            "timeout": timeout,
            "cancelled": cancelled,
            "stale": stale,
            "retry": retry,
            "conflict": conflict,
        }.items():
            if value is not None:
                self._slot_values[name] = value

    def render(self) -> NodeLike:
        state = self.props.state
        slot_name = "initial" if state == "idle" else state
        content = self._slot_values.get(slot_name)
        if content is None:
            content = self._content
        if not isinstance(content, tuple):
            content = (content,)
        aria: dict[str, str | bool | int | float | None] = {
            "busy": "true" if state == "pending" else "false"
        }
        if self.props.label:
            aria.update({"label": self.props.label, "live": "polite"})
        return html.div(
            *content,
            id=self.props.id,
            class_=class_names("hedron-async-region", self.props.class_),
            data={
                "hedron-async-region": "true",
                "hedron-action-phase": state,
                "hedron-async-fallback": self.props.fallback,
                "hedron-mark": self.props.mark,
            },
            aria=aria,
        )
