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
    detail: Mapping[str, Any] = field(default_factory=dict)

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
