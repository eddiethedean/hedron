"""Unified security event schema (0.56)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from typing import Any

EVENT_CODES = (
    "ctx.rejected",
    "sens.denied",
    "sink.denied",
    "egress.denied",
    "intent.rejected",
    "budget.exceeded",
    "policy.misconfigured",
)


@dataclass(frozen=True, slots=True)
class SecurityEvent:
    code: str
    control_version: str = "0.56"
    profile_name: str = "standard"
    ownership: str = "hedron-core"
    correlation_id: str = ""
    fingerprint: str = ""
    detail: Mapping[str, Any] = field(default_factory=dict[str, Any])

    def __post_init__(self) -> None:
        if self.code not in EVENT_CODES:
            raise ValueError(f"unknown security event code: {self.code}")

    def redacted_dict(self) -> dict[str, Any]:
        # Drop high-cardinality attacker-controlled subjects from metrics labels.
        safe_detail = {
            key: value
            for key, value in dict(self.detail).items()
            if key
            not in {
                "url",
                "filename",
                "subject",
                "raw_policy",
                "payload",
            }
        }
        data = asdict(self)
        data["detail"] = safe_detail
        return data


_EVENT_SINK: list[SecurityEvent] = []
_EVENT_SINK_LIMIT = 1_000


def emit_security_event(event: SecurityEvent) -> None:
    """Record a redacted security event (process-local bounded ring)."""
    _EVENT_SINK.append(event)
    if len(_EVENT_SINK) > _EVENT_SINK_LIMIT:
        del _EVENT_SINK[: len(_EVENT_SINK) - _EVENT_SINK_LIMIT]


def recent_security_events() -> tuple[SecurityEvent, ...]:
    return tuple(_EVENT_SINK)


def clear_security_events() -> None:
    _EVENT_SINK.clear()
