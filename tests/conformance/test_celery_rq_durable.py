"""Celery/RQ Redis-durable status via shared client stubs (JOB-013-*).

These tests use an in-process fake Redis client — not multi-process workers.
"""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any

import pytest

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
    def enqueue(self, *args: Any, **kwargs: Any) -> Any:
        return type("Job", (), {"cancel": lambda self: None})()


def test_celery_requires_redis() -> None:
    with pytest.raises(RuntimeError, match="Redis"):
        CeleryJobBackend(_FakeCelery())


def test_celery_status_shared_via_client_protocol() -> None:
    """Stub client only — not a multi-process worker proof."""
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


def test_celery_idempotency_shared_via_client_protocol() -> None:
    """Stub client only — not a multi-process worker proof."""
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


def test_rq_status_shared_via_client_protocol() -> None:
    """Stub client only — not a multi-process worker proof."""
    shared: Any = _SharedRedis()

    def _demo(payload: dict[str, object]) -> None:
        del payload

    registry = {"demo.task": _demo}
    a = RQJobBackend(_FakeQueue(), redis_client=shared, task_registry=registry)
    b = RQJobBackend(_FakeQueue(), redis_client=shared, task_registry=registry)
    handle = a.submit("demo.task", {"n": 1}, auth_subject="u1")
    status = b.get(handle.job_id, auth_subject="u1")
    assert status is not None
    assert status.state is JobState.QUEUED


def test_rq_cancel_shared_via_client_protocol() -> None:
    """Stub client only — not a multi-process worker proof."""
    shared: Any = _SharedRedis()

    def _demo(payload: dict[str, object]) -> None:
        del payload

    registry = {"demo.task": _demo}
    a = RQJobBackend(_FakeQueue(), redis_client=shared, task_registry=registry)
    b = RQJobBackend(_FakeQueue(), redis_client=shared, task_registry=registry)
    handle = a.submit("demo.task", {"n": 1}, auth_subject="u1")
    assert b.request_cancel(handle.job_id, auth_subject="u1") is True
    status = a.get(handle.job_id, auth_subject="u1")
    assert status is not None
    assert status.cancel_requested is True
    # Shared-store mark SUCCEEDED while cancel sticky → CANCELLED
    marked = a.mark(handle.job_id, JobState.SUCCEEDED)
    assert marked is not None
    assert marked.state is JobState.CANCELLED


def test_rq_idempotency_shared_via_client_protocol() -> None:
    """Stub client only — not a multi-process worker proof."""
    shared: Any = _SharedRedis()

    def _demo(payload: dict[str, object]) -> None:
        del payload

    registry = {"demo.task": _demo}
    a = RQJobBackend(_FakeQueue(), redis_client=shared, task_registry=registry)
    b = RQJobBackend(_FakeQueue(), redis_client=shared, task_registry=registry)
    first = a.submit(
        "demo.task",
        {"n": 1},
        idempotency_key="rq-k1",
        auth_subject="u1",
        tenant_id="t1",
    )
    second = b.submit(
        "demo.task",
        {"n": 2},
        idempotency_key="rq-k1",
        auth_subject="u1",
        tenant_id="t1",
    )
    assert first.job_id == second.job_id


def test_celery_revoke_failure_restores_status() -> None:
    shared: Any = _SharedRedis()

    class _FailRevoke:
        def send_task(self, *args: Any, **kwargs: Any) -> None:
            return None

        class control:
            @staticmethod
            def revoke(*args: Any, **kwargs: Any) -> None:
                raise RuntimeError("broker down")

    backend = CeleryJobBackend(_FailRevoke(), redis_client=shared)
    handle = backend.submit("demo.task", {"n": 1}, auth_subject="u1")
    assert backend.request_cancel(handle.job_id, auth_subject="u1") is False
    status = backend.get(handle.job_id, auth_subject="u1")
    assert status is not None
    assert status.state is JobState.QUEUED
    assert status.cancel_requested is False


def test_rq_unknown_job_type_raises() -> None:
    shared: Any = _SharedRedis()
    backend = RQJobBackend(_FakeQueue(), redis_client=shared, task_registry={})
    with pytest.raises(KeyError, match="Unknown RQ"):
        backend.submit("demo.task", {"n": 1})


def test_rq_requires_redis() -> None:
    with pytest.raises(RuntimeError, match="Redis"):
        RQJobBackend(_FakeQueue())
