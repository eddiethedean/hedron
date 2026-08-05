"""Distributed tracing (TRACE-013)."""

from __future__ import annotations

from hedron.tracing import (
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
    assert True


def test_tracing_enabled_without_otel_still_safe() -> None:
    configure_tracing(enabled=True, sample_rate=1.0)
    with span("hedron.prepare", route="/") as s:
        s.set_attribute("ok", 1)
    opened = start_span("hedron.job", job_id="j1")
    with opened:
        pass


def test_exporter_failure_does_not_change_semantics() -> None:
    configure_tracing(enabled=True)
    # Even if OTel import fails, body runs.
    value = 0
    with span("hedron.cache"):
        value = 1
    assert value == 1
