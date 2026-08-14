"""Celery/RQ idempotent submit: skip live re-enqueue (#157); reclaim enqueue fails (#199)."""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock

import pytest

from hedron_core.jobs import JobState
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


class _FakePipeline:
    def __init__(self, client: _FakeRedis) -> None:
        self._client = client
        self._watched: dict[str, str | None] = {}
        self._buffer: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    def watch(self, key: str) -> None:
        self._watched[key] = self._client._data.get(key)

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
            current = self._client._data.get(watched_key)
            if current != watched_value:
                self.unwatch()
                raise WatchError("watched key changed")
        results: list[object] = []
        for op, args, kwargs in self._buffer:
            if op == "set":
                results.append(self._client.set(args[0], args[1], **kwargs))  # type: ignore[arg-type]
        self.unwatch()
        return results


class _FakeRedis:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, name: str) -> str | None:
        return self._data.get(name)

    def set(
        self,
        name: str,
        value: str,
        ex: int | None = None,
        nx: bool = False,
    ) -> bool:
        del ex
        if nx and name in self._data:
            return False
        self._data[name] = value
        return True

    def delete(self, *names: str) -> int:
        removed = 0
        for name in names:
            if name in self._data:
                del self._data[name]
                removed += 1
        return removed

    def keys(self, pattern: str) -> list[str]:
        del pattern
        return list(self._data)

    def scan_iter(self, *, match: str | None = None, count: int | None = None) -> Any:
        del count
        prefix = (match or "*").rstrip("*")
        for key in list(self._data):
            if key.startswith(prefix):
                yield key

    def pipeline(self) -> _FakePipeline:
        return _FakePipeline(self)


def test_celery_idempotent_replay_skips_broker_and_does_not_mark_failed() -> None:
    celery = MagicMock()
    celery.send_task.side_effect = [None, RuntimeError("dup")]
    backend = CeleryJobBackend(celery, redis_client=_FakeRedis())  # type: ignore[arg-type]

    first = backend.submit("t", {"a": 1}, idempotency_key="k", auth_subject="u")
    second = backend.submit("t", {"a": 1}, idempotency_key="k", auth_subject="u")

    assert first.job_id == second.job_id
    assert celery.send_task.call_count == 1
    status = backend.get(first.job_id, auth_subject="u")
    assert status is not None
    assert status.state is JobState.QUEUED


def test_rq_idempotent_replay_skips_enqueue_and_does_not_mark_failed() -> None:
    def _task(payload: dict[str, object]) -> None:
        del payload

    queue = MagicMock()
    queue.enqueue.side_effect = [MagicMock(), RuntimeError("dup")]
    backend = RQJobBackend(
        queue,
        redis_client=_FakeRedis(),  # type: ignore[arg-type]
        task_registry={"t": _task},
    )

    first = backend.submit("t", {"a": 1}, idempotency_key="k", auth_subject="u")
    second = backend.submit("t", {"a": 1}, idempotency_key="k", auth_subject="u")

    assert first.job_id == second.job_id
    assert queue.enqueue.call_count == 1
    status = backend.get(first.job_id, auth_subject="u")
    assert status is not None
    assert status.state is JobState.QUEUED


def test_celery_new_submit_enqueue_failure_still_marks_failed() -> None:
    celery = MagicMock()
    celery.send_task.side_effect = RuntimeError("broker down")
    backend = CeleryJobBackend(celery, redis_client=_FakeRedis())  # type: ignore[arg-type]
    with pytest.raises(RuntimeError, match="broker"):
        backend.submit("demo", {}, idempotency_key="k", auth_subject="u")
    keys = [k for k in backend._store._client._data if ":idem:" not in k]  # type: ignore[attr-defined]
    assert len(keys) == 1
    job_id = keys[0].removeprefix("h1:job:")
    status = backend.get(job_id, auth_subject="u")
    assert status is not None
    assert status.state is JobState.FAILED
    # Idempotency pointer must be cleared so a retry can create a new job (#199).
    idem_keys = [k for k in backend._store._client._data if ":idem:" in k]  # type: ignore[attr-defined]
    assert idem_keys == []


def test_celery_idempotent_retry_after_enqueue_failure_reenqueues() -> None:
    celery = MagicMock()
    celery.send_task.side_effect = [RuntimeError("broker down"), None]
    backend = CeleryJobBackend(celery, redis_client=_FakeRedis())  # type: ignore[arg-type]

    with pytest.raises(RuntimeError, match="broker"):
        backend.submit("demo", {"x": 1}, idempotency_key="idem1", auth_subject="u")

    handle2 = backend.submit("demo", {"x": 1}, idempotency_key="idem1", auth_subject="u")
    assert celery.send_task.call_count == 2
    status = backend.get(handle2.job_id, auth_subject="u")
    assert status is not None
    assert status.state is JobState.QUEUED


def test_rq_idempotent_retry_after_enqueue_failure_reenqueues() -> None:
    def _task(payload: dict[str, object]) -> None:
        del payload

    queue = MagicMock()
    queue.enqueue.side_effect = [RuntimeError("broker down"), MagicMock()]
    backend = RQJobBackend(
        queue,
        redis_client=_FakeRedis(),  # type: ignore[arg-type]
        task_registry={"demo": _task},
    )

    with pytest.raises(RuntimeError, match="broker"):
        backend.submit("demo", {"x": 1}, idempotency_key="idem1", auth_subject="u")

    handle2 = backend.submit("demo", {"x": 1}, idempotency_key="idem1", auth_subject="u")
    assert queue.enqueue.call_count == 2
    status = backend.get(handle2.job_id, auth_subject="u")
    assert status is not None
    assert status.state is JobState.QUEUED


def test_celery_worker_failure_still_blocks_idempotent_replay() -> None:
    """Real execution failures must keep the idempotency key (#157 / opposite of #199)."""
    celery = MagicMock()
    backend = CeleryJobBackend(celery, redis_client=_FakeRedis())  # type: ignore[arg-type]
    handle = backend.submit("demo", {}, idempotency_key="k", auth_subject="u")
    backend.mark(handle.job_id, JobState.FAILED, error="worker boom")

    second = backend.submit("demo", {}, idempotency_key="k", auth_subject="u")
    assert second.job_id == handle.job_id
    assert celery.send_task.call_count == 1


def test_submit_heals_legacy_enqueue_failed_pointer() -> None:
    """Stuck FAILED+enqueue-error pointers from before the fix are reclaimable."""
    from hedron_core.job_status_store import CELERY_ENQUEUE_FAILED

    celery = MagicMock()
    redis = _FakeRedis()
    backend = CeleryJobBackend(celery, redis_client=redis)  # type: ignore[arg-type]
    handle = backend.submit("demo", {}, idempotency_key="stuck", auth_subject="u")
    # Simulate the pre-fix path: FAILED enqueue error while pointer remains.
    backend._store.mark(handle.job_id, JobState.FAILED, error=CELERY_ENQUEUE_FAILED)
    assert any(":idem:" in k for k in redis._data)

    handle2 = backend.submit("demo", {}, idempotency_key="stuck", auth_subject="u")
    assert handle2.job_id != handle.job_id
    assert celery.send_task.call_count == 2
    status = backend.get(handle2.job_id, auth_subject="u")
    assert status is not None
    assert status.state is JobState.QUEUED
