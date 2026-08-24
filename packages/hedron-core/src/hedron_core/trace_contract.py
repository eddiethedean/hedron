"""Portable, bounded interaction-trace encoding for phase 0.63 tooling."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from typing import Any

from hedron_core.action_state import ActionTrace
from hedron_core.security.secrets import redact_secret_like

__all__ = [
    "TRACE_CONTRACT_SCHEMA",
    "decode_interaction_trace",
    "encode_interaction_trace",
    "profile_interaction_trace",
]

TRACE_CONTRACT_SCHEMA = "hedron.interaction-trace.v1"
DEFAULT_TRACE_BYTES = 64 * 1024


def _safe_payload(trace: ActionTrace | Mapping[str, Any]) -> dict[str, Any]:
    source = trace.to_dict() if isinstance(trace, ActionTrace) else dict(trace)
    if source.get("schema") != TRACE_CONTRACT_SCHEMA:
        raise ValueError("unsupported interaction trace schema")
    if not isinstance(source.get("events"), list):
        raise ValueError("interaction trace events must be a list")
    return redact_secret_like(source)


def _encode(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode()


def encode_interaction_trace(
    trace: ActionTrace | Mapping[str, Any], *, max_bytes: int = DEFAULT_TRACE_BYTES
) -> bytes:
    """Encode a redacted trace deterministically, truncating oldest events to fit."""

    if max_bytes < 256:
        raise ValueError("max_bytes must be at least 256")
    payload = _safe_payload(trace)
    encoded = _encode(payload)
    if len(encoded) <= max_bytes:
        return encoded
    events = list(payload["events"])
    while events and len(encoded) > max_bytes:
        events.pop(0)
        candidate = {**payload, "events": events, "truncated": True}
        encoded = _encode(candidate)
        payload = candidate
    if len(encoded) > max_bytes:
        raise ValueError("interaction trace cannot fit within max_bytes")
    return encoded


def decode_interaction_trace(payload: bytes | str | Mapping[str, Any]) -> dict[str, Any]:
    """Decode and validate a trace without executing application code."""

    try:
        data = (
            json.loads(payload.decode("utf-8"))
            if isinstance(payload, bytes)
            else json.loads(payload)
            if isinstance(payload, str)
            else dict(payload)
        )
    except (UnicodeDecodeError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("invalid interaction trace JSON") from exc
    if not isinstance(data, dict) or data.get("schema") != TRACE_CONTRACT_SCHEMA:
        raise ValueError("unsupported interaction trace schema")
    events = data.get("events")
    if not isinstance(events, list) or any(not isinstance(event, dict) for event in events):
        raise ValueError("interaction trace events must be objects")
    return _safe_payload(data)


def profile_interaction_trace(payload: bytes | str | Mapping[str, Any]) -> dict[str, Any]:
    """Return a bounded read-only timeline summary with no payload retention.

    The trace envelope intentionally carries facts rather than a second
    profiler schema.  This projection recognizes only the public timeline
    fields and reports missing timing data explicitly; it never executes
    callbacks or retains arbitrary fact payloads.
    """

    data = decode_interaction_trace(payload)
    events = data["events"]
    phases = Counter(str(event.get("phase", "unknown")) for event in events)
    statuses = Counter(str(event["status"]) for event in events if event.get("status") is not None)
    timeline: list[dict[str, Any]] = []
    timing_samples = 0
    public_fact_keys = frozenset(
        {"component", "action", "request", "state", "cache", "focus", "failure"}
    )
    for index, event in enumerate(events):
        facts = event.get("facts") if isinstance(event.get("facts"), dict) else {}
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
