"""Declarative process/pipeline flow primitives (phases 0.54 / 0.57)."""

from __future__ import annotations

from typing import Any, Literal

from hedron_core.builtins._base import ElementProps, class_names, collect_children, mark_data
from hedron_core.builtins.appearance import Density, appearance_data, require_choice
from hedron_core.codes import HED_HTML_0006
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.presentation_064 import application_style_hook_data
from hedron_core.typing_aliases import HtmlAttrValue
from hedron_core.builtins.style_scope import presentation_data

__all__ = [
    "CONNECTOR_KINDS",
    "CONNECTOR_STATES",
    "FLOW_KINDS",
    "FLOW_STATUSES",
    "ConnectorFlow",
    "ConnectorNode",
    "ConnectorTrack",
    "FlowStep",
    "ProcessFlow",
]

FLOW_STATUSES: tuple[str, ...] = ("complete", "current", "pending", "blocked", "skipped")
FLOW_KINDS: tuple[str, ...] = ("step", "milestone", "decision", "end")
CONNECTOR_KINDS: tuple[str, ...] = ("source", "target")
CONNECTOR_STATES: tuple[str, ...] = ("ready", "blocked", "running", "succeeded", "failed")

# Status is never communicated by color alone; each step renders this text.
_STATUS_TEXT: dict[str, str] = {
    "complete": "Complete",
    "current": "In progress",
    "pending": "Not started",
    "blocked": "Blocked",
    "skipped": "Skipped",
}


class ConnectorNodeProps(ElementProps):
    label: str
    kind: Literal["source", "target"] = "source"
    state: Literal["ready", "blocked", "running", "succeeded", "failed"] = "ready"
    detail: str | None = None
    runtime: str | None = None


class ConnectorNode(Component[ConnectorNodeProps]):
    """Provider-neutral source/destination node for data movement workflows.

    The component owns the semantic markers and the baseline responsive card
    treatment. Applications provide provider identity and metadata as content,
    so connector styling does not require private application selectors.
    """

    props_type = ConnectorNodeProps
    logical_name = "ConnectorNode"

    def __init__(
        self,
        label: str,
        *nodes: NodeLike,
        children: NodeLike = None,
        kind: Literal["source", "target"] = "source",
        state: Literal["ready", "blocked", "running", "succeeded", "failed"] = "ready",
        detail: str | None = None,
        runtime: str | None = None,
        leading: NodeLike = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        require_choice(kind, CONNECTOR_KINDS, label="connector kind")
        require_choice(state, CONNECTOR_STATES, label="connector state")
        if not label.strip():
            raise error(
                HED_HTML_0006,
                title="ConnectorNode label is required",
                explanation="A connector node needs a discernible provider label.",
                remediation="Pass a non-empty label.",
            )
        super().__init__(
            ConnectorNodeProps(
                label=label,
                kind=kind,
                state=state,
                detail=detail,
                runtime=runtime,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)
        self._leading = leading

    def render(self) -> NodeLike:
        heading: list[NodeLike] = []
        if self._leading is not None:
            heading.append(self._leading)
        heading.append(html.h3(self.props.label, class_="hedron-connector-node-label"))
        body: list[NodeLike] = [html.div(*heading, class_="hedron-connector-node-heading")]
        if self.props.detail:
            body.append(html.p(self.props.detail, class_="hedron-connector-node-detail"))
        if self.props.runtime:
            body.append(html.p(self.props.runtime, class_="hedron-connector-node-runtime"))
        body.extend(self._children)
        return html.article(
            *body,
            id=self.props.id,
            class_=class_names("hedron-connector-node hedron-process-flow-step", self.props.class_),
            data={
                "hedron-connector-node": "true",
                "hedron-connector-kind": self.props.kind,
                "hedron-connector-state": self.props.state,
                "hedron-flow-status": "blocked" if self.props.state == "blocked" else "pending",
                **mark_data(self.props.mark),
            },
        )


class ConnectorFlowProps(ElementProps):
    direction: Literal["horizontal", "vertical"] = "horizontal"
    collapse: Literal["never", "sm", "md", "lg"] = "md"
    appearance: Literal["plain", "soft", "raised"] = "plain"
    density: Density = "comfortable"
    background: Literal["none", "grid", "dots"] = "none"
    overflow: Literal["visible", "auto", "scroll"] = "auto"
    min_size: Literal["none", "sm", "md", "lg"] = "none"


class ConnectorFlow(Component[ConnectorFlowProps]):
    """Responsive connector-node canvas with a documented fallback layout."""

    props_type = ConnectorFlowProps
    logical_name = "ConnectorFlow"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        direction: Literal["horizontal", "vertical"] = "horizontal",
        collapse: Literal["never", "sm", "md", "lg"] = "md",
        appearance: Literal["plain", "soft", "raised"] = "plain",
        density: Density = "comfortable",
        background: Literal["none", "grid", "dots"] = "none",
        overflow: Literal["visible", "auto", "scroll"] = "auto",
        min_size: Literal["none", "sm", "md", "lg"] = "none",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        require_choice(direction, ("horizontal", "vertical"), label="connector direction")
        require_choice(collapse, ("never", "sm", "md", "lg"), label="connector collapse")
        require_choice(appearance, ("plain", "soft", "raised"), label="connector appearance")
        require_choice(density, ("compact", "comfortable", "spacious"), label="connector density")
        require_choice(background, ("none", "grid", "dots"), label="connector background")
        require_choice(overflow, ("visible", "auto", "scroll"), label="connector overflow")
        require_choice(min_size, ("none", "sm", "md", "lg"), label="connector min_size")
        super().__init__(
            ConnectorFlowProps(
                direction=direction,
                collapse=collapse,
                appearance=appearance,
                density=density,
                background=background,
                overflow=overflow,
                min_size=min_size,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return html.div(
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-connector-flow hedron-process-flow", self.props.class_),
            data={
                "hedron-connector-flow": "true",
                "hedron-connector-direction": self.props.direction,
                "hedron-connector-collapse": self.props.collapse,
                "hedron-direction": self.props.direction,
                "hedron-flow-collapse": self.props.collapse,
                "hedron-appearance": self.props.appearance,
                "hedron-density": self.props.density,
                "hedron-connector-background": self.props.background,
                "hedron-connector-overflow": self.props.overflow,
                "hedron-connector-min-size": self.props.min_size,
                **mark_data(self.props.mark),
            },
        )


class ConnectorTrackProps(ElementProps):
    active: bool = False
    label: str | None = None


class ConnectorTrack(Component[ConnectorTrackProps]):
    """Accessible visual link between connector nodes.

    Motion is opt-in and the static line/arrow remains usable when motion is
    disabled, unsupported, or reduced by user preference.
    """

    props_type = ConnectorTrackProps
    logical_name = "ConnectorTrack"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        active: bool = False,
        label: str | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            ConnectorTrackProps(
                active=active,
                label=label,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names(
                "hedron-connector-track hedron-process-flow-step", self.props.class_
            ),
            "data": {
                "hedron-connector-track": "true",
                "hedron-connector-active": self.props.active,
                **mark_data(self.props.mark),
            },
            "aria": {"label": self.props.label} if self.props.label else None,
        }
        return html.div(*self._children, **attrs)


class FlowStepProps(ElementProps):
    label: str
    status: str = "pending"
    kind: str = "step"
    description: str | None = None
    status_text: str | None = None
    connector: Literal["line", "none"] = "line"


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
        kind: str = "step",
        description: str | None = None,
        status_text: str | None = None,
        connector: Literal["line", "none"] = "line",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        require_choice(status, FLOW_STATUSES, label="status")
        require_choice(kind, FLOW_KINDS, label="kind")
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
                kind=kind,
                description=description,
                status_text=status_text,
                connector=connector,
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
        if self.props.connector == "line":
            body.append(html.span(class_="hedron-process-flow-connector", aria={"hidden": "true"}))
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names("hedron-process-flow-step", self.props.class_),
            "data": {
                "hedron-flow-status": status,
                "hedron-flow-kind": self.props.kind,
                "hedron-flow-connector": self.props.connector,
                **mark_data(self.props.mark),
                **application_style_hook_data(
                    "ProcessFlow",
                    "step",
                    state=(
                        status if status in {"current", "complete", "blocked", "skipped"} else None
                    ),
                ),
                **presentation_data("ProcessFlow.step"),
            },
        }
        if status == "current":
            attrs["aria"] = {"current": "step"}
        return html.li(*body, **attrs)


class ProcessFlowProps(ElementProps):
    label: str
    direction: Literal["horizontal", "vertical"] = "horizontal"
    collapse: str = "md"
    density: Density | None = None


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
        density: Density | None = None,
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
                density=density,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        data = {
            "hedron-process-flow": "true",
            "hedron-direction": self.props.direction,
            "hedron-flow-collapse": self.props.collapse,
            **appearance_data(density=self.props.density),
            **mark_data(self.props.mark),
        }
        return html.ol(
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-process-flow", self.props.class_),
            aria={"label": self.props.label},
            data=data,
        )
