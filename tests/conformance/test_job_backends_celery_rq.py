"""Celery/RQ JobBackend bridge tests (phase 0.11)."""

from __future__ import annotations

from typing import Any

from hedron_core.jobs import JobState
from hedron_core.jobs_celery import CeleryJobBackend
from hedron_core.jobs_rq import RQJobBackend


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


def test_celery_backend_submit_get_cancel() -> None:
    backend = CeleryJobBackend(_FakeCelery())
    handle = backend.submit("demo.task", {"n": 1}, auth_subject="u1", tenant_id="t1")
    status = backend.get(handle.job_id, auth_subject="u1", tenant_id="t1")
    assert status is not None
    assert status.state is JobState.QUEUED
    assert backend.get(handle.job_id, auth_subject="other") is None
    assert backend.request_cancel(handle.job_id, auth_subject="u1", tenant_id="t1") is True


def test_rq_backend_submit_get_cancel() -> None:
    backend = RQJobBackend(_FakeQueue())
    handle = backend.submit("demo.task", {"n": 1}, auth_subject="u1")
    status = backend.get(handle.job_id, auth_subject="u1")
    assert status is not None
    assert backend.request_cancel(handle.job_id, auth_subject="u1") is True
