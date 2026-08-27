"""Explicit MapInteraction bindings compiling onto ActionHandle effects."""

from __future__ import annotations

import inspect
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol, cast

from pydantic import BaseModel, ConfigDict, Field

from hedron_core.bundles import (
    MAX_EFFECT_FANOUT,
    FeatureBundle,
    FeatureConflictError,
    FeatureRequirement,
)
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.codes import (
    HED_BUNDLE_0005,
    HED_BUNDLE_0007,
    HED_MAP_EVENT_0001,
    HED_MAP_EVENT_0002,
)
from hedron_core.cross_filter import MAP_VIEWPORT_TRIGGER
from hedron_core.diagnostics import DiagnosticSeverity, make_diagnostic
from hedron_maps.limits import EVENT_CARDINALITY, EVENT_PAYLOAD_BYTES

SUPPORTED_EVENTS = frozenset(
    {
        "feature-selected",
        "feature-activated",
        "viewport-changed",
        "layer-visibility-changed",
        "map-loaded",
        "map-failed",
    }
)

__all__ = [
    "SUPPORTED_EVENTS",
    "FeatureActivated",
    "FeatureSelected",
    "LayerVisibilityChanged",
    "MapFailed",
    "MapInteraction",
    "MapLoaded",
    "ViewportChanged",
]


class _Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FeatureSelected(_Payload):
    ids: list[str] = Field(default_factory=list)
    layer: str | None = None


class FeatureActivated(_Payload):
    id: str
    layer: str | None = None


class ViewportChanged(_Payload):
    west: float
    south: float
    east: float
    north: float
    zoom: float
    trigger: str = MAP_VIEWPORT_TRIGGER


class LayerVisibilityChanged(_Payload):
    layer: str
    visible: bool


class MapLoaded(_Payload):
    ok: bool = True


class MapFailed(_Payload):
    code: str
    message: str = ""


class _CommandHost(Protocol):
    _interaction_commands: dict[str, str]


EVENT_PAYLOADS: dict[str, type[BaseModel]] = {
    "feature-selected": FeatureSelected,
    "feature-activated": FeatureActivated,
    "viewport-changed": ViewportChanged,
    "layer-visibility-changed": LayerVisibilityChanged,
    "map-loaded": MapLoaded,
    "map-failed": MapFailed,
}


def _projection_id(value: object) -> str:
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
class MapInteraction:
    """Typed map event → registered ActionHandle / effects. Not a map runtime."""

    map: object
    event: str
    payload: type[Any]
    command: object
    refreshes: Sequence[object] = ()
    max_items: int = 100
    provider: str = "hedron-maps"
    provider_version: str = "0.1.0"
    name: str | None = None

    def __post_init__(self) -> None:
        if self.event not in SUPPORTED_EVENTS:
            raise _error(
                HED_MAP_EVENT_0001,
                "Unknown MapInteraction event",
                f"Event {self.event!r} is outside the locked 0.47 set.",
                "Use feature-selected, feature-activated, viewport-changed, "
                "layer-visibility-changed, map-loaded, or map-failed.",
            )
        expected = EVENT_PAYLOADS[self.event]
        if self.payload is not expected and not issubclass(self.payload, expected):
            raise _error(
                HED_MAP_EVENT_0001,
                "MapInteraction payload type mismatch",
                f"Event {self.event!r} expects {expected.__name__}.",
                f"Pass payload={expected.__name__}.",
            )
        if self.max_items > EVENT_CARDINALITY or self.max_items < 1:
            raise _error(
                HED_MAP_EVENT_0002,
                "Map selection cardinality bound",
                f"max_items={self.max_items} must be 1..{EVENT_CARDINALITY}.",
                "Bound the selection in MapInteraction(max_items=...).",
            )
        if len(self.refreshes) > MAX_EFFECT_FANOUT:
            raise _error(
                HED_BUNDLE_0005,
                "Map effect fan-out bound exceeded",
                f"{len(self.refreshes)} refresh targets exceeds {MAX_EFFECT_FANOUT}.",
                "Declare fewer explicit refresh targets.",
            )
        if not hasattr(self.command, "logical_id"):
            raise _error(
                HED_BUNDLE_0007,
                "MapInteraction.command must be a registered ActionHandle",
                "Event payloads are untrusted Pydantic input to a registered command.",
                "Register the command with @app.action before composing MapInteraction.",
            )

    def to_bundle(self) -> FeatureBundle:
        ident = (
            (self.name or f"maps-{self.event}-{getattr(self.command, 'logical_id', 'command')}")
            .replace(":", "-")
            .replace(".", "-")
            .lower()
        )
        command = self.command
        event = self.event
        max_items = self.max_items
        payload_type = self.payload
        refresh_targets = tuple(self.refreshes)
        map_ref = self.map
        path = f"/maps/{ident}/{event}"
        commands = getattr(map_ref, "_interaction_commands", None)
        if not isinstance(commands, dict):
            try:
                host = cast(_CommandHost, map_ref)
                host._interaction_commands = {}
                commands = host._interaction_commands
            except (AttributeError, TypeError):
                commands = None
        if isinstance(commands, dict):
            commands[event] = path

        def event_command(app: object) -> object:
            def on_map_event(payload: object) -> object:
                typed = payload
                validator = getattr(payload_type, "model_validate", None)
                if callable(validator) and not isinstance(payload, payload_type):
                    typed = validator(payload)
                encoded = str(typed)
                if len(encoded.encode("utf-8")) > EVENT_PAYLOAD_BYTES:
                    raise _error(
                        HED_MAP_EVENT_0002,
                        "Map event payload too large",
                        f"Payload exceeded {EVENT_PAYLOAD_BYTES} bytes.",
                        "Reduce selected ids or viewport metadata.",
                    )
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

            on_map_event.__annotations__ = {"payload": payload_type, "return": object}
            return app.action(  # type: ignore[union-attr]
                path,
                name=f"{ident}-{event}",
            )(on_map_event)

        projection = PackageProjection(
            namespace=f"hedron.maps.interaction.{ident}",
            provider=self.provider,
            provider_version=self.provider_version,
            capabilities=(ProjectionCapability(name="MapInteraction", support="supported"),),
            data={
                "event": event,
                "command": _projection_id(command),
                "map": _projection_id(map_ref),
                "max_items": max_items,
                "command_path": path,
                "refreshes": [_projection_id(item) for item in self.refreshes],
                "viewport_trigger": MAP_VIEWPORT_TRIGGER,
                "reuse_chart_interaction": False,
            },
            limitations=(
                "Supported events: feature-selected, feature-activated, viewport-changed, "
                "layer-visibility-changed, map-loaded, map-failed",
                "viewport-changed is debounced onto map.viewport",
            ),
        )
        return FeatureBundle(
            logical_id=ident,
            provider=self.provider,
            provider_version=self.provider_version,
            views=(),
            commands=(event_command,),
            projections=(projection,),
            requirements=(FeatureRequirement(name="hedron-maps", required=True),),
        )
