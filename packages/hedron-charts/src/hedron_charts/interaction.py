"""Explicit ChartInteraction bindings compiling onto ActionHandle effects."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from hedron_core.bundles import (
    MAX_CHART_SELECTION_ITEMS,
    MAX_EFFECT_FANOUT,
    FeatureBundle,
    FeatureConflictError,
    FeatureRequirement,
)
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.codes import HED_BUNDLE_0005, HED_BUNDLE_0007
from hedron_core.cross_filter import CHART_038_EVENT_KINDS
from hedron_core.diagnostics import DiagnosticSeverity, make_diagnostic

SUPPORTED_EVENTS = frozenset({"select", "inspect", "focus", "reset"})
EXPERIMENTAL_EVENTS = frozenset({"legend_filter", "brush", "drill_intent"})

__all__ = [
    "EXPERIMENTAL_EVENTS",
    "SUPPORTED_EVENTS",
    "ChartInteraction",
]


def _error(code: str, title: str, explanation: str, remediation: str) -> FeatureConflictError:
    return FeatureConflictError(
        make_diagnostic(
            code,
            severity=DiagnosticSeverity.ERROR,
            title=title,
            explanation=explanation,
            remediation=remediation,
        )
    )


@dataclass(frozen=True, slots=True)
class ChartInteraction:
    """Typed chart event → registered ActionHandle / effects. Not a chart runtime."""

    chart: object
    event: str
    payload: type[Any]
    command: object
    refreshes: Sequence[object] = ()
    max_items: int = 100
    provider: str = "hedron-charts"
    provider_version: str = "0.2.0"
    name: str | None = None
    experimental: bool = False

    def __post_init__(self) -> None:
        if self.event not in CHART_038_EVENT_KINDS:
            raise _error(
                HED_BUNDLE_0007,
                "Unknown ChartInteraction event",
                f"Event {self.event!r} is outside CHART_038_EVENT_KINDS.",
                "Use a closed first-party kind; adapter ChartEvent kinds stay Experimental.",
            )
        if self.event not in SUPPORTED_EVENTS and self.event not in EXPERIMENTAL_EVENTS:
            raise _error(
                HED_BUNDLE_0007,
                "ChartInteraction event is not in the 0.46 inventory",
                f"Event {self.event!r} is typed but has no 0.46 binding.",
                "Supported events are select, inspect, focus, and reset.",
            )
        if self.event in EXPERIMENTAL_EVENTS and not self.experimental:
            raise _error(
                HED_BUNDLE_0007,
                "Experimental ChartInteraction requires explicit opt-in",
                f"Event {self.event!r} stays Experimental until host+a11y evidence.",
                "Pass experimental=True or use a Supported event.",
            )
        if self.max_items > MAX_CHART_SELECTION_ITEMS or self.max_items < 1:
            raise _error(
                HED_BUNDLE_0005,
                "Chart selection cardinality bound",
                f"max_items={self.max_items} must be 1..{MAX_CHART_SELECTION_ITEMS}.",
                "Bound the selection in ChartInteraction(max_items=...).",
            )
        if len(self.refreshes) > MAX_EFFECT_FANOUT:
            raise _error(
                HED_BUNDLE_0005,
                "Chart effect fan-out bound exceeded",
                f"{len(self.refreshes)} refresh targets exceeds {MAX_EFFECT_FANOUT}.",
                "Declare fewer explicit refresh targets.",
            )
        if not hasattr(self.command, "logical_id"):
            raise _error(
                HED_BUNDLE_0007,
                "ChartInteraction.command must be a registered ActionHandle",
                "Event payloads are untrusted Pydantic input to a registered command.",
                "Register the command with @app.command before composing ChartInteraction.",
            )

    def to_bundle(self) -> FeatureBundle:
        ident = (
            self.name
            or f"{self.provider}:{self.event}:{getattr(self.command, 'logical_id', 'command')}"
        )
        command = self.command
        chart = self.chart
        event = self.event
        max_items = self.max_items

        def export_command(app: object) -> object:
            from hedron import Text

            @app.command(f"/charts/{ident}/export", name=f"{ident}-export")  # type: ignore[union-attr]
            def export() -> object:
                return Text("export")

            return export

        projection = PackageProjection(
            namespace=f"hedron.charts.interaction.{ident.replace(':', '.')}",
            provider=self.provider,
            provider_version=self.provider_version,
            capabilities=(
                ProjectionCapability(
                    name="ChartInteraction",
                    support="supported" if event in SUPPORTED_EVENTS else "experimental",
                ),
            ),
            data={
                "event": event,
                "command": getattr(command, "logical_id", ""),
                "chart": getattr(chart, "logical_id", type(chart).__name__),
                "max_items": max_items,
                "refreshes": [getattr(item, "logical_id", str(item)) for item in self.refreshes],
                "export_is": "ActionHandle",
                "compose_chartlink_039": False,
            },
            limitations=(
                "Supported events: select, inspect, focus, reset",
                "legend_filter/brush/drill_intent remain Experimental",
            ),
        )
        return FeatureBundle(
            logical_id=ident,
            provider=self.provider,
            provider_version=self.provider_version,
            views=(),
            commands=(export_command,),
            projections=(projection,),
            requirements=(FeatureRequirement(name="hedron-charts", required=True),),
        )
