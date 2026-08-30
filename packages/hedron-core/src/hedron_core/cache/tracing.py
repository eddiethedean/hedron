"""Bounded, application-scoped cache activity traces for Explorer."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field

from hedron_core.cache.types import CacheEvent
from hedron_core.typing_aliases import CacheTraceDict

_TRACE_LIMIT = 200


@dataclass(slots=True)
class CacheTraceState:
    """Bounded cache telemetry owned by one application runtime."""

    events: list[CacheEvent] = field(default_factory=list[CacheEvent])


_default_state = CacheTraceState()
_scoped_state: ContextVar[CacheTraceState | None] = ContextVar(
    "hedron_cache_trace_state", default=None
)


def new_cache_trace_state() -> CacheTraceState:
    """Create an isolated, bounded trace store for an application."""
    return CacheTraceState()


def _active_state() -> CacheTraceState:
    return _scoped_state.get() or _default_state


@contextmanager
def use_cache_trace_state(state: CacheTraceState) -> Generator[None, None, None]:
    """Bind cache telemetry to the current application/task context."""
    token = _scoped_state.set(state)
    try:
        yield
    finally:
        _scoped_state.reset(token)


def record_cache_trace(event: CacheEvent) -> None:
    traces = _active_state().events
    traces.append(event)
    if len(traces) > _TRACE_LIMIT:
        del traces[: len(traces) - _TRACE_LIMIT]


def get_cache_traces() -> tuple[CacheEvent, ...]:
    return tuple(_active_state().events)


def clear_cache_traces() -> None:
    _active_state().events.clear()


class CacheTrace:
    """Explorer-facing snapshot of recent cache activity."""

    @staticmethod
    def recent(limit: int = 50) -> list[CacheTraceDict]:
        events = list(get_cache_traces())[-limit:]
        return [
            {
                "kind": e.kind,
                "key_fingerprint": e.key_fingerprint,
                "scope": e.scope,
                "age_ms": e.age_ms,
                "size": e.size,
                "tags": list(e.tags),
                "detail": e.detail,
            }
            for e in events
        ]
