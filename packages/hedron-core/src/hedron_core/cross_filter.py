"""Cross-filter dashboard composition helpers (RFC-0040 / XFILTER-017 / CHARTLINK-039).

Wires Published ``hedron-chart`` events (0.38), grid selection fields, and optional map
viewport triggers into page-local ``DashboardBinding`` edges over declared target regions.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from hedron_core.dashboard import DashboardBinding, InteractionGraph
from hedron_core.visualization import ChartEvent

__all__ = [
    "CHART_038_EVENT_KINDS",
    "MAP_VIEWPORT_TRIGGER",
    "CrossFilterBinding",
    "compose_chartlink_039",
    "compose_cross_filter",
    "triggers_from_chart_event",
    "triggers_from_grid_selection",
    "triggers_from_hedron_chart_event",
]

MAP_VIEWPORT_TRIGGER = "map.viewport"

# Published 0.38 first-party chart event kinds (no parallel renderer).
CHART_038_EVENT_KINDS = (
    "inspect",
    "focus",
    "select",
    "legend_filter",
    "brush",
    "zoom",
    "pan",
    "reset",
    "crosshair",
    "drill_intent",
)


@dataclass(frozen=True, slots=True)
class CrossFilterBinding:
    """Helper that maps chart/grid field names onto ``DashboardBinding`` triggers."""

    id: str
    targets: tuple[str, ...]
    action_id: str = "cross_filter"
    chart_fields: tuple[str, ...] = ()
    grid_selection_fields: tuple[str, ...] = ()
    map_viewport: bool = False
    debounce_ms: int = 0
    snapshot_inputs: tuple[str, ...] = ()
    init: bool = False

    def trigger_ids(self) -> tuple[str, ...]:
        triggers: list[str] = []
        for name in self.chart_fields:
            triggers.append(name if "." in name else f"chart.{name}")
        for name in self.grid_selection_fields:
            triggers.append(name if "." in name else f"grid.{name}")
        if self.map_viewport:
            triggers.append(MAP_VIEWPORT_TRIGGER)
        return tuple(triggers)

    def to_binding(self) -> DashboardBinding:
        triggers = self.trigger_ids()
        if not triggers:
            raise ValueError("CrossFilterBinding requires at least one chart/grid/map trigger.")
        return DashboardBinding(
            id=self.id,
            triggers=triggers,
            snapshot_inputs=self.snapshot_inputs,
            targets=self.targets,
            action_id=self.action_id,
            init=self.init,
            debounce_ms=self.debounce_ms,
        )

    def register(self, graph: InteractionGraph) -> DashboardBinding:
        """Declare trigger inputs and register the derived ``DashboardBinding``."""
        binding = self.to_binding()
        graph.declare_inputs(*binding.triggers)
        graph.register(binding)
        return binding


def triggers_from_chart_event(
    event: ChartEvent, *, fields: Sequence[str] | None = None
) -> tuple[str, ...]:
    """Return trigger ids for a chart event (default: ``chart.<kind>``)."""
    if fields is None:
        return (f"chart.{event.kind}",)
    return tuple(name if "." in name else f"chart.{name}" for name in fields)


def triggers_from_hedron_chart_event(
    kind: str,
    *,
    event_name: str | None = None,
) -> tuple[str, ...]:
    """Return trigger ids for a Published 0.38 ``hedron-chart-*`` event kind."""
    if kind not in CHART_038_EVENT_KINDS:
        raise ValueError(
            f"Unknown hedron-chart event kind {kind!r}; expected one of {CHART_038_EVENT_KINDS}"
        )
    if event_name:
        return (event_name if "." in event_name else f"chart.{event_name}",)
    return (f"chart.{kind}",)


def triggers_from_grid_selection(
    *,
    fields: Sequence[str] = ("selection",),
) -> tuple[str, ...]:
    """Return trigger ids for grid selection field names."""
    return tuple(name if "." in name else f"grid.{name}" for name in fields)


def compose_cross_filter(
    graph: InteractionGraph,
    *,
    chart_trigger: str,
    grid_trigger: str,
    targets: Sequence[str],
    map_viewport: bool | str = False,
    binding_id: str = "cross_filter",
    action_id: str = "cross_filter",
    debounce_ms: int = 0,
) -> DashboardBinding:
    """Register a multi-region cross-filter binding on ``graph``.

    ``map_viewport`` may be ``True`` (uses ``map.viewport``), a custom trigger string,
    or ``False`` to omit.
    """
    if not targets:
        raise ValueError("compose_cross_filter requires one or more targets.")
    triggers: list[str] = [chart_trigger, grid_trigger]
    if map_viewport is True:
        triggers.append(MAP_VIEWPORT_TRIGGER)
    elif isinstance(map_viewport, str) and map_viewport:
        triggers.append(map_viewport)

    graph.declare_inputs(*triggers)
    binding = DashboardBinding(
        id=binding_id,
        triggers=tuple(triggers),
        snapshot_inputs=(),
        targets=tuple(targets),
        action_id=action_id,
        debounce_ms=debounce_ms,
    )
    graph.register(binding)
    return binding


def compose_chartlink_039(
    graph: InteractionGraph,
    *,
    targets: Sequence[str],
    chart_kinds: Sequence[str] = ("select", "legend_filter", "brush"),
    grid_trigger: str = "grid.selection",
    binding_id: str = "chartlink_039",
    debounce_ms: int = 0,
) -> DashboardBinding:
    """CHARTLINK-039: bind Published hedron-chart events to DataTable/DataEditor selection.

    Does not create a parallel chart renderer; consumes 0.38 event kinds only.
    """
    if not targets:
        raise ValueError("compose_chartlink_039 requires one or more targets.")
    triggers: list[str] = [grid_trigger]
    for kind in chart_kinds:
        triggers.extend(triggers_from_hedron_chart_event(kind))
    graph.declare_inputs(*triggers)
    binding = DashboardBinding(
        id=binding_id,
        triggers=tuple(triggers),
        snapshot_inputs=(),
        targets=tuple(targets),
        action_id="cross_filter",
        debounce_ms=debounce_ms,
    )
    graph.register(binding)
    return binding
