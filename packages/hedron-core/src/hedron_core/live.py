"""Portable SSE framing and live observation contracts (phase 0.10)."""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any

__all__ = [
    "LiveObservation",
    "SseEvent",
    "encode_sse",
    "iter_sse_bytes",
    "job_status_sse_events",
]


@dataclass(frozen=True, slots=True)
class SseEvent:
    """One Server-Sent Event frame."""

    data: str
    event: str | None = None
    id: str | None = None
    retry_ms: int | None = None


@dataclass(frozen=True, slots=True)
class LiveObservation:
    """Portable live observation payload for a declared region."""

    region_id: str
    html: str
    event: str = "message"
    event_id: str | None = None
    terminal: bool = False


def encode_sse(event: SseEvent) -> str:
    lines: list[str] = []
    if event.id is not None:
        lines.append(f"id: {event.id}")
    if event.event is not None:
        lines.append(f"event: {event.event}")
    if event.retry_ms is not None:
        lines.append(f"retry: {int(event.retry_ms)}")
    for part in event.data.splitlines() or [""]:
        lines.append(f"data: {part}")
    return "\n".join(lines) + "\n\n"


def iter_sse_bytes(events: Iterator[SseEvent]) -> Iterator[bytes]:
    for event in events:
        yield encode_sse(event).encode("utf-8")


def job_status_sse_events(
    *,
    job_id: str,
    state: str,
    message_html: str,
    event_id: str | None = None,
    retry_ms: int = 2000,
    terminal: bool = False,
) -> list[SseEvent]:
    """Encode a job-status observation as SSE events (JOB-006)."""
    payload = json.dumps(
        {"job_id": job_id, "state": state, "terminal": terminal},
        separators=(",", ":"),
    )
    events = [
        SseEvent(data=payload, event="job-status", id=event_id or job_id, retry_ms=retry_ms),
        SseEvent(data=message_html, event="message", id=event_id or job_id),
    ]
    if terminal:
        events.append(SseEvent(data="close", event="hedron-close", id=event_id or job_id))
    return events


def observation_to_sse(obs: LiveObservation) -> SseEvent:
    return SseEvent(data=obs.html, event=obs.event, id=obs.event_id)


def client_state_payload(values: Mapping[str, Any]) -> str:
    return json.dumps(dict(values), separators=(",", ":"), default=str)
