"""Process-wide cache backend installation."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar

from hedron_core.cache.backend import CacheBackend
from hedron_core.cache.memory import InMemoryCacheBackend
from hedron_core.cache.tracing import clear_cache_traces, record_cache_trace
from hedron_core.cache.types import CacheEvent
from hedron_core.durability import is_process_local

_backend: CacheBackend = InMemoryCacheBackend()
_scoped_backend: ContextVar[CacheBackend | None] = ContextVar("hedron_cache_backend", default=None)


def get_cache_backend() -> CacheBackend:
    return _scoped_backend.get() or _backend


@contextmanager
def use_cache_backend(backend: CacheBackend) -> Generator[None, None, None]:
    """Temporarily bind a cache backend to the current application context."""
    token = _scoped_backend.set(backend)
    try:
        yield
    finally:
        _scoped_backend.reset(token)


def set_cache_backend(backend: CacheBackend) -> None:
    global _backend
    from hedron_core.compile_gate import is_production_env

    if is_production_env() and is_process_local(backend):
        from hedron_core.audit import SecurityAuditEventType, emit_security_audit

        emit_security_audit(
            SecurityAuditEventType.PRODUCTION_GATE_FAILED,
            "InMemoryCacheBackend refused in production",
            attributes={"backend": type(backend).__name__, "via": "set_cache_backend"},
        )
        raise RuntimeError(
            "InMemoryCacheBackend is not allowed under HEDRON_ENV=production. "
            "Call set_cache_backend(...) with an external store, or unset production "
            "for local demos."
        )
    scoped = _scoped_backend.get()
    if scoped is not None:
        _scoped_backend.set(backend)
    else:
        _backend = backend
    if is_production_env():
        from hedron_core.production_gate import assert_durable_backends

        assert_durable_backends(production=True)


def invalidate_tags(*tags: str) -> int:
    count = get_cache_backend().invalidate(tags=tags)
    record_cache_trace(
        CacheEvent(
            kind="invalidate",
            key_fingerprint="*",
            scope="*",
            tags=tags,
            detail=f"removed={count}",
        )
    )
    return count


def reset_cache_for_tests() -> None:
    global _backend
    _backend = InMemoryCacheBackend()
    clear_cache_traces()
