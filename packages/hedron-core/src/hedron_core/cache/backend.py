"""Cache backend protocol."""

from __future__ import annotations

import math
from typing import Any, Protocol, runtime_checkable


def validate_cache_ttl(ttl: object) -> float | None:
    """Return a normalized finite cache TTL while preserving expiry semantics."""
    if ttl is None:
        return None
    if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
        raise ValueError("cache ttl must be None or a finite number")
    normalized = float(ttl)
    if not math.isfinite(normalized):
        raise ValueError("cache ttl must be None or a finite number")
    return normalized


@runtime_checkable
class CacheBackend(Protocol):
    """Key/value cache used by ``cache_data`` / ``cache_component``.

    Implementations may set ``process_local = True`` when they cannot span
    processes. Production gates treat a missing attribute as durable.

    ``lookup`` must distinguish a stored ``None`` from a miss.
    """

    def get(self, key: str) -> Any | None:
        """Return the cached value, or ``None`` on miss."""
        ...

    def lookup(self, key: str) -> tuple[bool, Any]:
        """Return ``(hit, value)`` so stored ``None`` is distinguishable from a miss."""
        ...

    def set(
        self,
        key: str,
        value: Any,
        *,
        ttl: float | None = None,
        tags: tuple[str, ...] = (),
    ) -> None:
        """Store ``value`` under ``key`` with optional TTL and invalidation tags."""
        ...

    def invalidate(self, *, tags: tuple[str, ...] = (), keys: tuple[str, ...] = ()) -> int:
        """Remove matching entries and return how many were dropped."""
        ...
