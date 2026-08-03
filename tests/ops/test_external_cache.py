"""External cache conformance (fakeredis or stub)."""

from __future__ import annotations

from typing import Any

import pytest

from hedron_core.redis_cache import RedisCacheBackend


class _StubRedis:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def set(self, key: str, value: str, ex: int | None = None) -> bool:
        del ex
        self._store[key] = value
        return True

    def delete(self, key: str) -> int:
        return 1 if self._store.pop(key, None) is not None else 0

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


def test_redis_cache_rejects_bad_json() -> None:
    client = _StubRedis()
    backend = RedisCacheBackend(client)
    with pytest.raises(ValueError):
        backend.set("x", object())  # type: ignore[arg-type]
