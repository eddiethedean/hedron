"""Portable, bounded interaction-trace encoding for phase 0.63 tooling."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from typing import cast

from hedron_core.action_state import ActionTrace
from hedron_core.security.secrets import redact_secret_like
from hedron_core.typing_aliases import is_string_mapping

__all__ = [
    "TRACE_CONTRACT_SCHEMA",
    "decode_interaction_trace",
    "encode_interaction_trace",
    "profile_interaction_trace",
]

TRACE_CONTRACT_SCHEMA = "hedron.interaction-trace.v1"
DEFAULT_TRACE_BYTES = 64 * 1024


def _safe_payload(trace: ActionTrace | Mapping[str, object]) -> dict[str, object]:
    source: dict[str, object] = (
        dict(trace.to_dict()) if isinstance(trace, ActionTrace) else dict(trace)
    )
    if source.get("schema") != TRACE_CONTRACT_SCHEMA:
        raise ValueError("unsupported interaction trace schema")
    if not isinstance(source.get("events"), list):
        raise ValueError("interaction trace events must be a list")
    return redact_secret_like(source)


def _encode(payload: Mapping[str, object]) -> bytes:
    return json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode()


def encode_interaction_trace(
    trace: ActionTrace | Mapping[str, object], *, max_bytes: int = DEFAULT_TRACE_BYTES
) -> bytes:
    """Encode a redacted trace deterministically, truncating oldest events to fit."""

    if max_bytes < 256:
        raise ValueError("max_bytes must be at least 256")
    payload = _safe_payload(trace)
    encoded = _encode(payload)
    if len(encoded) <= max_bytes:
        return encoded
    events_value = payload["events"]
    if not isinstance(events_value, list):
        raise ValueError("interaction trace events must be a list")
    events = list(cast(list[object], events_value))
    while events and len(encoded) > max_bytes:
        events.pop(0)
        candidate = {**payload, "events": events, "truncated": True}
        encoded = _encode(candidate)
        payload = candidate
    if len(encoded) > max_bytes:
        raise ValueError("interaction trace cannot fit within max_bytes")
    return encoded


def decode_interaction_trace(payload: bytes | str | Mapping[str, object]) -> dict[str, object]:
    """Decode and validate a trace without executing application code."""

    try:
        decoded: object = (
            json.loads(payload.decode("utf-8"))
            if isinstance(payload, bytes)
            else json.loads(payload)
            if isinstance(payload, str)
            else dict(payload)
        )
    except (UnicodeDecodeError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("invalid interaction trace JSON") from exc
    if not is_string_mapping(decoded) or decoded.get("schema") != TRACE_CONTRACT_SCHEMA:
        raise ValueError("unsupported interaction trace schema")
    events = decoded.get("events")
    if not isinstance(events, list) or any(
        not is_string_mapping(event) for event in cast(list[object], events)
    ):
        raise ValueError("interaction trace events must be objects")
    return _safe_payload(decoded)


def profile_interaction_trace(
    payload: bytes | str | Mapping[str, object],
) -> dict[str, object]:
    """Return a bounded read-only timeline summary with no payload retention.

    The trace envelope intentionally carries facts rather than a second
    profiler schema.  This projection recognizes only the public timeline
    fields and reports missing timing data explicitly; it never executes
    callbacks or retains arbitrary fact payloads.
    """

    data = decode_interaction_trace(payload)
    events = cast(list[Mapping[str, object]], data["events"])
    phases = Counter(str(event.get("phase", "unknown")) for event in events)
    statuses = Counter(str(event["status"]) for event in events if event.get("status") is not None)
    timeline: list[dict[str, object]] = []
    timing_samples = 0
    public_fact_keys = frozenset(
        {"component", "action", "request", "state", "cache", "focus", "failure"}
    )
    for index, event in enumerate(events):
        facts_value = event.get("facts")
        facts = (
            cast(dict[str, object], facts_value)
            if isinstance(facts_value, dict)
            else dict[str, object]()
        )
        timing = facts.get("duration_ms")
        if isinstance(timing, (int, float)) and not isinstance(timing, bool):
            timing_samples += 1
        timeline.append(
            {
                "index": index,
                "phase": str(event.get("phase", "unknown")),
                "operation_id": event.get("operation_id"),
                "generation": event.get("generation"),
                "target": event.get("target"),
                "status": event.get("status"),
                "facts": {
                    key: facts[key]
                    for key in sorted(public_fact_keys & set(facts))
                    if isinstance(facts[key], (str, int, float, bool)) or facts[key] is None
                },
                "timing": timing if isinstance(timing, (int, float)) else None,
            }
        )
    return {
        "schema": "hedron.interaction-profile/1",
        "trace_schema": TRACE_CONTRACT_SCHEMA,
        "event_count": len(events),
        "truncated": bool(data.get("truncated", False)),
        "phases": dict(sorted(phases.items())),
        "statuses": dict(sorted(statuses.items())),
        "timing": {
            "clock": "event-fact-or-unavailable",
            "samples": timing_samples,
            "complete": timing_samples == len(events) if events else True,
        },
        "timeline": timeline,
        "payloads_retained": False,
    }
