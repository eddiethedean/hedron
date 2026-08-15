"""In-process cache activity traces for Explorer."""

from __future__ import annotations

from hedron_core.cache.types import CacheEvent
from hedron_core.typing_aliases import CacheTraceDict

_traces: list[CacheEvent] = []
_TRACE_LIMIT = 200


def record_cache_trace(event: CacheEvent) -> None:
    _traces.append(event)
    if len(_traces) > _TRACE_LIMIT:
        del _traces[: len(_traces) - _TRACE_LIMIT]


def get_cache_traces() -> tuple[CacheEvent, ...]:
    return tuple(_traces)


def clear_cache_traces() -> None:
    _traces.clear()


class CacheTrace:
    """Explorer-facing snapshot of recent cache activity."""

    @staticmethod
    def recent(limit: int = 50) -> list[CacheTraceDict]:
        events = list(_traces)[-limit:]
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
