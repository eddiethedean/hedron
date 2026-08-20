"""Redis CacheBackend conformance implementation (phase 0.7B)."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from typing import Any, Protocol, cast, runtime_checkable

from hedron_core.cache import CacheBackend

__all__ = ["RedisCacheBackend"]

_logger = logging.getLogger("hedron.core.redis_cache")

# Disjoint from RedisStatusStore / RedisJobBackend (``h1:job:``). Sharing a client
# with the legacy cache prefix ``h1:`` nests ``job:{id}`` onto live job records (#252).
REDIS_CACHE_PREFIX = "h1:c:"
REDIS_JOB_PREFIX = "h1:job:"


def _keyspace_overlaps(left: str, right: str) -> bool:
    return left.startswith(right) or right.startswith(left)


def _reject_reserved_cache_key(key: str) -> None:
    if key.startswith("tag:"):
        raise ValueError("Cache keys must not use the reserved 'tag:' prefix")


class RedisCachePipelineLike(Protocol):
    """Pipeline / MULTI batch used by ``RedisCacheBackend.set`` and membership drops."""

    def set(
        self,
        name: str,
        value: str,
        ex: int | None = None,
        px: int | None = None,
    ) -> object: ...

    def sadd(self, name: str, *values: str) -> object: ...

    def srem(self, name: str, *values: str) -> object: ...

    def delete(self, *names: str) -> object: ...

    def pexpire(self, name: str, time: int) -> object: ...

    def expire(self, name: str, time: int) -> object: ...

    def execute(self) -> object: ...


@runtime_checkable
class RedisClientLike(Protocol):
    """Redis client surface used by ``RedisCacheBackend`` (get/set/tags/TTL/pipeline)."""

    def get(self, name: str) -> bytes | str | None: ...

    def set(
        self,
        name: str,
        value: str,
        ex: int | None = None,
        px: int | None = None,
    ) -> object: ...

    def delete(self, *names: str) -> object: ...

    def ping(self) -> object: ...

    def smembers(self, name: str) -> Iterable[object]: ...

    def sadd(self, name: str, *values: str) -> object: ...

    def srem(self, name: str, *values: str) -> object: ...

    def pttl(self, name: str) -> object: ...

    def pexpire(self, name: str, time: int) -> object: ...

    def expire(self, name: str, time: int) -> object: ...

    def pipeline(self, transaction: bool = True) -> RedisCachePipelineLike: ...


class _RedisMutatorLike(Protocol):
    """Client or pipeline target for queued SET / SADD / SREM / DELETE / expire."""

    def set(
        self,
        name: str,
        value: str,
        ex: int | None = None,
        px: int | None = None,
    ) -> object: ...

    def sadd(self, name: str, *values: str) -> object: ...

    def srem(self, name: str, *values: str) -> object: ...

    def delete(self, *names: str) -> object: ...

    def pexpire(self, name: str, time: int) -> object: ...

    def expire(self, name: str, time: int) -> object: ...


class RedisCacheBackend(CacheBackend):
    """JSON-valued Redis cache with ``h1:c:`` key prefix and tag index sets.

    The default prefix is disjoint from job records (``h1:job:``). Value keys use
    ``{prefix}v:`` and tag indexes use ``{prefix}t:`` so a cache key named
    ``tag:{name}`` cannot collide with a tag set (#254). Sharing a Redis
    client with overlapping prefixes is rejected so cache lookup/invalidate cannot
    leak or delete job JSON (#252). Serialization failures raise — values are never
    stored poisoned. Value SET and tag SADDs commit together via ``MULTI``/``EXEC``
    (#218). Overwrite ``SREM``s previous tag memberships so stale indexes cannot
    delete the live value (#253). Positive TTLs use millisecond ``PX`` so fractional
    lifetimes match in-memory (#242). Tag index keys receive a matching
    ``PEXPIRE`` so they cannot outlive values (#208). Indexes with no TTL
    (PTTL -1) stay immortal so mixed non-TTL members stay invalidatable (#285).
    """

    process_local = False

    def __init__(self, client: RedisClientLike, *, prefix: str = REDIS_CACHE_PREFIX) -> None:
        if _keyspace_overlaps(prefix, REDIS_JOB_PREFIX):
            raise ValueError(
                "RedisCacheBackend prefix must not overlap the Redis job keyspace "
                f"{REDIS_JOB_PREFIX!r}; got {prefix!r}. Use a dedicated cache prefix "
                f"(default {REDIS_CACHE_PREFIX!r}) when sharing a Redis client."
            )
        self._client = client
        self._prefix = prefix

    def _key(self, key: str) -> str:
        _reject_reserved_cache_key(key)
        return f"{self._prefix}v:{key}"

    def _tag_key(self, tag: str) -> str:
        return f"{self._prefix}t:{tag}"

    def _ktags_key(self, key: str) -> str:
        return f"{self._prefix}_tags:{key}"

    def _decode(self, raw: object) -> str | None:
        if raw is None:
            return None
        if isinstance(raw, bytes):
            return raw.decode("utf-8")
        return str(raw)

    def get(self, key: str) -> Any | None:
        hit, value = self.lookup(key)
        return value if hit else None

    def lookup(self, key: str) -> tuple[bool, Any]:
        _reject_reserved_cache_key(key)
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
        value: object,
        *,
        ttl: float | None = None,
        tags: tuple[str, ...] = (),
    ) -> None:
        _reject_reserved_cache_key(key)
        try:
            payload = json.dumps(value, separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            raise ValueError("Cache value is not JSON-serializable") from exc
        redis_key = self._key(key)
        ktags_key = self._ktags_key(key)
        prior = self._prior_tags(key)
        # Match InMemoryCacheBackend: ttl<=0 means already expired / do not keep (#242).
        if ttl is not None and ttl <= 0:
            self._drop_membership(key, prior)
            return

        px_ms = max(1, int(ttl * 1000)) if ttl is not None else None
        stale = prior.difference(tags)
        pipe_factory = getattr(self._client, "pipeline", None)
        if not callable(pipe_factory):
            raise ValueError(
                "RedisCacheBackend requires a client.pipeline(transaction=True) "
                "so value SET and tag indexes commit atomically"
            )
        pipe: RedisCachePipelineLike = cast(RedisCachePipelineLike, pipe_factory(transaction=True))
        self._queue_overwrite(
            pipe, key, redis_key, ktags_key, payload, tags=tags, stale=stale, px_ms=px_ms
        )
        pipe.execute()

    def _prior_tags(self, key: str) -> set[str]:
        smembers = getattr(self._client, "smembers", None)
        if not callable(smembers):
            return set()
        raw: object = smembers(self._ktags_key(key))
        if not raw:
            return set()
        prior: set[str] = set()
        for member in cast(Iterable[object], raw):
            decoded = self._decode(member)
            if decoded is not None:
                prior.add(decoded)
        return prior

    def _queue_srem(self, target: _RedisMutatorLike, tag_key: str, member: str) -> None:
        srem = getattr(target, "srem", None)
        if callable(srem):
            srem(tag_key, member)

    def _queue_delete(self, target: _RedisMutatorLike, redis_key: str) -> None:
        delete = getattr(target, "delete", None)
        if callable(delete):
            delete(redis_key)

    def _drop_membership(self, key: str, prior: set[str]) -> None:
        redis_key = self._key(key)
        ktags_key = self._ktags_key(key)
        pipe_factory = getattr(self._client, "pipeline", None)
        if callable(pipe_factory):
            pipe: RedisCachePipelineLike = cast(
                RedisCachePipelineLike, pipe_factory(transaction=True)
            )
            self._queue_drop(pipe, key, redis_key, ktags_key, prior)
            pipe.execute()
            return
        self._queue_drop(self._client, key, redis_key, ktags_key, prior)

    def _queue_drop(
        self,
        target: _RedisMutatorLike,
        key: str,
        redis_key: str,
        ktags_key: str,
        prior: set[str],
    ) -> None:
        for tag in prior:
            self._queue_srem(target, self._tag_key(tag), key)
        self._queue_delete(target, redis_key)
        self._queue_delete(target, ktags_key)

    def _queue_overwrite(
        self,
        target: _RedisMutatorLike,
        key: str,
        redis_key: str,
        ktags_key: str,
        payload: str,
        *,
        tags: tuple[str, ...],
        stale: set[str],
        px_ms: int | None,
    ) -> None:
        for tag in stale:
            self._queue_srem(target, self._tag_key(tag), key)
        self._queue_set(target, redis_key, payload, px_ms=px_ms)
        self._queue_delete(target, ktags_key)
        for tag in tags:
            tag_key = self._tag_key(tag)
            current = self._tag_pttl(tag_key) if px_ms is not None else None
            target.sadd(tag_key, key)
            target.sadd(ktags_key, tag)
            if px_ms is not None:
                self._queue_tag_expire(target, tag_key, px_ms, current=current)
        if tags and px_ms is not None:
            self._queue_tag_expire(target, ktags_key, px_ms, current=None)

    @staticmethod
    def _queue_set(
        target: _RedisMutatorLike, redis_key: str, payload: str, *, px_ms: int | None
    ) -> None:
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
        except Exception:
            _logger.debug("Redis PTTL failed for tag key %s", tag_key, exc_info=True)
            return None
        if isinstance(raw_ttl, (int, float, str)):
            return int(raw_ttl)
        return None

    def _queue_tag_expire(
        self,
        target: _RedisMutatorLike,
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
        to_delete: set[str] = set()
        for key in keys:
            _reject_reserved_cache_key(key)
            to_delete.add(key)
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
            _logger.debug("Redis ping failed", exc_info=True)
            return False

    def age_ms(self, key: str) -> float | None:
        del key
        return None
