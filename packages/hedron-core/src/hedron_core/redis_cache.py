"""Redis CacheBackend conformance implementation (phase 0.7B)."""

from __future__ import annotations

import json
from typing import Any

from hedron_core.cache import CacheBackend

__all__ = ["RedisCacheBackend"]


class RedisCacheBackend(CacheBackend):
    """JSON-valued Redis cache with ``h1:`` key prefix and tag index sets.

    Serialization failures raise — values are never stored poisoned.
    Value SET and tag SADDs commit together via ``MULTI``/``EXEC`` (#218).
    Positive TTLs use millisecond ``PX`` so fractional lifetimes match in-memory (#242).
    Tag index keys receive a matching ``PEXPIRE`` so they cannot outlive values (#208).
    Indexes with no TTL (PTTL -1) stay immortal so mixed non-TTL members stay
    invalidatable (#285).
    """

    process_local = False

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
        hit, value = self.lookup(key)
        return value if hit else None

    def lookup(self, key: str) -> tuple[bool, Any]:
        raw = self._client.get(self._key(key))
        if raw is None:
            return False, None
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        try:
            return True, json.loads(raw)
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
        # Match InMemoryCacheBackend: ttl<=0 means already expired / do not keep (#242).
        if ttl is not None and ttl <= 0:
            self._client.delete(redis_key)
            return

        px_ms = max(1, int(ttl * 1000)) if ttl is not None else None
        tag_keys = [self._tag_key(tag) for tag in tags]
        pipe_factory = getattr(self._client, "pipeline", None)
        if callable(pipe_factory):
            pipe: Any = pipe_factory(transaction=True)
            self._queue_set(pipe, redis_key, payload, px_ms=px_ms)
            for tag_key in tag_keys:
                current = self._tag_pttl(tag_key) if px_ms is not None else None
                pipe.sadd(tag_key, key)
                if px_ms is not None:
                    self._queue_tag_expire(pipe, tag_key, px_ms, current=current)
            pipe.execute()
            return

        # Stubs without pipeline: still write value then tags (best-effort).
        self._queue_set(self._client, redis_key, payload, px_ms=px_ms)
        for tag_key in tag_keys:
            current = self._tag_pttl(tag_key) if px_ms is not None else None
            self._client.sadd(tag_key, key)
            if px_ms is not None:
                self._queue_tag_expire(self._client, tag_key, px_ms, current=current)

    @staticmethod
    def _queue_set(target: Any, redis_key: str, payload: str, *, px_ms: int | None) -> None:
        if px_ms is None:
            target.set(redis_key, payload)
            return
        target.set(redis_key, payload, px=px_ms)

    def _tag_pttl(self, tag_key: str) -> int | None:
        pttl = getattr(self._client, "pttl", None)
        if not callable(pttl):
            return None
        try:
            raw_ttl = pttl(tag_key)
        except Exception:  # noqa: BLE001
            return None
        if isinstance(raw_ttl, (int, float, str)):
            return int(raw_ttl)
        return None

    def _queue_tag_expire(
        self,
        target: Any,
        tag_key: str,
        px_ms: int,
        *,
        current: int | None,
    ) -> None:
        """Extend tag-index TTL to at least the value TTL (never shorten).

        ``current`` is PTTL sampled before SADD: ``-2`` missing, ``-1`` no
        expire, ``>0`` remaining ms. Newly created indexes look like ``-1``
        after SADD, so the sample must precede membership (#285 vs #208).
        """
        if current is not None and (current == -1 or current >= px_ms):
            return
        pexpire = getattr(target, "pexpire", None)
        if callable(pexpire):
            pexpire(tag_key, px_ms)
            return
        expire = getattr(target, "expire", None)
        if callable(expire):
            expire(tag_key, max(1, (px_ms + 999) // 1000))

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
        except Exception:  # noqa: BLE001
            return False

    def age_ms(self, key: str) -> float | None:
        del key
        return None
