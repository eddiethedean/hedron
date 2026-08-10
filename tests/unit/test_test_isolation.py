"""Regression coverage for the shared test-process isolation fixture."""

from __future__ import annotations

from tests.conftest import _reset_process_state

from hedron.concurrency import configure_concurrency, get_concurrency_config
from hedron.tracing import configure_tracing, get_trace_config
from hedron_core.audit import get_security_audit_sink, set_security_audit_sink
from hedron_core.cache import InMemoryCacheBackend, get_cache_backend, set_cache_backend
from hedron_core.jobs import InMemoryJobBackend, get_job_backend, set_job_backend


def test_shared_reset_restores_mutable_process_singletons() -> None:
    """A test that changes globals cannot influence the following test."""

    class Sink:
        def emit(self, event: object) -> None:
            del event

    class Cache(InMemoryCacheBackend):
        pass

    class Jobs(InMemoryJobBackend):
        pass

    configure_concurrency(enabled=True, max_in_flight=1, degrade_at=1)
    configure_tracing(enabled=True, sample_rate=1.0)
    set_cache_backend(Cache())
    set_job_backend(Jobs())
    set_security_audit_sink(Sink())

    _reset_process_state()

    assert get_concurrency_config().enabled is True
    assert get_concurrency_config().max_in_flight == 32
    assert get_trace_config().enabled is False
    assert type(get_cache_backend()) is InMemoryCacheBackend
    assert type(get_job_backend()) is InMemoryJobBackend
    assert type(get_security_audit_sink()).__name__ == "StructuredLogAuditSink"
