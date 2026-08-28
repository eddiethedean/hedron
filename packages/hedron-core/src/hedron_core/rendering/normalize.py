"""Node normalization and component lifecycle policies."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from dataclasses import replace
from types import GeneratorType
from typing import Any, Protocol, cast

from hedron_core._nodes import ComponentBoundaryNode, EmptyNode, FragmentNode, Node, TextNode
from hedron_core.alpine import AlpineFeatureDemand
from hedron_core.component import (
    Component,
    ComponentNode,
    NodeLike,
    _pop_render_identity,
    _push_render_identity,
)
from hedron_core.diagnostics import error
from hedron_core.html import _NativeElement, _TrustedRaw
from hedron_core.rendering.state import RenderState
from hedron_core.security import Secret

Normalizer = Callable[[NodeLike, int], tuple[Node, ...]]


class ComponentRenderer(Protocol):
    def render(
        self, component: Component[Any], state: RenderState, *, depth: int, normalize: Normalizer
    ) -> tuple[Node, ...]: ...


_ALPINE_DIRECTIVE_FEATURES = {
    "x-data": "data",
    "x-bind": "bind",
    "x-model": "model",
    "x-on": "on",
    "x-show": "show",
    "x-if": "if",
    "x-for": "for",
    "x-text": "text",
    "x-html": "html",
    "x-transition": "transition",
    "x-cloak": "cloak",
    "x-init": "init",
    "x-effect": "effect",
    "x-ignore": "ignore",
    "x-id": "id",
    "x-teleport": "teleport",
}


def reject_generator(value: object) -> None:
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


class BrowserDemandCollector:
    """Translate native element metadata into browser feature demands."""

    def collect(self, element: _NativeElement, state: RenderState) -> None:
        attributes = element.attributes
        for demand in element.browser_demands:
            state.add_browser_demand(demand)
        typed_features = {demand.feature for demand in element.browser_demands}
        for name in attributes:
            lowered = name.lower()
            if lowered.startswith("x-"):
                base = lowered.split(":", 1)[0].split(".", 1)[0]
                feature = _ALPINE_DIRECTIVE_FEATURES.get(base)
                if feature and feature not in typed_features:
                    state.add_browser_demand(AlpineFeatureDemand(feature, "rendered-html"))
            elif lowered == "data-hedron-interaction":
                kind = str(attributes[name])
                if kind in {"local", "combined"} and "interaction" not in typed_features:
                    state.add_browser_demand(
                        AlpineFeatureDemand("interaction", "rendered-interaction")
                    )


class ComponentLifecycleRenderer:
    """Render a component with identity, cycle, slot, and style-scope policies."""

    def render(
        self,
        component: Component[Any],
        state: RenderState,
        *,
        depth: int,
        normalize: Normalizer,
    ) -> tuple[Node, ...]:
        logical = component.logical_id()
        identity_key = id(component)
        if identity_key in state.stack:
            raise error(
                "HED-RENDER-0012",
                title="Component render cycle detected",
                explanation=f"Cycle involving {logical} at path {state.path()}.",
                remediation="Break the recursive render() call chain.",
                component_id=logical,
            )
        state.stack.append(identity_key)
        state.stack_labels.append(logical)
        try:
            component.validate_slots()
            identity = component.identity_fields()
            auto_key: str | None = None
            if "key" not in identity:
                count = state.occurrence_by_logical.get(logical, 0) + 1
                state.occurrence_by_logical[logical] = count
                auto_key = f"auto-{count}"
            instance = component.compute_instance_id(auto_key=auto_key)
            if instance in state.seen_instance_ids:
                raise error(
                    "HED-RENDER-0013",
                    title="Instance ID collision",
                    explanation=(
                        f"Duplicate instance id {instance} for {logical} at {state.path()}."
                    ),
                    remediation="Provide distinct key= or identity fields.",
                    component_id=logical,
                )
            state.seen_instance_ids.add(instance)
            map_key = f"{logical}#{identity.get('key', auto_key)}"
            state.identity_map[map_key] = instance

            render_key = str(identity.get("key", auto_key))
            token = _push_render_identity(instance, render_key)
            style_token = None
            try:
                style_context = getattr(component, "style_context", None)
                if style_context is not None:
                    from hedron_core.builtins.style_scope import (
                        current_style_context,
                        push_style_context,
                    )

                    parent_context = current_style_context()
                    if parent_context is not None and style_context.parent is None:
                        style_context = replace(style_context, parent=parent_context)
                    style_token = push_style_context(style_context)
                children = normalize(component.render(), depth + 1)
            finally:
                if style_token is not None:
                    from hedron_core.builtins.style_scope import pop_style_context

                    pop_style_context(style_token)
                _pop_render_identity(token)
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
            state.stack_labels.pop()


class NodeNormalizer:
    """Convert public ``NodeLike`` values to the private node algebra."""

    def __init__(
        self,
        state: RenderState,
        *,
        component_renderer: ComponentRenderer | None = None,
        browser_collector: BrowserDemandCollector | None = None,
    ) -> None:
        self.state = state
        self.component_renderer = component_renderer or ComponentLifecycleRenderer()
        self.browser_collector = browser_collector or BrowserDemandCollector()

    def normalize(self, value: NodeLike, *, depth: int) -> tuple[Node, ...]:
        self.state.consume_node(depth)
        if value is None:
            return (EmptyNode(),)
        if isinstance(value, Secret):
            raise error(
                "HED-SEC-0005",
                title="Secret cannot be rendered",
                explanation="Secret values cannot appear in the render tree.",
                remediation="Reveal only in application code and pass a non-secret string.",
                component_id=self.state.path(),
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
            self.browser_collector.collect(value, self.state)
            child_nodes: list[Node] = []
            for child in value.children:
                child_nodes.extend(self.normalize(child, depth=depth + 1))
            return (value.to_element_node(tuple(child_nodes)),)
        if isinstance(value, Component):
            return self.component_renderer.render(
                cast(Component[Any], value),
                self.state,
                depth=depth,
                normalize=self._normalize_for_renderer,
            )
        hedron_node = getattr(value, "__hedron_node__", None)
        if callable(hedron_node) and not isinstance(value, type):
            return self.normalize(cast(NodeLike, hedron_node()), depth=depth + 1)
        if isinstance(value, ComponentNode) and not isinstance(value, Component):
            node_fn = getattr(value, "__hedron_node__", None)
            if callable(node_fn):
                return self.normalize(cast(NodeLike, node_fn()), depth=depth + 1)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            reject_generator(value)
            nodes: list[Node] = []
            for item in value:
                nodes.extend(self.normalize(cast(NodeLike, item), depth=depth + 1))
            return (FragmentNode(tuple(nodes)),)

        reject_generator(value)
        raise error(
            "HED-RENDER-0011",
            title="Unsupported render value",
            explanation=(
                "Value of type "
                f"{type(value).__name__!r} is not a valid NodeLike at {self.state.path()}."
            ),
            remediation="Return a Component, html element, string, sequence, or None.",
            component_id=self.state.path(),
        )

    def _normalize_for_renderer(self, value: NodeLike, depth: int) -> tuple[Node, ...]:
        return self.normalize(value, depth=depth)
