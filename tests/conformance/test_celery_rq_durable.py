"""Celery/RQ Redis-durable status (JOB-013-*)."""

from __future__ import annotations

from typing import Any

import pytest

from hedron_core.jobs import JobBackend, JobState
from hedron_core.jobs_celery import CeleryJobBackend
from hedron_core.jobs_rq import RQJobBackend


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

    def keys(self, pattern: str) -> list[str]:
        prefix = pattern.rstrip("*")
        return [k for k in self._store if k.startswith(prefix)]


class _FakeCelery:
    def send_task(self, *args: Any, **kwargs: Any) -> None:
        return None

    class control:
        @staticmethod
        def revoke(*args: Any, **kwargs: Any) -> None:
            return None


class _FakeQueue:
    def enqueue(self, *args: Any, **kwargs: Any) -> Any:
        return type("Job", (), {"cancel": lambda self: None})()


def test_celery_requires_redis() -> None:
    with pytest.raises(RuntimeError, match="Redis"):
        CeleryJobBackend(_FakeCelery())


def test_celery_status_shared_across_workers() -> None:
    shared: Any = _SharedRedis()
    a = CeleryJobBackend(_FakeCelery(), redis_client=shared)
    b = CeleryJobBackend(_FakeCelery(), redis_client=shared)
    assert isinstance(a, JobBackend)
    handle = a.submit("demo.task", {"n": 1}, auth_subject="u1", tenant_id="t1")
    status = b.get(handle.job_id, auth_subject="u1", tenant_id="t1")
    assert status is not None
    assert status.state is JobState.QUEUED
    assert b.request_cancel(handle.job_id, auth_subject="u1", tenant_id="t1") is True
    marked = a.mark(handle.job_id, JobState.CANCELLED)
    assert marked is not None and marked.state is JobState.CANCELLED


def test_celery_idempotency_across_workers() -> None:
    shared: Any = _SharedRedis()
    a = CeleryJobBackend(_FakeCelery(), redis_client=shared)
    b = CeleryJobBackend(_FakeCelery(), redis_client=shared)
    first = a.submit(
        "demo.task",
        {"n": 1},
        idempotency_key="k1",
        auth_subject="u1",
        tenant_id="t1",
    )
    second = b.submit(
        "demo.task",
        {"n": 2},
        idempotency_key="k1",
        auth_subject="u1",
        tenant_id="t1",
    )
    assert first.job_id == second.job_id


def test_rq_status_shared_across_workers() -> None:
    shared: Any = _SharedRedis()
    a = RQJobBackend(_FakeQueue(), redis_client=shared, task_registry={})
    b = RQJobBackend(_FakeQueue(), redis_client=shared, task_registry={})
    handle = a.submit("demo.task", {"n": 1}, auth_subject="u1")
    status = b.get(handle.job_id, auth_subject="u1")
    assert status is not None
    assert status.state is JobState.QUEUED


def test_rq_requires_redis() -> None:
    with pytest.raises(RuntimeError, match="Redis"):
        RQJobBackend(_FakeQueue())
