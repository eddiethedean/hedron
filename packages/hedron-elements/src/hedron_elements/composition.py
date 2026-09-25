"""Typed browser composition contracts (COMPOSE/TRACE/FALLBACK-041)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$")
_FORBIDDEN_TRACE = frozenset({"payload", "detail", "value", "content", "query", "fragment"})
_CONCURRENCY_MODES = frozenset({"drop", "replace", "queue", "parallel"})
_PAYLOAD_KEYS = {
    "detail_keys": "detailKeys",
    "max_depth": "maxDepth",
    "max_payload_bytes": "maxPayloadBytes",
}


@dataclass(frozen=True, slots=True)
class CompositionEdge:
    id: str
    event: str
    action: str
    target: str
    detail_keys: tuple[str, ...] = ()
    authorization: str = "server"
    concurrency: Literal["drop", "replace", "queue", "parallel"] = "replace"
    max_depth: int = 8
    max_payload_bytes: int = 16_384
    fallback: Literal["native", "form", "link", "fragment"] = "native"

    def __post_init__(self) -> None:
        for label, value in (
            ("id", self.id),
            ("event", self.event),
            ("action", self.action),
            ("target", self.target),
        ):
            if not _ID.fullmatch(value):
                raise ValueError(f"invalid composition {label}: {value!r}")
        if not 1 <= self.max_depth <= 32:
            raise ValueError("max_depth must be between 1 and 32")
        if not 1 <= self.max_payload_bytes <= 65_536:
            raise ValueError("max_payload_bytes must be between 1 and 65536")
        if len(set(self.detail_keys)) != len(self.detail_keys):
            raise ValueError("detail_keys must be unique")
        if self.concurrency not in _CONCURRENCY_MODES:
            raise ValueError(f"invalid concurrency: {self.concurrency!r}")

    def as_payload(self) -> dict[str, object]:
        """Return the JS runner schema (camelCase keys, list detailKeys)."""
        payload: dict[str, object] = {}
        values: dict[str, object] = {
            "id": self.id,
            "event": self.event,
            "action": self.action,
            "target": self.target,
            "detail_keys": self.detail_keys,
            "authorization": self.authorization,
            "concurrency": self.concurrency,
            "max_depth": self.max_depth,
            "max_payload_bytes": self.max_payload_bytes,
            "fallback": self.fallback,
        }
        for key, value in values.items():
            out_key = _PAYLOAD_KEYS.get(key, key)
            payload[out_key] = list(self.detail_keys) if key == "detail_keys" else value
        return payload


@dataclass(frozen=True, slots=True)
class BrowserTrace:
    correlation_id: str
    element_id: str
    outcome: Literal["start", "success", "error", "canceled", "fallback"]
    edge_id: str | None = None
    operation_id: str | None = None
    diagnostic_code: str | None = None
    duration_ms: int | None = None

    def as_payload(self) -> dict[str, object]:
        values: dict[str, object] = {
            "correlation_id": self.correlation_id,
            "element_id": self.element_id,
            "outcome": self.outcome,
            "edge_id": self.edge_id,
            "operation_id": self.operation_id,
            "diagnostic_code": self.diagnostic_code,
            "duration_ms": self.duration_ms,
        }
        payload = {key: value for key, value in values.items() if value is not None}
        validate_trace_payload(payload)
        return payload


def validate_trace_payload(payload: dict[str, object]) -> None:
    forbidden = _FORBIDDEN_TRACE.intersection(key.lower() for key in payload)
    if forbidden:
        raise ValueError(f"content-bearing trace fields are forbidden: {sorted(forbidden)}")
    if len(str(payload).encode()) > 4096:
        raise ValueError("trace payload exceeds 4096 bytes")


__all__ = ["BrowserTrace", "CompositionEdge", "validate_trace_payload"]
