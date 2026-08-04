"""Redis job backend multi-worker durability."""

from __future__ import annotations

from typing import Any

from hedron_core.jobs import JobState, RedisJobBackend


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


def test_redis_jobs_shared_across_workers() -> None:
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
