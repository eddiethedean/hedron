"""Framework-boundary security audit sink (phase 0.13 / #9)."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable

from hedron_core.csrf import redact_secret_like

__all__ = [
    "SecurityAuditEvent",
    "SecurityAuditEventType",
    "SecurityAuditSink",
    "StructuredLogAuditSink",
    "emit_security_audit",
    "get_security_audit_sink",
    "reset_security_audit_for_tests",
    "set_security_audit_sink",
]


class SecurityAuditEventType(StrEnum):
    CSRF_REJECTED = "csrf_rejected"
    HTMX_TARGET_REJECTED = "htmx_target_rejected"
    EXPLORER_DENIED = "explorer_denied"
    PRODUCTION_GATE_FAILED = "production_gate_failed"


@dataclass(frozen=True, slots=True)
class SecurityAuditEvent:
    event_type: SecurityAuditEventType
    message: str
    attributes: Mapping[str, Any] = field(default_factory=dict)


@runtime_checkable
class SecurityAuditSink(Protocol):
    def emit(self, event: SecurityAuditEvent) -> None: ...


class StructuredLogAuditSink:
    """Default sink: redacted structured logging; never logs secrets."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger("hedron.audit")

    def emit(self, event: SecurityAuditEvent) -> None:
        safe = redact_secret_like(dict(event.attributes))
        self._logger.info(
            "security_audit event=%s message=%s attrs=%s",
            event.event_type.value,
            event.message,
            safe,
            extra={"hedron_audit_event": event.event_type.value, "hedron_audit_attrs": safe},
        )


_sink: SecurityAuditSink = StructuredLogAuditSink()


def get_security_audit_sink() -> SecurityAuditSink:
    return _sink


def set_security_audit_sink(sink: SecurityAuditSink | None) -> None:
    global _sink
    _sink = sink if sink is not None else StructuredLogAuditSink()


def reset_security_audit_for_tests() -> None:
    set_security_audit_sink(None)


def emit_security_audit(
    event_type: SecurityAuditEventType | str,
    message: str,
    *,
    attributes: Mapping[str, Any] | None = None,
) -> None:
    typed = (
        event_type
        if isinstance(event_type, SecurityAuditEventType)
        else SecurityAuditEventType(event_type)
    )
    # Redact before any sink so custom sinks cannot observe secrets.
    safe_attrs = redact_secret_like(dict(attributes or {}))
    if not isinstance(safe_attrs, dict):
        safe_attrs = {}
    event = SecurityAuditEvent(
        event_type=typed,
        message=message,
        attributes=safe_attrs,
    )
    try:
        get_security_audit_sink().emit(event)
    except Exception:
        # Audit sinks must never break request handling.
        # HED-AUDIT-0001 marks sink failure for catalog honesty.
        logging.getLogger("hedron.audit").exception("HED-AUDIT-0001 SecurityAuditSink failed")
