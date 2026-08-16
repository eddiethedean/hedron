"""Update phase 0.11 Celery/RQ tests for Redis-required durability (0.13)."""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any

from hedron_core.jobs import JobBackend, JobState
from hedron_core.jobs_celery import CeleryJobBackend
from hedron_core.jobs_rq import RQJobBackend


class WatchError(Exception):
    """Stub WatchError so RedisStatusStore CAS works without redis-py."""


_redis_mod = ModuleType("redis")
_exc_mod = ModuleType("redis.exceptions")
_exc_mod.WatchError = WatchError  # type: ignore[attr-defined]
_redis_mod.exceptions = _exc_mod  # type: ignore[attr-defined]
sys.modules.setdefault("redis", _redis_mod)
sys.modules.setdefault("redis.exceptions", _exc_mod)


class _SharedPipeline:
    def __init__(self, client: _SharedRedis) -> None:
        self._client = client
        self._watched: dict[str, str | None] = {}
        self._buffer: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    def watch(self, key: str) -> None:
        self._watched[key] = self._client._store.get(key)

    def unwatch(self) -> None:
        self._watched.clear()
        self._buffer.clear()

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def multi(self) -> None:
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
        for watched_key, watched_value in self._watched.items():
            current = self._client._store.get(watched_key)
            if current != watched_value:
                self.unwatch()
                raise WatchError("watched key changed")
        results: list[object] = []
        for op, args, kwargs in self._buffer:
            if op == "set":
                results.append(self._client.set(args[0], args[1], **kwargs))  # type: ignore[arg-type]
        self.unwatch()
        return results


class _SharedRedis:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

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

    def eval(self, script: str, numkeys: int, *args: object) -> int:
        del script
        if numkeys != 1 or len(args) != 2:
            raise NotImplementedError("stub eval supports one-key compare-and-delete only")
        key = str(args[0])
        expected = str(args[1])
        if self._store.get(key) == expected:
            self._store.pop(key, None)
            return 1
        return 0

    def keys(self, pattern: str) -> list[str]:
        prefix = pattern.rstrip("*")
        return [k for k in self._store if k.startswith(prefix)]

    def pipeline(self) -> _SharedPipeline:
        return _SharedPipeline(self)


class _FakeCelery:
    def send_task(self, *args: Any, **kwargs: Any) -> None:
        return None

    class control:
        @staticmethod
        def revoke(*args: Any, **kwargs: Any) -> None:
            return None


class _FakeQueue:
    def __init__(self) -> None:
        self.enqueued: list[tuple[Any, ...]] = []

    def enqueue(self, *args: Any, **kwargs: Any) -> Any:
        self.enqueued.append(args)
        return type("Job", (), {"cancel": lambda self: None})()


def _redis() -> Any:
    return _SharedRedis()


def test_celery_backend_is_job_backend() -> None:
    backend = CeleryJobBackend(_FakeCelery(), redis_client=_redis())
    assert isinstance(backend, JobBackend)


def test_rq_backend_is_job_backend() -> None:
    backend = RQJobBackend(_FakeQueue(), redis_client=_redis())
    assert isinstance(backend, JobBackend)


def test_celery_backend_submit_get_cancel_mark_cleanup() -> None:
    backend = CeleryJobBackend(_FakeCelery(), redis_client=_redis())
    handle = backend.submit("demo.task", {"n": 1}, auth_subject="u1", tenant_id="t1")
    status = backend.get(handle.job_id, auth_subject="u1", tenant_id="t1")
    assert status is not None
    assert status.state is JobState.QUEUED
    assert backend.get(handle.job_id, auth_subject="other") is None
    assert backend.request_cancel(handle.job_id, auth_subject="u1", tenant_id="t1") is True
    marked = backend.mark(handle.job_id, JobState.CANCELLED)
    assert marked is not None and marked.state is JobState.CANCELLED
    assert backend.cleanup_expired(older_than_seconds=0) >= 1


def test_celery_idempotency_key() -> None:
    backend = CeleryJobBackend(_FakeCelery(), redis_client=_redis())
    first = backend.submit(
        "demo.task",
        {"n": 1},
        idempotency_key="k1",
        auth_subject="u1",
        tenant_id="t1",
    )
    second = backend.submit(
        "demo.task",
        {"n": 2},
        idempotency_key="k1",
        auth_subject="u1",
        tenant_id="t1",
    )
    assert first.job_id == second.job_id


def test_rq_backend_submit_get_cancel_with_registry() -> None:
    def demo_task(payload: dict[str, Any]) -> None:
        del payload

    queue = _FakeQueue()
    backend = RQJobBackend(queue, redis_client=_redis(), task_registry={"demo.task": demo_task})
    handle = backend.submit("demo.task", {"n": 1}, auth_subject="u1")
    assert queue.enqueued
    assert backend.get(handle.job_id, auth_subject="u1") is not None
