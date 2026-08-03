"""Redis CacheBackend conformance implementation (phase 0.7B)."""

from __future__ import annotations

import json
from typing import Any

from hedron_core.cache import CacheBackend

__all__ = ["RedisCacheBackend"]


class RedisCacheBackend(CacheBackend):
    """JSON-valued Redis cache with ``h1:`` key prefix.

    Serialization failures raise — values are never stored poisoned.
    """

    def __init__(self, client: Any, *, prefix: str = "h1:") -> None:
        self._client = client
        self._prefix = prefix

    def _key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    def get(self, key: str) -> Any | None:
        raw = self._client.get(self._key(key))
        if raw is None:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Corrupt cache value for {key}") from exc

    def set(
        self,
        key: str,
        value: Any,
        *,
        ttl: float | None = None,
        tags: tuple[str, ...] = (),
    ) -> None:
        del tags  # tag index optional; conformance uses key invalidation
        try:
            payload = json.dumps(value, separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            raise ValueError("Cache value is not JSON-serializable") from exc
        if ttl is None:
            self._client.set(self._key(key), payload)
        else:
            self._client.set(self._key(key), payload, ex=max(1, int(ttl)))

    def invalidate(self, *, tags: tuple[str, ...] = (), keys: tuple[str, ...] = ()) -> int:
        del tags
        removed = 0
        for key in keys:
            if self._client.delete(self._key(key)):
                removed += 1
        return removed

    def ping(self) -> bool:
        try:
            return bool(self._client.ping())
        except Exception:  # noqa: BLE001
            return False

    def age_ms(self, key: str) -> float | None:
        del key
        return None
