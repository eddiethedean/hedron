"""Deterministic scenario recording, virtual time, and bounds for hedron-sim.

A :class:`SimRecorder` captures the requests, swaps, triggers, delays, and
failures a demo performs against virtual time, and exports them as a JSON
scenario that can be replayed or diffed. Every entry point is bounded so an
imported scenario cannot exhaust memory or wall clock.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, cast

from hedron_sim.subset import require_supported_method, require_supported_swap

__all__ = [
    "HED_SIM_LIMIT",
    "SIM_SCENARIO_SCHEMA",
    "SimClock",
    "SimEvent",
    "SimLimitError",
    "SimLimits",
    "SimRecorder",
    "SimScenario",
    "export_scenario",
    "import_scenario",
]

# Mirrors hedron_conformance.authoring_loop.HED_SIM_LIMIT. hedron-sim does not depend
# on hedron-conformance; tests/unit/test_sim_054.py asserts the two agree.
HED_SIM_LIMIT = "HED-SIM-LIMIT"

SIM_SCENARIO_SCHEMA = "hedron-sim-scenario-1"

EventKind = Literal["request", "swap", "trigger", "delay", "failure"]

EVENT_KINDS: tuple[EventKind, ...] = ("request", "swap", "trigger", "delay", "failure")


class SimLimitError(ValueError):
    """Raised when a recording or import exceeds a declared simulator bound."""

    code: str = HED_SIM_LIMIT

    def __init__(self, message: str, *, limit: str, value: int, maximum: int) -> None:
        super().__init__(message)
        self.limit = limit
        self.value = value
        self.maximum = maximum


@dataclass(frozen=True, slots=True)
class SimLimits:
    """Bounds applied to recording and to imported scenarios."""

    max_bytes: int = 262_144
    max_steps: int = 512
    max_depth: int = 12
    max_time_ms: int = 600_000

    def as_dict(self) -> dict[str, int]:
        return {
            "max_bytes": self.max_bytes,
            "max_steps": self.max_steps,
            "max_depth": self.max_depth,
            "max_time_ms": self.max_time_ms,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> SimLimits:
        if not data:
            return cls()
        default = cls()
        return cls(
            max_bytes=int(data.get("max_bytes", default.max_bytes)),
            max_steps=int(data.get("max_steps", default.max_steps)),
            max_depth=int(data.get("max_depth", default.max_depth)),
            max_time_ms=int(data.get("max_time_ms", default.max_time_ms)),
        )

    def check_bytes(self, size: int) -> None:
        if size > self.max_bytes:
            raise SimLimitError(
                f"sim scenario payload of {size} bytes exceeds max_bytes={self.max_bytes}",
                limit="max_bytes",
                value=size,
                maximum=self.max_bytes,
            )

    def check_steps(self, count: int) -> None:
        if count > self.max_steps:
            raise SimLimitError(
                f"sim scenario of {count} steps exceeds max_steps={self.max_steps}",
                limit="max_steps",
                value=count,
                maximum=self.max_steps,
            )

    def check_depth(self, depth: int) -> None:
        if depth > self.max_depth:
            raise SimLimitError(
                f"sim scenario nesting depth {depth} exceeds max_depth={self.max_depth}",
                limit="max_depth",
                value=depth,
                maximum=self.max_depth,
            )

    def check_time_ms(self, elapsed_ms: int) -> None:
        if elapsed_ms > self.max_time_ms:
            raise SimLimitError(
                f"sim scenario clock {elapsed_ms}ms exceeds max_time_ms={self.max_time_ms}",
                limit="max_time_ms",
                value=elapsed_ms,
                maximum=self.max_time_ms,
            )


def _payload_depth(value: Any, *, depth: int = 1) -> int:
    children: list[Any]
    if isinstance(value, Mapping):
        children = list(cast(Mapping[str, Any], value).values())
    elif isinstance(value, (list, tuple)):
        children = list(cast(Sequence[Any], value))
    else:
        return depth
    if not children:
        return depth
    return max(_payload_depth(child, depth=depth + 1) for child in children)


@dataclass
class SimClock:
    """Virtual clock: scenarios advance time explicitly, never by sleeping."""

    now_ms: int = 0
    limits: SimLimits = field(default_factory=SimLimits)

    def advance(self, ms: int) -> int:
        """Advance virtual time by ``ms`` and return the new timestamp."""
        step = int(ms)
        if step < 0:
            raise ValueError(f"SimClock.advance requires a non-negative delay, got {ms!r}")
        self.limits.check_time_ms(self.now_ms + step)
        self.now_ms += step
        return self.now_ms

    def reset(self) -> None:
        self.now_ms = 0


@dataclass(frozen=True, slots=True)
class SimEvent:
    """One recorded scenario step at a virtual timestamp."""

    kind: EventKind
    name: str
    at_ms: int = 0
    detail: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "name": self.name,
            "at_ms": self.at_ms,
            "detail": dict(self.detail),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> SimEvent:
        kind = str(data.get("kind", ""))
        if kind not in EVENT_KINDS:
            raise ValueError(f"unknown sim scenario event kind {kind!r}; expected {EVENT_KINDS}")
        raw_detail: Any = data.get("detail") or {}
        if not isinstance(raw_detail, Mapping):
            raise ValueError(f"sim scenario event detail must be a mapping, got {type(raw_detail)}")
        return cls(
            kind=kind,
            name=str(data.get("name", "")),
            at_ms=int(data.get("at_ms", 0)),
            detail=dict(cast(Mapping[str, Any], raw_detail)),
        )


@dataclass(frozen=True, slots=True)
class SimScenario:
    """JSON-serializable recording of a simulator session."""

    scenario_id: str
    events: tuple[SimEvent, ...] = ()
    limits: SimLimits = field(default_factory=SimLimits)
    schema_version: str = SIM_SCENARIO_SCHEMA

    @property
    def duration_ms(self) -> int:
        return max((event.at_ms for event in self.events), default=0)

    def of_kind(self, kind: EventKind) -> tuple[SimEvent, ...]:
        return tuple(event for event in self.events if event.kind == kind)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "scenario_id": self.scenario_id,
            "limits": self.limits.as_dict(),
            "events": [event.as_dict() for event in self.events],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> SimScenario:
        version = str(data.get("schema_version") or "")
        if version != SIM_SCENARIO_SCHEMA:
            raise ValueError(f"sim scenario schema_version {version!r} != {SIM_SCENARIO_SCHEMA!r}")
        limits = SimLimits.from_dict(data.get("limits"))
        raw_events: Any = data.get("events") or []
        if not isinstance(raw_events, (list, tuple)):
            raise ValueError("sim scenario events must be a list")
        rows = cast(Sequence[Any], raw_events)
        limits.check_steps(len(rows))
        events: list[SimEvent] = []
        for row in rows:
            if not isinstance(row, Mapping):
                raise ValueError("each sim scenario event must be a mapping")
            event = SimEvent.from_dict(cast(Mapping[str, Any], row))
            limits.check_depth(_payload_depth(event.detail))
            limits.check_time_ms(event.at_ms)
            events.append(event)
        return cls(
            scenario_id=str(data.get("scenario_id") or "sim"),
            events=tuple(events),
            limits=limits,
            schema_version=version,
        )


class SimRecorder:
    """Record a deterministic simulator scenario against virtual time."""

    def __init__(
        self,
        scenario_id: str = "sim",
        *,
        limits: SimLimits | None = None,
        clock: SimClock | None = None,
    ) -> None:
        self.scenario_id = scenario_id
        self.limits = limits or SimLimits()
        self.clock = clock or SimClock(limits=self.limits)
        self._events: list[SimEvent] = []

    @property
    def events(self) -> tuple[SimEvent, ...]:
        return tuple(self._events)

    def _append(self, kind: EventKind, name: str, detail: Mapping[str, Any]) -> SimEvent:
        self.limits.check_steps(len(self._events) + 1)
        self.limits.check_depth(_payload_depth(dict(detail)))
        event = SimEvent(kind=kind, name=name, at_ms=self.clock.now_ms, detail=dict(detail))
        self._events.append(event)
        return event

    def record_request(
        self,
        method: str,
        path: str,
        *,
        target: str | None = None,
        status: int = 200,
    ) -> SimEvent:
        """Record a fragment/action request. ``method``/``path`` match ``AppScenario``."""
        normalized = require_supported_method(method)
        return self._append(
            "request",
            f"{normalized} {path}",
            {"method": normalized, "path": path, "target": target, "status": int(status)},
        )

    def record_swap(self, style: str, *, target: str) -> SimEvent:
        normalized = require_supported_swap(style)
        return self._append("swap", normalized, {"style": normalized, "target": target})

    def record_trigger(self, name: str, *, selector: str = "") -> SimEvent:
        return self._append("trigger", name, {"selector": selector})

    def record_delay(self, ms: int) -> SimEvent:
        """Advance the virtual clock and record the scripted delay."""
        self.clock.advance(ms)
        return self._append("delay", f"{int(ms)}ms", {"ms": int(ms)})

    def record_failure(self, code: str, message: str) -> SimEvent:
        return self._append("failure", code, {"code": code, "message": message})

    def scenario(self) -> SimScenario:
        return SimScenario(
            scenario_id=self.scenario_id,
            events=self.events,
            limits=self.limits,
        )


def export_scenario(scenario: SimScenario, *, indent: int | None = None) -> str:
    """Serialize ``scenario`` to deterministic JSON text within its byte bound."""
    text = json.dumps(scenario.as_dict(), indent=indent, sort_keys=True)
    scenario.limits.check_bytes(len(text.encode("utf-8")))
    return text


def import_scenario(
    source: str | bytes | Mapping[str, Any],
    *,
    limits: SimLimits | None = None,
) -> SimScenario:
    """Parse a scenario from JSON text/bytes or a mapping, enforcing every bound."""
    bounds = limits or SimLimits()
    if isinstance(source, (str, bytes)):
        raw = source.encode("utf-8") if isinstance(source, str) else source
        bounds.check_bytes(len(raw))
        loaded: Any = json.loads(raw.decode("utf-8"))
    else:
        loaded = dict(source)
        bounds.check_bytes(len(json.dumps(loaded, sort_keys=True).encode("utf-8")))
    if not isinstance(loaded, Mapping):
        raise ValueError("sim scenario document must be a JSON object")
    payload: dict[str, Any] = dict(cast(Mapping[str, Any], loaded))
    if limits is not None:
        payload["limits"] = bounds.as_dict()
    return SimScenario.from_dict(payload)
