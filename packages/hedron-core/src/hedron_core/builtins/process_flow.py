"""Declarative process/pipeline flow primitives (phase 0.54 / RFC-0081)."""

from __future__ import annotations

from typing import Any, Literal

from hedron_core.builtins._base import ElementProps, class_names, collect_children, mark_data
from hedron_core.builtins.appearance import require_choice
from hedron_core.codes import HED_HTML_0006
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.typing_aliases import HtmlAttrValue

__all__ = ["FLOW_STATUSES", "FlowStep", "ProcessFlow"]

FLOW_STATUSES: tuple[str, ...] = ("complete", "current", "pending", "blocked", "skipped")

# Status is never communicated by color alone; each step renders this text.
_STATUS_TEXT: dict[str, str] = {
    "complete": "Complete",
    "current": "In progress",
    "pending": "Not started",
    "blocked": "Blocked",
    "skipped": "Skipped",
}


class FlowStepProps(ElementProps):
    label: str
    status: str = "pending"
    description: str | None = None
    status_text: str | None = None


class FlowStep(Component[FlowStepProps]):
    """One stage of a :class:`ProcessFlow`, rendered as a list item."""

    props_type = FlowStepProps
    logical_name = "FlowStep"

    def __init__(
        self,
        label: str,
        *nodes: NodeLike,
        children: NodeLike = None,
        status: str = "pending",
        description: str | None = None,
        status_text: str | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        require_choice(status, FLOW_STATUSES, label="status")
        if not label.strip():
            raise error(
                HED_HTML_0006,
                title="FlowStep label is required",
                explanation="Each process step needs a discernible label.",
                remediation="Pass a non-empty label.",
            )
        super().__init__(
            FlowStepProps(
                label=label,
                status=status,
                description=description,
                status_text=status_text,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        status = self.props.status
        body: list[NodeLike] = [
            html.span(self.props.label, class_="hedron-process-flow-label"),
            html.span(
                self.props.status_text or _STATUS_TEXT[status],
                class_="hedron-process-flow-status",
            ),
        ]
        if self.props.description:
            body.append(html.p(self.props.description, class_="hedron-process-flow-description"))
        if self._children:
            body.append(html.div(*self._children, class_="hedron-process-flow-body"))
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names("hedron-process-flow-step", self.props.class_),
            "data": {
                "hedron-flow-status": status,
                **mark_data(self.props.mark),
            },
        }
        if status == "current":
            attrs["aria"] = {"current": "step"}
        return html.li(*body, **attrs)


class ProcessFlowProps(ElementProps):
    label: str
    direction: Literal["horizontal", "vertical"] = "horizontal"
    collapse: str = "md"


class ProcessFlow(Component[ProcessFlowProps]):
    """Ordered operational workflow rendered as an accessible ordered list."""

    props_type = ProcessFlowProps
    logical_name = "ProcessFlow"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        label: str,
        direction: Literal["horizontal", "vertical"] = "horizontal",
        collapse: str = "md",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        require_choice(collapse, ("never", "sm", "md", "lg"), label="collapse")
        if not label.strip():
            raise error(
                HED_HTML_0006,
                title="ProcessFlow label is required",
                explanation="The step list needs an accessible name.",
                remediation="Pass label='Ingestion pipeline'.",
            )
        super().__init__(
            ProcessFlowProps(
                label=label,
                direction=direction,
                collapse=collapse,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return html.ol(
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-process-flow", self.props.class_),
            aria={"label": self.props.label},
            data={
                "hedron-process-flow": "true",
                "hedron-direction": self.props.direction,
                "hedron-flow-collapse": self.props.collapse,
                **mark_data(self.props.mark),
            },
        )
