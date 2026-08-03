"""Visualization adapter contracts shared by hedron-charts and data sources."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from hedron_core.component import NodeLike

__all__ = [
    "DEFAULT_MAX_CHART_ROWS",
    "DEFAULT_MAX_PAYLOAD_BYTES",
    "ChartAccessibility",
    "ChartOutput",
    "VisualizationAdapter",
    "VisualizationLimits",
]


DEFAULT_MAX_CHART_ROWS = 10_000
DEFAULT_MAX_PAYLOAD_BYTES = 1_000_000


@dataclass(frozen=True, slots=True)
class VisualizationLimits:
    max_rows: int = DEFAULT_MAX_CHART_ROWS
    max_payload_bytes: int = DEFAULT_MAX_PAYLOAD_BYTES


@dataclass(frozen=True, slots=True)
class ChartAccessibility:
    """Accessibility contract for every chart output."""

    title: str
    description: str | None = None
    alt: str | None = None
    waiver: str | None = None
    tabular_fallback: Sequence[Mapping[str, Any]] | None = None

    def validated(self) -> ChartAccessibility:
        if not self.title.strip():
            raise ValueError("Chart title is required")
        if not (self.description or self.alt or self.waiver):
            raise ValueError(
                "Chart requires description, alt text, or an explicit accessibility waiver"
            )
        return self


@dataclass(frozen=True, slots=True)
class ChartOutput:
    """Compiled visualization payload ready for component rendering."""

    kind: str  # "svg" | "png" | "plotly-json" | "vega-lite" | "html"
    body: str | bytes
    accessibility: ChartAccessibility
    media_type: str = "application/json"
    assets: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    payload_bytes: int = 0


@runtime_checkable
class VisualizationAdapter(Protocol):
    """Compile a supported upstream value into a ChartOutput."""

    name: str
    optional_package: str | None

    def supports(self, value: Any) -> bool: ...

    def compile(
        self,
        value: Any,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput: ...

    def render_node(self, output: ChartOutput) -> NodeLike: ...
