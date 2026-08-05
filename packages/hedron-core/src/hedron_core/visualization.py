"""Visualization adapter contracts shared by hedron-charts and data sources."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from hedron_core.component import NodeLike
from hedron_core.diagnostics import error

__all__ = [
    "DEFAULT_MAX_CHART_ROWS",
    "DEFAULT_MAX_PAYLOAD_BYTES",
    "ChartAccessibility",
    "ChartAnnotation",
    "ChartEvent",
    "ChartOutput",
    "VisualizationAdapter",
    "VisualizationLimits",
    "authorized_chart_event",
    "validate_annotation",
    "validate_chart_event",
]


DEFAULT_MAX_CHART_ROWS = 10_000
DEFAULT_MAX_PAYLOAD_BYTES = 1_000_000

_CHART_EVENT_KINDS = frozenset(
    {
        "hover",
        "click",
        "click-annotation",
        "box",
        "lasso",
        "relayout",
        "restyle",
        "legend",
        "extend",
        "prepend",
    }
)
_ANNOTATION_KINDS = frozenset({"point", "region", "line", "text", "shape"})


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


@dataclass(frozen=True, slots=True)
class ChartEvent:
    kind: str
    trace_id: str
    point_index: int | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)
    auth_context: Mapping[str, Any] = field(default_factory=dict)
    debounce_ms: int = 0
    coalesce_key: str | None = None
    accessible_fallback: str | None = None


@dataclass(frozen=True, slots=True)
class ChartAnnotation:
    kind: str
    label: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    trace_id: str | None = None
    description: str | None = None


def validate_chart_event(event: ChartEvent, *, max_payload_bytes: int = 65_536) -> ChartEvent:
    if event.kind not in _CHART_EVENT_KINDS:
        raise error(
            "HED-CHART-0010",
            title="Unknown chart event kind",
            explanation=f"{event.kind!r} is not a supported chart event.",
            remediation=f"Use one of: {sorted(_CHART_EVENT_KINDS)}",
        )
    if not event.trace_id:
        raise error(
            "HED-CHART-0011",
            title="Chart event missing trace identity",
            explanation="Stable trace_id is required for authorized chart events.",
            remediation="Assign stable trace identities in the adapter.",
        )
    if event.debounce_ms < 0:
        raise ValueError("debounce_ms must be >= 0")
    encoded = json.dumps(dict(event.payload), default=str).encode("utf-8")
    if len(encoded) > max_payload_bytes:
        raise error(
            "HED-CHART-0012",
            title="Chart event payload exceeds budget",
            explanation=f"Payload is {len(encoded)} bytes; max is {max_payload_bytes}.",
            remediation="Debounce/coalesce or reduce event payloads.",
        )
    return event


def authorized_chart_event(
    event: ChartEvent,
    *,
    allowed_kinds: frozenset[str],
) -> ChartEvent:
    event = validate_chart_event(event)
    if event.kind not in allowed_kinds:
        raise error(
            "HED-CHART-0013",
            title="Chart event kind not authorized",
            explanation=f"{event.kind!r} is not in the allowlist for this actor.",
            remediation="Declare allowed event kinds on the interaction boundary.",
        )
    return event


def validate_annotation(ann: ChartAnnotation) -> ChartAnnotation:
    if ann.kind not in _ANNOTATION_KINDS:
        raise ValueError(f"Unknown annotation kind {ann.kind!r}")
    if not ann.label.strip():
        raise ValueError("Annotation label is required")
    if "html" in {k.lower() for k in ann.payload}:
        raise error(
            "HED-CHART-0014",
            title="Raw HTML annotations are forbidden",
            explanation="Annotation payloads must stay typed and policy-bounded.",
            remediation="Use label/description fields instead of raw HTML.",
        )
    return ann


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
