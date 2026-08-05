"""SecurityAuditSink (AUDIT-013)."""

from __future__ import annotations

from hedron_core.audit import (
    SecurityAuditEvent,
    SecurityAuditEventType,
    emit_security_audit,
    reset_security_audit_for_tests,
    set_security_audit_sink,
)
from hedron_core.csrf import redact_secret_like


class _Capture:
    def __init__(self) -> None:
        self.events: list[SecurityAuditEvent] = []

    def emit(self, event: SecurityAuditEvent) -> None:
        self.events.append(event)


def setup_function() -> None:
    reset_security_audit_for_tests()


def teardown_function() -> None:
    reset_security_audit_for_tests()


def test_audit_emits_expected_event_types() -> None:
    sink = _Capture()
    set_security_audit_sink(sink)
    for event_type in SecurityAuditEventType:
        emit_security_audit(event_type, "test", attributes={"path": "/x"})
    assert {e.event_type for e in sink.events} == set(SecurityAuditEventType)


def test_audit_redacts_secrets() -> None:
    payload = redact_secret_like({"password": "secret", "path": "/login", "token": "abc"})
    assert payload["password"] == "[redacted]"
    assert payload["token"] == "[redacted]"
    assert payload["path"] == "/login"


def test_sink_failure_is_swallowed() -> None:
    class Boom:
        def emit(self, event: SecurityAuditEvent) -> None:
            raise RuntimeError("sink down")

    set_security_audit_sink(Boom())  # type: ignore[arg-type]
    emit_security_audit(SecurityAuditEventType.CSRF_REJECTED, "x")
