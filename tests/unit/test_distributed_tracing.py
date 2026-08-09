"""Distributed tracing (TRACE-013)."""

from __future__ import annotations

from hedron.tracing import (
    _RecordingSpan,
    configure_tracing,
    reset_tracing_for_tests,
    span,
    start_span,
)


def setup_function() -> None:
    reset_tracing_for_tests()


def teardown_function() -> None:
    reset_tracing_for_tests()


def test_tracing_disabled_is_noop() -> None:
    configure_tracing(enabled=False)
    with span("hedron.render", secret_token="abc") as s:
        s.set_attribute("password", "nope")
        assert type(s).__name__ == "TracingDisabled"
    opened = start_span("hedron.job", job_id="j1")
    assert type(opened).__name__ == "TracingDisabled"


def test_tracing_enabled_without_otel_still_safe() -> None:
    configure_tracing(enabled=True, sample_rate=1.0)
    ran = False
    with span("hedron.prepare", route="/") as s:
        s.set_attribute("ok", 1)
        ran = True
    assert ran is True
    opened = start_span("hedron.job", job_id="j1")
    with opened:
        opened.set_attribute("job", "j1")
    # Without OTel the span may be Recording or Disabled; body must complete.
    assert type(opened).__name__ in {"_RecordingSpan", "TracingDisabled"}


def test_exporter_failure_does_not_change_semantics() -> None:
    configure_tracing(enabled=True)
    # Even if OTel import fails, body runs (HED-TRACE-0001 logged on exporter miss).
    value = 0
    with span("hedron.cache"):
        value = 1
    assert value == 1


def test_sample_rate_zero_is_noop() -> None:
    configure_tracing(enabled=True, sample_rate=0.0)
    with span("hedron.render", password="secret") as s:
        assert type(s).__name__ == "TracingDisabled"
        s.set_attribute("token", "x")


def test_recording_span_redacts_secret_attributes() -> None:
    configure_tracing(enabled=True, sample_rate=1.0)
    recording = _RecordingSpan("hedron.render", {"password": "hunter2", "route": "/x"})
    assert recording.attributes.get("password") == "[redacted]"
    assert recording.attributes.get("route") == "/x"
    recording.set_attribute("api_key", "abc")
    assert recording.attributes.get("api_key") == "[redacted]"
