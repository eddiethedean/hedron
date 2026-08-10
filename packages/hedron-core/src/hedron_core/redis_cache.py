"""Redis CacheBackend conformance implementation (phase 0.7B)."""

from __future__ import annotations

import json
from typing import Any

from hedron_core.cache import CacheBackend

__all__ = ["RedisCacheBackend"]


class RedisCacheBackend(CacheBackend):
    """JSON-valued Redis cache with ``h1:`` key prefix and tag index sets.

    Serialization failures raise — values are never stored poisoned.
    """

    def __init__(self, client: Any, *, prefix: str = "h1:") -> None:
        self._client = client
        self._prefix = prefix

    def _key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    def _tag_key(self, tag: str) -> str:
        return f"{self._prefix}tag:{tag}"

    def _decode(self, raw: Any) -> str | None:
        if raw is None:
            return None
        if isinstance(raw, bytes):
            return raw.decode("utf-8")
        return str(raw)

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
        try:
            payload = json.dumps(value, separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            raise ValueError("Cache value is not JSON-serializable") from exc
        redis_key = self._key(key)
        if ttl is None:
            self._client.set(redis_key, payload)
        else:
            self._client.set(redis_key, payload, ex=max(1, int(ttl)))
        for tag in tags:
            self._client.sadd(self._tag_key(tag), key)

    def invalidate(self, *, tags: tuple[str, ...] = (), keys: tuple[str, ...] = ()) -> int:
        removed = 0
        to_delete: set[str] = set(keys)
        for tag in tags:
            members = self._client.smembers(self._tag_key(tag)) or set()
            for member in members:
                decoded = self._decode(member)
                if decoded is not None:
                    to_delete.add(decoded)
            self._client.delete(self._tag_key(tag))
        for key in to_delete:
            if self._client.delete(self._key(key)):
                removed += 1
        return removed

    def ping(self) -> bool:
        try:
            return bool(self._client.ping())
        except Exception:
            return False

    def age_ms(self, key: str) -> float | None:
        del key
        return None
