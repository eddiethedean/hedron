"""External cache conformance (in-process stub / fakeredis).

Protocol-only: proves RedisCacheBackend call shapes against a stub client.
Not a multi-process or real-Redis durability proof — keep real Redis behind an
explicit opt-in marker/job.
"""

from __future__ import annotations

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


def test_redis_cache_rejects_bad_json() -> None:
    client = _StubRedis()
    backend = RedisCacheBackend(client)
    with pytest.raises(ValueError):
        backend.set("x", object())  # type: ignore[arg-type]
