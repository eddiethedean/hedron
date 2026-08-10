"""Redis job backend shared-client protocol (in-process stub).

Not a multi-process / real-Redis worker proof — see opt-in redis markers for that.
"""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any

from hedron_core.jobs import JobState, RedisJobBackend


class WatchError(Exception):
    """Stub WatchError so RedisJobBackend CAS works without redis-py installed."""


_redis_mod = ModuleType("redis")
_exc_mod = ModuleType("redis.exceptions")
_exc_mod.WatchError = WatchError  # type: ignore[attr-defined]
_redis_mod.exceptions = _exc_mod  # type: ignore[attr-defined]
sys.modules.setdefault("redis", _redis_mod)
sys.modules.setdefault("redis.exceptions", _exc_mod)


class _SharedRedis:
    """Minimal shared Redis stub used by two backend instances."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._sets: dict[str, set[str]] = {}

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def set(
        self,
        key: str,
        value: str,
        ex: int | None = None,
        nx: bool = False,
    ) -> bool:
        del ex
        if nx and key in self._store:
            return False
        self._store[key] = value
        return True

    def delete(self, key: str) -> int:
        return 1 if self._store.pop(key, None) is not None else 0

    def keys(self, pattern: str) -> list[str]:
        prefix = pattern.rstrip("*")
        return [k for k in self._store if k.startswith(prefix)]

    def sadd(self, key: str, member: str) -> int:
        self._sets.setdefault(key, set()).add(member)
        return 1

    def smembers(self, key: str) -> set[str]:
        return set(self._sets.get(key, set()))

    def pipeline(self) -> _SharedPipeline:
        return _SharedPipeline(self)


class _SharedPipeline:
    """Minimal WATCH/MULTI/EXEC stub for RedisJobBackend CAS tests."""

    def __init__(self, client: _SharedRedis) -> None:
        self._client = client
        self._watched: str | None = None
        self._buffer: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
        self._in_multi = False

    def watch(self, key: str) -> None:
        self._watched = key

    def unwatch(self) -> None:
        self._watched = None
        self._buffer.clear()
        self._in_multi = False

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def multi(self) -> None:
        self._in_multi = True
        self._buffer.clear()

    def set(
        self,
        key: str,
        value: str,
        ex: int | None = None,
        nx: bool = False,
    ) -> None:
        self._buffer.append(("set", (key, value), {"ex": ex, "nx": nx}))

    def execute(self) -> list[object]:
        results: list[object] = []
        for op, args, kwargs in self._buffer:
            if op == "set":
                results.append(self._client.set(args[0], args[1], **kwargs))  # type: ignore[arg-type]
        self.unwatch()
        return results


def test_redis_job_backend_shares_state_via_client_protocol() -> None:
    """Stub client only — not a multi-process worker proof."""
    shared: Any = _SharedRedis()
    a = RedisJobBackend(shared)
    b = RedisJobBackend(shared)
    handle = a.submit("demo", {"n": 1}, idempotency_key="k1", tenant_id="t")
    again = b.submit("demo", {"n": 2}, idempotency_key="k1", tenant_id="t")
    assert handle.job_id == again.job_id
    assert b.get(handle.job_id) is not None
    assert b.request_cancel(handle.job_id, tenant_id="t") is True
    st = a.get(handle.job_id)
    assert st is not None and st.cancel_requested is True
    marked = b.mark(handle.job_id, JobState.CANCELLED)
    assert marked is not None
    assert a.get(handle.job_id) is not None
