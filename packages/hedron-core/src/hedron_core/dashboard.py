"""Page-local dashboard interaction graph (RFC-0040 / GRAPH-017).

Bindings declare trigger inputs, snapshot-only state, and target regions. Each edge is an
explicit typed action — not an application-wide callback DAG. Registration fails closed on
missing dependencies, cycles, duplicate writers, and empty targets.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from hedron_core.codes import (
    HED_GRAPH_0001,
    HED_GRAPH_0002,
    HED_GRAPH_0003,
    HED_GRAPH_0004,
    HED_GRAPH_0005,
)
from hedron_core.diagnostics import HedronError, error
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "DashboardBinding",
    "DashboardGraphError",
    "InteractionGraph",
    "TriggerContext",
    "dashboard_graph_payload",
]


class DashboardGraphError(ValueError):
    """Interaction graph registration or ordering failure."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        diagnostic: HedronError | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.diagnostic = diagnostic


@dataclass(frozen=True, slots=True)
class TriggerContext:
    """Typed context for a firing dashboard binding edge."""

    binding_id: str
    event_source: str
    component_id: str
    changed_fields: tuple[str, ...] = ()
    correlation_id: str = ""
    snapshots: Mapping[str, JsonValue] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DashboardBinding:
    """Page-local binding: triggers → action → targets."""

    id: str
    triggers: tuple[str, ...]
    snapshot_inputs: tuple[str, ...]
    targets: tuple[str, ...]
    action_id: str
    init: bool = False
    debounce_ms: int = 0


@dataclass(slots=True)
class InteractionGraph:
    """Finite, inspectable page-local interaction graph."""

    declared_inputs: frozenset[str] = frozenset()
    _bindings: dict[str, DashboardBinding] = field(default_factory=dict, init=False, repr=False)

    def declare_inputs(self, *input_ids: str) -> None:
        """Declare external trigger sources that are not produced by bindings."""
        self.declared_inputs = frozenset(self.declared_inputs | set(input_ids))

    def register(self, binding: DashboardBinding) -> None:
        """Register a binding, failing closed on invalid graph structure."""
        if not binding.id:
            raise self._fail(
                HED_GRAPH_0005,
                "Binding id must be non-empty.",
                title="Invalid binding id",
                remediation="Provide a stable non-empty binding id.",
            )
        if binding.id in self._bindings:
            raise self._fail(
                HED_GRAPH_0005,
                f"Duplicate binding id {binding.id!r}.",
                title="Duplicate binding id",
                remediation="Use a unique id per DashboardBinding.",
            )
        if not binding.targets:
            raise self._fail(
                HED_GRAPH_0004,
                f"Binding {binding.id!r} has empty targets.",
                title="Empty binding targets",
                remediation="Declare one or more target region ids.",
            )

        tentative = dict(self._bindings)
        tentative[binding.id] = binding
        self._validate(tentative)
        self._bindings[binding.id] = binding

    def bindings(self) -> tuple[DashboardBinding, ...]:
        return tuple(self._bindings[bid] for bid in sorted(self._bindings))

    def topological_order(self) -> list[str]:
        """Return binding ids in deterministic dependency order (producers before consumers)."""
        return self._topo_sort(self._bindings)

    def _validate(self, bindings: Mapping[str, DashboardBinding]) -> None:
        writers = self._writers(bindings)
        for bid, binding in bindings.items():
            for target in binding.targets:
                owners = writers.get(target, ())
                if len(owners) > 1:
                    raise self._fail(
                        HED_GRAPH_0003,
                        (f"Duplicate writer for target {target!r}: {', '.join(sorted(owners))}."),
                        title="Duplicate target writer",
                        remediation=(
                            "Ensure each target is written by at most one binding, "
                            "or declare explicit arbitration."
                        ),
                    )
            for trigger in binding.triggers:
                if trigger in self.declared_inputs:
                    continue
                if trigger in writers:
                    continue
                raise self._fail(
                    HED_GRAPH_0001,
                    (
                        f"Binding {bid!r} trigger {trigger!r} is missing: "
                        "not a declared input and not produced by any binding."
                    ),
                    title="Missing graph dependency",
                    remediation=(
                        "Declare the input with declare_inputs() or register a binding "
                        "that writes the trigger as a target."
                    ),
                )
        self._topo_sort(bindings)  # raises on cycles

    def _writers(self, bindings: Mapping[str, DashboardBinding]) -> dict[str, tuple[str, ...]]:
        owners: dict[str, list[str]] = {}
        for bid, binding in bindings.items():
            for target in binding.targets:
                owners.setdefault(target, []).append(bid)
        return {target: tuple(sorted(bids)) for target, bids in owners.items()}

    def _producer_edges(
        self, bindings: Mapping[str, DashboardBinding]
    ) -> dict[str, tuple[str, ...]]:
        """Map consumer binding id → producer binding ids (via trigger ← target)."""
        writers = self._writers(bindings)
        edges: dict[str, list[str]] = {bid: [] for bid in bindings}
        for bid, binding in bindings.items():
            for trigger in binding.triggers:
                for producer in writers.get(trigger, ()):
                    if producer != bid:
                        edges[bid].append(producer)
        return {bid: tuple(sorted(set(deps))) for bid, deps in edges.items()}

    def _topo_sort(self, bindings: Mapping[str, DashboardBinding]) -> list[str]:
        deps = self._producer_edges(bindings)
        seen: set[str] = set()
        stack: set[str] = set()
        ordered: list[str] = []

        def visit(name: str) -> None:
            if name in seen:
                return
            if name in stack:
                raise self._fail(
                    HED_GRAPH_0002,
                    f"Cycle detected at binding {name!r}.",
                    title="Interaction graph cycle",
                    remediation="Remove cyclic trigger/target edges between bindings.",
                )
            stack.add(name)
            for dep in deps.get(name, ()):
                visit(dep)
            stack.remove(name)
            seen.add(name)
            ordered.append(name)

        for name in sorted(bindings):
            visit(name)
        return ordered

    def _fail(
        self,
        code: str,
        message: str,
        *,
        title: str,
        remediation: str,
    ) -> DashboardGraphError:
        diagnostic = error(
            code,
            title=title,
            explanation=message,
            remediation=remediation,
        )
        return DashboardGraphError(message, code=code, diagnostic=diagnostic)


def dashboard_graph_payload(graph: InteractionGraph) -> dict[str, object]:
    """Serialize ``graph`` as Explorer-friendly ``{"nodes", "edges"}`` JSON.

    Nodes cover declared inputs, bindings, and target regions. Edges are typed
    ``trigger`` (input/region → binding) and ``target`` (binding → region).
    """
    nodes: list[dict[str, object]] = []
    edges: list[dict[str, object]] = []
    seen: set[str] = set()

    def add_node(node_id: str, *, kind: str, **extra: object) -> None:
        if node_id in seen:
            return
        seen.add(node_id)
        nodes.append({"id": node_id, "kind": kind, **extra})

    for input_id in sorted(graph.declared_inputs):
        add_node(input_id, kind="input")

    for binding in graph.bindings():
        add_node(binding.id, kind="binding", action_id=binding.action_id)
        for trigger in binding.triggers:
            kind = "input" if trigger in graph.declared_inputs else "region"
            add_node(trigger, kind=kind)
            edges.append({"from": trigger, "to": binding.id, "kind": "trigger"})
        for target in binding.targets:
            add_node(target, kind="region")
            edges.append({"from": binding.id, "to": target, "kind": "target"})

    return {"nodes": nodes, "edges": edges}
