"""Process-wide job backend installation."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar

from hedron_core.durability import is_process_local
from hedron_core.jobs.backend import JobBackend
from hedron_core.jobs.memory import InMemoryJobBackend

_backend: JobBackend = InMemoryJobBackend()
_scoped_backend: ContextVar[JobBackend | None] = ContextVar("hedron_job_backend", default=None)


def get_job_backend() -> JobBackend:
    return _scoped_backend.get() or _backend


@contextmanager
def use_job_backend(backend: JobBackend) -> Generator[None, None, None]:
    """Temporarily bind a job backend to the current application context."""
    token = _scoped_backend.set(backend)
    try:
        yield
    finally:
        _scoped_backend.reset(token)


def set_job_backend(backend: JobBackend) -> None:
    global _backend
    import logging

    from hedron_core.compile_gate import is_production_env

    if is_production_env() and is_process_local(backend):
        from hedron_core.audit import SecurityAuditEventType, emit_security_audit

        emit_security_audit(
            SecurityAuditEventType.PRODUCTION_GATE_FAILED,
            "InMemoryJobBackend refused in production",
            attributes={"backend": type(backend).__name__, "via": "set_job_backend"},
        )
        raise RuntimeError(
            "InMemoryJobBackend is not allowed under HEDRON_ENV=production. "
            "Call set_job_backend(...) with Redis/Celery/RQ, or unset production "
            "for local demos."
        )
    scoped = _scoped_backend.get()
    if scoped is not None:
        _scoped_backend.set(backend)
    else:
        _backend = backend
    if is_process_local(backend) and not is_production_env():
        logging.getLogger("hedron.jobs").warning(
            "InMemoryJobBackend does not span processes; use Redis/Celery/RQ "
            "(set_job_backend) for multi-worker deployments. Refused automatically "
            "under HEDRON_ENV=production."
        )
    if is_production_env():
        from hedron_core.production_gate import assert_durable_backends

        assert_durable_backends(production=True)


def reset_jobs_for_tests() -> None:
    global _backend
    _backend = InMemoryJobBackend()
