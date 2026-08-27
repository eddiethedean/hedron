"""Explicit ChartInteraction bindings compiling onto ActionHandle effects."""

from __future__ import annotations

import inspect
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


def _projection_id(value: object) -> str:
    """Return a stable projection identifier for handles and components."""
    ident = getattr(value, "logical_id", None)
    if callable(ident):
        try:
            ident = ident()
        except TypeError:
            ident = None
    if isinstance(ident, str) and ident:
        return ident
    return type(value).__name__


def _invoke_command(command: object, handler: object, payload: object) -> object:
    """Invoke native and facade handles using their declared payload keyword."""
    if not callable(handler):
        return None
    signature = getattr(command, "handler_signature", None)
    if isinstance(signature, inspect.Signature):
        names = [
            parameter.name
            for parameter in signature.parameters.values()
            if parameter.name not in {"self", "request", "websocket"}
            and parameter.kind
            in {
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            }
        ]
        if names:
            return handler(**{names[0]: payload})
    return handler(payload)


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
                "Register the command with @app.action before composing ChartInteraction.",
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
        payload_type = self.payload
        refresh_targets = tuple(self.refreshes)

        def event_command(app: object) -> object:
            def on_chart_event(payload: object) -> object:
                typed = payload
                validator = getattr(payload_type, "model_validate", None)
                if callable(validator) and not isinstance(payload, payload_type):
                    typed = validator(payload)
                ids = getattr(typed, "ids", None)
                if isinstance(ids, list) and len(ids) > max_items:
                    copier = getattr(typed, "model_copy", None)
                    if callable(copier):
                        typed = copier(update={"ids": ids[:max_items]})
                handler = getattr(command, "__wrapped__", None) or getattr(command, "handler", None)
                result = _invoke_command(command, handler, typed)
                if result is not None:
                    return result
                from hedron.handles import BoundFragment, FragmentHandle, refresh

                targets = tuple(
                    item
                    for item in refresh_targets
                    if isinstance(item, (BoundFragment, FragmentHandle))
                )
                if targets:
                    return refresh(*targets)
                return result

            on_chart_event.__annotations__ = {"payload": payload_type, "return": object}
            return app.action(  # type: ignore[union-attr]
                f"/charts/{ident}/{event}",
                name=f"{ident}-{event}",
            )(on_chart_event)

        def export_command(app: object) -> object:
            from hedron import Text

            @app.action(f"/charts/{ident}/export", name=f"{ident}-export")  # type: ignore[union-attr]
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
                "command": _projection_id(command),
                "chart": _projection_id(chart),
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
            commands=(event_command, export_command),
            projections=(projection,),
            requirements=(FeatureRequirement(name="hedron-charts", required=True),),
        )
