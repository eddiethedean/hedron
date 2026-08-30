"""Cache backend protocol."""

from __future__ import annotations

import math
from typing import Any, Protocol, runtime_checkable

# Redis PX uses a signed 64-bit millisecond duration. Leave one second of
# floating-point headroom so every accepted value converts safely in all backends.
_MAX_CACHE_TTL_SECONDS = ((2**63 - 1) // 1_000) - 1


def validate_cache_ttl(ttl: object) -> float | None:
    """Return a normalized finite cache TTL while preserving expiry semantics."""
    if ttl is None:
        return None
    if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
        raise ValueError("cache ttl must be None or a finite number")
    try:
        normalized = float(ttl)
    except OverflowError as exc:
        raise ValueError(
            "cache ttl must be None or a finite number in the supported range"
        ) from exc
    if not math.isfinite(normalized) or normalized > _MAX_CACHE_TTL_SECONDS:
        raise ValueError("cache ttl must be None or a finite number in the supported range")
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
