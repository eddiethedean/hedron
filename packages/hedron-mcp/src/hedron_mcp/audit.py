"""Redacted structured audit events for MCP (AUDIT-032)."""

from __future__ import annotations

import re
from collections.abc import Mapping, MutableSequence
from dataclasses import dataclass, field
from typing import Any, cast

_SECRET_KEYS = frozenset(
    {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "authorization",
        "cookie",
        "session",
    }
)
_SECRET_RE = re.compile(r"(?i)(password|secret|token|api[_-]?key|bearer)\s*[:=]\s*\S+")


def redact_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        mapping = cast(Mapping[object, Any], value)
        return {
            str(k): ("[REDACTED]" if str(k).lower() in _SECRET_KEYS else redact_value(v))
            for k, v in mapping.items()
        }
    if isinstance(value, list):
        items = cast(list[Any], value)
        return [redact_value(item) for item in items]
    if isinstance(value, str):
        return _SECRET_RE.sub(r"\1=[REDACTED]", value)
    return value


@dataclass
class McpAuditEvent:
    """One redacted MCP audit record (owner prefix ``HED-MCP-``)."""

    code: str
    kind: str
    principal: str | None
    detail: Mapping[str, Any] = field(default_factory=lambda: cast(Mapping[str, Any], {}))

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "kind": self.kind,
            "principal": self.principal,
            "detail": dict(redact_value(self.detail)),
        }


@dataclass
class McpAuditLog:
    """Process-local audit buffer; multi-worker apps must attach an external sink."""

    events: MutableSequence[McpAuditEvent] = field(
        default_factory=lambda: cast(MutableSequence[McpAuditEvent], [])
    )
    sink: Any | None = None

    def emit(
        self,
        *,
        code: str,
        kind: str,
        principal: str | None,
        detail: Mapping[str, Any] | None = None,
    ) -> McpAuditEvent:
        event = McpAuditEvent(
            code=code,
            kind=kind,
            principal=principal,
            detail=dict(detail or {}),
        )
        self.events.append(event)
        if self.sink is not None:
            self.sink(event.as_dict())
        return event
