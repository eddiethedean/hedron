"""Framework-neutral rendering engine."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from types import GeneratorType
from typing import Any

from hedron_core._nodes import (
    ComponentBoundaryNode,
    EmptyNode,
    FragmentNode,
    Node,
    TextNode,
)
from hedron_core._serializer import serialize_tree
from hedron_core.component import Component, ComponentNode
from hedron_core.diagnostics import Diagnostic, DiagnosticSeverity, error, make_diagnostic
from hedron_core.html import _NativeElement, _TrustedRaw
from hedron_core.identifiers import instance_id
from hedron_core.security import Secret

# Public recursive alias for accepted render inputs / component returns.
NodeLike = (
    Component[Any] | ComponentNode | str | int | float | bool | None | Sequence["NodeLike"]
)


class RenderMode(StrEnum):
    PAGE = "page"
    FRAGMENT = "fragment"


@dataclass(frozen=True, slots=True)
class RenderContext:
    locale: str = "en"
    theme: str | None = None
    max_depth: int = 100
    max_nodes: int = 50_000

    @classmethod
    def standalone(cls, *, locale: str = "en", theme: str | None = None) -> RenderContext:
        return cls(locale=locale, theme=theme)


@dataclass(frozen=True, slots=True)
class AssetRef:
    kind: str
    href: str
    attributes: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RenderResult:
    html: str
    mode: RenderMode
    assets: tuple[AssetRef, ...] = ()
    headers: Mapping[str, str] = field(default_factory=dict)
    identity_map: Mapping[str, str] = field(default_factory=dict)
    diagnostics: tuple[Diagnostic, ...] = ()
    trace: Mapping[str, Any] | None = None


class _RenderState:
    def __init__(self, context: RenderContext) -> None:
        self.context = context
        self.node_count = 0
        self.occurrence = 0
        self.identity_map: dict[str, str] = {}
        self.seen_instance_ids: set[str] = set()
        self.diagnostics: list[Diagnostic] = []
        self.stack: list[str] = []

    def path(self) -> str:
        return " > ".join(self.stack) if self.stack else "<root>"


def _reject_generator(value: Any) -> None:
    if isinstance(value, GeneratorType) or (
        isinstance(value, Iterator) and not isinstance(value, (list, tuple, str, bytes))
    ):
        raise error(
            "HED-RENDER-0008",
            title="Unsafe iterator rejected",
            explanation=(
                "Generators and arbitrary iterators are not accepted as node "
                "sequences because they may hide I/O."
            ),
            remediation="Materialize the sequence as a list or tuple first.",
        )


def _normalize(
    value: Any,
    state: _RenderState,
    *,
    depth: int,
) -> tuple[Node, ...]:
    if depth > state.context.max_depth:
        raise error(
            "HED-RENDER-0009",
            title="Render depth limit exceeded",
            explanation=f"Exceeded max_depth={state.context.max_depth} at {state.path()}.",
            remediation="Reduce nesting or raise the configured depth limit.",
            component_id=state.path(),
        )
    state.node_count += 1
    if state.node_count > state.context.max_nodes:
        raise error(
            "HED-RENDER-0010",
            title="Render node limit exceeded",
            explanation=f"Exceeded max_nodes={state.context.max_nodes} at {state.path()}.",
            remediation="Reduce tree size or raise the configured node limit.",
            component_id=state.path(),
        )

    if value is None:
        return (EmptyNode(),)
    if isinstance(value, Secret):
        raise error(
            "HED-SEC-0005",
            title="Secret cannot be rendered",
            explanation="Secret values cannot appear in the render tree.",
            remediation="Reveal only in application code and pass a non-secret string.",
            component_id=state.path(),
        )
    if isinstance(value, str):
        return (TextNode(value),)
    if isinstance(value, bool):
        return (TextNode("true" if value else "false"),)
    if isinstance(value, (int, float)):
        return (TextNode(str(value)),)
    if isinstance(value, _TrustedRaw):
        return (value.to_node(),)
    if isinstance(value, _NativeElement):
        child_nodes: list[Node] = []
        for child in value.children:
            child_nodes.extend(_normalize(child, state, depth=depth + 1))
        return (value.to_element_node(tuple(child_nodes)),)
    if isinstance(value, Component):
        return _render_component(value, state, depth=depth)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        _reject_generator(value)
        nodes: list[Node] = []
        for item in value:
            nodes.extend(_normalize(item, state, depth=depth + 1))
        return (FragmentNode(tuple(nodes)),)

    _reject_generator(value)
    raise error(
        "HED-RENDER-0011",
        title="Unsupported render value",
        explanation=(
            f"Value of type {type(value).__name__!r} is not a valid NodeLike at {state.path()}."
        ),
        remediation="Return a Component, html element, string, sequence, or None.",
        component_id=state.path(),
    )


def _render_component(
    component: Component[Any], state: _RenderState, *, depth: int
) -> tuple[Node, ...]:
    logical = component.logical_id()
    if logical in state.stack:
        raise error(
            "HED-RENDER-0012",
            title="Component render cycle detected",
            explanation=f"Cycle involving {logical} at path {state.path()}.",
            remediation="Break the recursive render() call chain.",
            component_id=logical,
        )
    state.stack.append(logical)
    try:
        state.occurrence += 1
        ordinal = state.occurrence
        instance = instance_id(
            {
                "logical_id": logical,
                "identity": component.identity_fields(),
                "path": state.path(),
                "ordinal": ordinal,
            }
        )
        if instance in state.seen_instance_ids:
            raise error(
                "HED-RENDER-0013",
                title="Instance ID collision",
                explanation=(f"Duplicate instance id {instance} for {logical} at {state.path()}."),
                remediation="Provide distinct key= or identity fields.",
                component_id=logical,
            )
        state.seen_instance_ids.add(instance)
        state.identity_map[f"{logical}#{ordinal}"] = instance

        rendered = component.render()
        children = _normalize(rendered, state, depth=depth + 1)
        return (
            ComponentBoundaryNode(
                logical_id=logical,
                instance_id=instance,
                children=children,
                props_summary={},
            ),
        )
    finally:
        state.stack.pop()


def render(
    value: Any,
    *,
    context: RenderContext | None = None,
    mode: RenderMode = RenderMode.FRAGMENT,
) -> RenderResult:
    """Framework-neutral entry point producing a ``RenderResult``."""
    ctx = context if context is not None else RenderContext.standalone()
    state = _RenderState(ctx)
    nodes = _normalize(value, state, depth=0)

    if mode is RenderMode.PAGE:
        # Wrap fragment content in a minimal document shell when the root is not Page.
        from hedron_core.builtins.document import Page

        if isinstance(value, Page):
            html_text = serialize_tree(nodes)
            if not html_text.lstrip().lower().startswith("<!doctype"):
                html_text = "<!DOCTYPE html>" + html_text
        else:
            body_html = serialize_tree(nodes)
            html_text = (
                "<!DOCTYPE html>"
                f'<html lang="{_escape_attr(ctx.locale)}">'
                '<head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">'
                "</head>"
                f"<body>{body_html}</body></html>"
            )
    else:
        html_text = serialize_tree(nodes)

    return RenderResult(
        html=html_text,
        mode=mode,
        assets=(),
        headers={},
        identity_map=dict(state.identity_map),
        diagnostics=tuple(state.diagnostics),
        trace={
            "path": state.path(),
            "node_count": state.node_count,
            "locale": ctx.locale,
            "theme": ctx.theme,
        },
    )


def _escape_attr(value: str) -> str:
    return (
        value.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
    )


def warn(state: _RenderState, code: str, title: str, explanation: str) -> None:
    state.diagnostics.append(
        make_diagnostic(
            code,
            severity=DiagnosticSeverity.WARNING,
            title=title,
            explanation=explanation,
            component_id=state.path(),
        )
    )
