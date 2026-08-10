"""Interaction-graph recorder and deterministic replay (RFC-0040 / REPLAY-017).

Recordings are contract fixtures with redacted payloads. Replay applies scripted
stale/duplicate/disconnect/conflict schedules without timing sleeps.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass, field
from typing import Any, Literal

from hedron_core.codes import HED_GRAPH_0006, HED_PATCH_0002
from hedron_core.csrf import redact_secret_like
from hedron_core.dashboard import DashboardBinding, InteractionGraph
from hedron_core.patches import PropertyPatch, apply_property_patch

__all__ = [
    "GraphRecording",
    "GraphReplayEvent",
    "GraphReplayKind",
    "record_exchange",
    "replay",
]

GraphReplayKind = Literal[
    "trigger",
    "patch",
    "stale",
    "duplicate",
    "disconnect",
    "conflict",
]

_VALID_KINDS: frozenset[str] = frozenset(
    {"trigger", "patch", "stale", "duplicate", "disconnect", "conflict"}
)

_REDACT_KEYS = frozenset({"password", "token", "secret", "authorization"})


@dataclass(frozen=True, slots=True)
class GraphReplayEvent:
    """One recorded trigger/action/patch exchange or scripted adversarial step."""

    correlation_id: str
    binding_id: str
    kind: GraphReplayKind
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GraphRecording:
    """Ordered exchange fixture for deterministic graph replay."""

    events: list[GraphReplayEvent] = field(default_factory=list)
    initial_regions: dict[str, Any] = field(default_factory=dict)


def record_exchange(
    recording: GraphRecording,
    *,
    correlation_id: str,
    binding_id: str,
    kind: GraphReplayKind | str,
    payload: Mapping[str, Any] | None = None,
) -> GraphReplayEvent:
    """Append a redacted exchange event to ``recording`` and return it."""
    if kind not in _VALID_KINDS:
        raise ValueError(
            f"Unknown graph replay kind {kind!r}; expected one of {sorted(_VALID_KINDS)}"
        )
    redacted = _redact_payload(dict(payload or {}))
    event = GraphReplayEvent(
        correlation_id=correlation_id,
        binding_id=binding_id,
        kind=kind,  # type: ignore[arg-type]
        payload=redacted,
    )
    recording.events.append(event)
    return event


def replay(
    graph: InteractionGraph,
    recording: GraphRecording,
    *,
    schedule: list[str] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Replay ``recording`` against ``graph`` without sleeping.

    Returns ``(final_region_snapshot, audit)``. ``schedule`` injects scripted
    stale/duplicate/disconnect/conflict steps after recorded exchanges (or alone).
    """
    regions: dict[str, Any] = copy.deepcopy(dict(recording.initial_regions))
    audit: list[dict[str, Any]] = []
    seen_correlations: set[str] = set()

    queue: list[GraphReplayEvent] = list(recording.events)
    for kind in schedule or ():
        if kind not in _VALID_KINDS:
            raise ValueError(
                f"Unknown schedule kind {kind!r}; expected one of {sorted(_VALID_KINDS)}"
            )
        if kind in {"trigger", "patch"}:
            continue
        anchor = queue[-1].binding_id if queue else ""
        queue.append(
            GraphReplayEvent(
                correlation_id=f"schedule:{kind}",
                binding_id=anchor,
                kind=kind,  # type: ignore[arg-type]
                payload={},
            )
        )

    for event in queue:
        if event.kind not in _VALID_KINDS:
            raise ValueError(f"Unknown graph replay kind {event.kind!r}")

        if event.kind == "disconnect":
            audit.append(
                {
                    "kind": "disconnect",
                    "correlation_id": event.correlation_id,
                    "binding_id": event.binding_id,
                    "code": HED_GRAPH_0006,
                }
            )
            break

        if event.kind == "stale":
            audit.append(
                {
                    "kind": "stale",
                    "correlation_id": event.correlation_id,
                    "binding_id": event.binding_id,
                    "rejected": True,
                }
            )
            continue

        if event.kind == "duplicate":
            audit.append(
                {
                    "kind": "duplicate",
                    "correlation_id": event.correlation_id,
                    "binding_id": event.binding_id,
                    "skipped": True,
                }
            )
            continue

        if event.kind == "conflict":
            audit.append(
                {
                    "kind": "conflict",
                    "correlation_id": event.correlation_id,
                    "binding_id": event.binding_id,
                    "code": HED_PATCH_0002,
                    "full_fragment_fallback": True,
                }
            )
            continue

        if event.correlation_id and event.correlation_id in seen_correlations:
            audit.append(
                {
                    "kind": "duplicate",
                    "correlation_id": event.correlation_id,
                    "binding_id": event.binding_id,
                    "skipped": True,
                }
            )
            continue
        if event.correlation_id:
            seen_correlations.add(event.correlation_id)

        if event.kind == "trigger":
            _apply_trigger(graph, regions, event, audit)
        elif event.kind == "patch":
            _apply_patch(regions, event, audit)

    return regions, audit


def _redact_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return redact_secret_like(dict(payload), keys=_REDACT_KEYS)


def _binding(graph: InteractionGraph, binding_id: str) -> DashboardBinding | None:
    for binding in graph.bindings():
        if binding.id == binding_id:
            return binding
    return None


def _apply_trigger(
    graph: InteractionGraph,
    regions: MutableMapping[str, Any],
    event: GraphReplayEvent,
    audit: list[dict[str, Any]],
) -> None:
    payload = dict(event.payload)
    region_updates = payload.get("regions")
    if isinstance(region_updates, Mapping):
        for target_id, state in region_updates.items():
            regions[str(target_id)] = copy.deepcopy(state)
    else:
        binding = _binding(graph, event.binding_id)
        targets = binding.targets if binding is not None else ()
        for target_id in targets:
            if target_id in payload:
                regions[target_id] = copy.deepcopy(payload[target_id])
    audit.append(
        {
            "kind": "trigger",
            "correlation_id": event.correlation_id,
            "binding_id": event.binding_id,
            "applied": True,
        }
    )


def _apply_patch(
    regions: MutableMapping[str, Any],
    event: GraphReplayEvent,
    audit: list[dict[str, Any]],
) -> None:
    payload = dict(event.payload)
    target_id = str(payload.get("target_id") or "")
    path = str(payload.get("path") or "")
    op = payload.get("op", "assign")
    if not target_id:
        audit.append(
            {
                "kind": "patch",
                "correlation_id": event.correlation_id,
                "binding_id": event.binding_id,
                "applied": False,
                "reason": "missing target_id",
            }
        )
        return
    patch = PropertyPatch(
        target_id=target_id,
        path=path,
        op=str(op),
        value=payload.get("value"),
        expected_version=payload.get("expected_version"),  # type: ignore[arg-type]
    )
    try:
        updated = apply_property_patch(dict(regions), patch)
        regions.clear()
        regions.update(updated)
        audit.append(
            {
                "kind": "patch",
                "correlation_id": event.correlation_id,
                "binding_id": event.binding_id,
                "applied": True,
                "target_id": target_id,
            }
        )
    except Exception as exc:  # noqa: BLE001
        audit.append(
            {
                "kind": "conflict",
                "correlation_id": event.correlation_id,
                "binding_id": event.binding_id,
                "code": getattr(exc, "code", HED_PATCH_0002),
                "full_fragment_fallback": True,
                "error": str(exc),
            }
        )
