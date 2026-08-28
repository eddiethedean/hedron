"""Mutable request-local state for one or more render operations."""

from __future__ import annotations

from collections.abc import Callable

from hedron_core.alpine import AlpineFeatureDemand
from hedron_core.diagnostics import Diagnostic, DiagnosticSeverity, error, make_diagnostic
from hedron_core.rendering.contracts import RenderContext


class RenderState:
    """Own render budgets, identity bookkeeping, diagnostics, and traversal state.

    The normalizer and component lifecycle renderer depend on this narrow state
    object instead of mutating orchestration concerns directly.
    """

    def __init__(self, context: RenderContext) -> None:
        self.context = context
        self.node_count = 0
        self.occurrence_by_logical: dict[str, int] = {}
        self.identity_map: dict[str, str] = {}
        self.seen_instance_ids: set[str] = set()
        self.diagnostics: list[Diagnostic] = []
        self.stack: list[int] = []
        self.stack_labels: list[str] = []
        self.browser_demands: list[AlpineFeatureDemand] = []

    def path(self) -> str:
        return " > ".join(self.stack_labels) if self.stack_labels else "<root>"

    def consume_node(self, depth: int) -> None:
        if depth > self.context.max_depth:
            raise error(
                "HED-RENDER-0009",
                title="Render depth limit exceeded",
                explanation=f"Exceeded max_depth={self.context.max_depth} at {self.path()}.",
                remediation="Reduce nesting or raise the configured depth limit.",
                component_id=self.path(),
            )
        self.node_count += 1
        if self.node_count > self.context.max_nodes:
            raise error(
                "HED-RENDER-0010",
                title="Render node limit exceeded",
                explanation=f"Exceeded max_nodes={self.context.max_nodes} at {self.path()}.",
                remediation="Reduce tree size or raise the configured node limit.",
                component_id=self.path(),
            )

    def add_browser_demand(self, demand: AlpineFeatureDemand) -> None:
        self.browser_demands.append(demand)

    def warn(self, code: str, title: str, explanation: str) -> None:
        self.diagnostics.append(
            make_diagnostic(
                code,
                severity=DiagnosticSeverity.WARNING,
                title=title,
                explanation=explanation,
                component_id=self.path(),
            )
        )


RenderStateFactory = Callable[[RenderContext], RenderState]
