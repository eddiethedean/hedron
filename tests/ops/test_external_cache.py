"""External cache conformance (in-process stub / fakeredis).

Protocol-only: proves RedisCacheBackend call shapes against a stub client.
Not a multi-process or real-Redis durability proof — keep real Redis behind an
explicit opt-in marker/job.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from hedron_core.redis_cache import RedisCacheBackend


class _StubPipeline:
    def __init__(self, client: _StubRedis) -> None:
        self._client = client
        self._ops: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def set(
        self, key: str, value: str, ex: int | None = None, px: int | None = None
    ) -> _StubPipeline:
        self._ops.append(("set", (key, value), {"ex": ex, "px": px}))
        return self

    def sadd(self, key: str, member: str) -> _StubPipeline:
        self._ops.append(("sadd", (key, member), {}))
        return self

    def srem(self, key: str, member: str) -> _StubPipeline:
        self._ops.append(("srem", (key, member), {}))
        return self

    def delete(self, key: str) -> _StubPipeline:
        self._ops.append(("delete", (key,), {}))
        return self

    def pexpire(self, key: str, milliseconds: int) -> _StubPipeline:
        self._ops.append(("pexpire", (key, milliseconds), {}))
        return self

    def expire(self, key: str, seconds: int) -> _StubPipeline:
        self._ops.append(("expire", (key, seconds), {}))
        return self

    def execute(self) -> list[Any]:
        results: list[Any] = []
        for name, args, kwargs in self._ops:
            results.append(getattr(self._client, name)(*args, **kwargs))
        self._ops.clear()
        return results


class _StubRedis:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._sets: dict[str, set[str]] = {}
        self._ttls_ms: dict[str, int] = {}

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def set(
        self,
        key: str,
        value: str,
        ex: int | None = None,
        px: int | None = None,
    ) -> bool:
        self._store[key] = value
        if px is not None:
            self._ttls_ms[key] = int(px)
        elif ex is not None:
            self._ttls_ms[key] = int(ex) * 1000
        else:
            self._ttls_ms.pop(key, None)
        return True

    def delete(self, key: str) -> int:
        self._sets.pop(key, None)
        self._ttls_ms.pop(key, None)
        return 1 if self._store.pop(key, None) is not None else 0

    def sadd(self, key: str, member: str) -> int:
        self._sets.setdefault(key, set()).add(member)
        return 1

    def srem(self, key: str, member: str) -> int:
        bucket = self._sets.get(key)
        if not bucket or member not in bucket:
            return 0
        bucket.discard(member)
        if not bucket:
            del self._sets[key]
        return 1

    def smembers(self, key: str) -> set[str]:
        return set(self._sets.get(key, set()))

    def ttl(self, key: str) -> int:
        ms = self._ttls_ms.get(key)
        if ms is None:
            return -2 if key not in self._sets and key not in self._store else -1
        return max(1, ms // 1000)

    def pttl(self, key: str) -> int:
        ms = self._ttls_ms.get(key)
        if ms is None:
            return -2 if key not in self._sets and key not in self._store else -1
        return ms

    def expire(self, key: str, seconds: int) -> bool:
        self._ttls_ms[key] = max(1, int(seconds) * 1000)
        return True

    def pexpire(self, key: str, milliseconds: int) -> bool:
        self._ttls_ms[key] = max(1, int(milliseconds))
        return True

    def pipeline(self, transaction: bool = True) -> _StubPipeline:
        del transaction
        return _StubPipeline(self)

    def ping(self) -> bool:
        return True


def _client() -> Any:
    try:
        import fakeredis

        return fakeredis.FakeRedis(decode_responses=True)
    except ImportError:
        return _StubRedis()


def test_redis_cache_roundtrip() -> None:
    backend = RedisCacheBackend(_client())
    backend.set("a", {"n": 1}, ttl=30)
    assert backend.get("a") == {"n": 1}
    assert backend.invalidate(keys=("a",)) == 1
    assert backend.get("a") is None


def test_redis_cache_tag_invalidation() -> None:
    backend = RedisCacheBackend(_StubRedis())
    backend.set("a", {"n": 1}, tags=("t1",))
    backend.set("b", {"n": 2}, tags=("t1",))
    assert backend.invalidate(tags=("t1",)) == 2
    assert backend.get("a") is None
    assert backend.get("b") is None


def test_redis_cache_tag_index_does_not_expire_immortal_members() -> None:
    """#285: PTTL -1 must not be treated as shorter than a later member TTL."""
    client = _StubRedis()
    backend = RedisCacheBackend(client)
    backend.set("perm", {"v": 1}, ttl=None, tags=("t",))
    tag_key = f"{backend._prefix}t:t"
    assert client.pttl(tag_key) == -1
    backend.set("temp", {"v": 2}, ttl=2, tags=("t",))
    assert client.pttl(tag_key) == -1
    assert backend.invalidate(tags=("t",)) == 2
    hit, _value = backend.lookup("perm")
    assert hit is False


def test_redis_cache_overwrite_drops_stale_tag_membership() -> None:
    """#253: invalidating an old tag must not delete a live value tagged only with the new tag."""
    client = _StubRedis()
    backend = RedisCacheBackend(client)
    backend.set("k", {"v": 1}, tags=("a",))
    backend.set("k", {"v": 2}, tags=("b",))
    assert "k" not in client._sets.get(f"{backend._prefix}t:a", set())
    assert "k" in client._sets[f"{backend._prefix}t:b"]
    assert backend.invalidate(tags=("a",)) == 0
    assert backend.lookup("k") == (True, {"v": 2})
    assert backend.invalidate(tags=("b",)) == 1
    assert backend.lookup("k") == (False, None)


def test_redis_cache_ttl_zero_cleans_tag_membership() -> None:
    """#253: ttl<=0 must SREM the key from tag indexes, not only DELETE the value."""
    client = _StubRedis()
    backend = RedisCacheBackend(client)
    backend.set("k", {"v": 1}, tags=("a",))
    backend.set("k", {"v": 1}, tags=("a",), ttl=0)
    assert backend.lookup("k") == (False, None)
    assert "k" not in client._sets.get(f"{backend._prefix}t:a", set())
    backend.set("k", {"v": 2}, tags=("b",))
    assert backend.invalidate(tags=("a",)) == 0
    assert backend.lookup("k") == (True, {"v": 2})


def test_redis_cache_rejects_bad_json() -> None:
    client = _StubRedis()
    backend = RedisCacheBackend(client)
    with pytest.raises(ValueError):
        backend.set("x", object())  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_redis_cache_rejects_non_finite_json_without_writes(value: float) -> None:
    client = _StubRedis()
    backend = RedisCacheBackend(client)
    with pytest.raises(ValueError, match="not JSON-serializable"):
        backend.set("x", {"nested": [value]}, tags=("t",))
    assert client._store == {}
    assert client._sets == {}


def test_redis_cache_rejects_poisoned_non_standard_json() -> None:
    client = _StubRedis()
    backend = RedisCacheBackend(client)
    client._store["h1:c:v:x"] = '{"value":NaN}'
    with pytest.raises(ValueError, match="Corrupt cache value"):
        backend.lookup("x")


@pytest.mark.parametrize("ttl", [math.nan, math.inf, -math.inf])
def test_redis_cache_rejects_non_finite_ttl_without_writes(ttl: float) -> None:
    client = _StubRedis()
    backend = RedisCacheBackend(client)
    with pytest.raises(ValueError, match="finite number"):
        backend.set("x", {"value": 1}, ttl=ttl, tags=("t",))
    assert client._store == {}
    assert client._sets == {}


def test_redis_cache_does_not_share_job_keyspace() -> None:
    """#252: cache lookup/invalidate of job:{id} must not hit or delete job records."""
    from hedron_core.job_status_store import RedisStatusStore

    client = _StubRedis()
    jobs = RedisStatusStore(client)  # type: ignore[arg-type]
    cache = RedisCacheBackend(client)
    handle, _created = jobs.submit("demo", {"secret": "payload"}, auth_subject="alice")
    job_cache_key = f"job:{handle.job_id}"
    hit, value = cache.lookup(job_cache_key)
    assert hit is False
    assert value is None
    assert cache.invalidate(keys=(job_cache_key,)) == 0
    status = jobs.get(handle.job_id)
    assert status is not None
    assert status.auth_subject == "alice"
    assert "secret" in str(client._store[f"h1:job:{handle.job_id}"])
    cache.set(job_cache_key, {"v": 1})
    assert cache.lookup(job_cache_key) == (True, {"v": 1})
    assert jobs.get(handle.job_id) is not None
    assert cache.invalidate(keys=(job_cache_key,)) == 1
    assert jobs.get(handle.job_id) is not None


def test_redis_cache_rejects_prefix_that_nests_jobs() -> None:
    """#252: legacy ``h1:`` cache prefix nests ``h1:job:`` records."""
    with pytest.raises(ValueError, match="overlap"):
        RedisCacheBackend(_StubRedis(), prefix="h1:")
    with pytest.raises(ValueError, match="overlap"):
        RedisCacheBackend(_StubRedis(), prefix="h1:job:")
