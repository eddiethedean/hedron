"""Render-session orchestration.

This module coordinates policies; it does not implement node normalization,
component lifecycle rules, browser-plan construction, or HTML serialization.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import MappingProxyType

from hedron_core._nodes import Node
from hedron_core.component import NodeLike
from hedron_core.diagnostics import Diagnostic
from hedron_core.rendering.browser_plan import BrowserPlanBuilder, DefaultBrowserPlanBuilder
from hedron_core.rendering.contracts import (
    RenderContext,
    RenderMode,
    RenderResult,
    pop_render_context,
    push_render_context,
)
from hedron_core.rendering.normalize import (
    BrowserDemandCollector,
    ComponentRenderer,
    NodeNormalizer,
)
from hedron_core.rendering.page_shell import serialize_page_or_fragment
from hedron_core.rendering.state import RenderState

Serializer = Callable[[NodeLike, tuple[Node, ...], RenderContext, RenderMode], str]


def serialize_result(
    value: NodeLike,
    nodes: tuple[Node, ...],
    context: RenderContext,
    mode: RenderMode,
) -> str:
    return serialize_page_or_fragment(
        value,
        nodes,
        mount_path=context.mount_path,
        locale=context.locale,
        page_mode=mode is RenderMode.PAGE,
    )


class RenderSession:
    """Render multiple values through one identity and resource-budget scope."""

    def __init__(
        self,
        context: RenderContext | None = None,
        *,
        component_renderer: ComponentRenderer | None = None,
        browser_collector: BrowserDemandCollector | None = None,
        browser_plan_builder: BrowserPlanBuilder | None = None,
        serializer: Serializer | None = None,
    ) -> None:
        self.context = context if context is not None else RenderContext.standalone()
        self._state = RenderState(self.context)
        self._normalizer = NodeNormalizer(
            self._state,
            component_renderer=component_renderer,
            browser_collector=browser_collector,
        )
        self._browser_plan_builder = (
            browser_plan_builder
            if browser_plan_builder is not None
            else DefaultBrowserPlanBuilder()
        )
        self._serializer = serializer if serializer is not None else serialize_result
        self._render_count = 0

    @property
    def node_count(self) -> int:
        return self._state.node_count

    @property
    def identity_map(self) -> Mapping[str, str]:
        return MappingProxyType(dict(self._state.identity_map))

    @property
    def diagnostics(self) -> tuple[Diagnostic, ...]:
        return tuple(self._state.diagnostics)

    def render(
        self,
        value: NodeLike,
        *,
        mode: RenderMode = RenderMode.FRAGMENT,
        base_depth: int = 0,
    ) -> RenderResult:
        """Render one value while retaining state for subsequent calls."""
        if base_depth < 0:
            raise ValueError("base_depth must be non-negative")
        previous_identity_keys = set(self._state.identity_map)
        previous_diagnostic_count = len(self._state.diagnostics)
        previous_node_count = self._state.node_count
        ctx_token = push_render_context(self.context)
        from hedron_core.hosts import begin_host_mount_scope, end_host_mount_scope
        from hedron_core.htmx_extensions import (
            begin_extension_collect,
            finish_extension_plan,
            reset_extension_collect,
        )

        mount_token = begin_host_mount_scope()
        ext_tokens = begin_extension_collect()
        try:
            nodes = self._normalizer.normalize(value, depth=base_depth)
            html_text = self._serializer(value, nodes, self.context, mode)
            htmx_plan = finish_extension_plan(mode=mode)
        finally:
            reset_extension_collect(ext_tokens)
            end_host_mount_scope(mount_token)
            pop_render_context(ctx_token)
        self._render_count += 1
        identity_delta = {
            key: value
            for key, value in self._state.identity_map.items()
            if key not in previous_identity_keys
        }
        diagnostic_delta = tuple(self._state.diagnostics[previous_diagnostic_count:])
        plan_diagnostics = getattr(htmx_plan, "diagnostics", ()) or ()
        browser_plan = self._browser_plan_builder.build(self._state.browser_demands)
        return RenderResult(
            html=html_text,
            mode=mode,
            assets=(),
            headers=MappingProxyType({}),
            identity_map=MappingProxyType(identity_delta),
            diagnostics=diagnostic_delta + tuple(plan_diagnostics),
            htmx_plan=htmx_plan,
            browser_plan=browser_plan,
            trace=MappingProxyType(
                {
                    "path": self._state.path(),
                    "node_count": self._state.node_count - previous_node_count,
                    "session_node_count": self._state.node_count,
                    "render_ordinal": self._render_count,
                    "locale": self.context.locale,
                    "theme": self.context.theme,
                    "browser_plan_fingerprint": browser_plan.fingerprint,
                }
            ),
        )


def render(
    value: NodeLike,
    *,
    context: RenderContext | None = None,
    mode: RenderMode = RenderMode.FRAGMENT,
) -> RenderResult:
    """Framework-neutral entry point producing a ``RenderResult``."""
    return RenderSession(context).render(value, mode=mode)
