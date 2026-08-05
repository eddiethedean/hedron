"""Optional RQ JobBackend bridge (phase 0.11)."""

from __future__ import annotations

import secrets
import time
from collections.abc import Mapping
from typing import Any

from hedron_core.jobs import JobHandle, JobState, JobStatus

__all__ = ["RQJobBackend"]


class RQJobBackend:
    """Thin ``JobBackend`` over an application-supplied RQ Queue."""

    def __init__(self, queue: Any, *, key_prefix: str = "h1:job:") -> None:
        self._queue = queue
        self._prefix = key_prefix
        self._local: dict[str, JobStatus] = {}
        self._rq_jobs: dict[str, Any] = {}

    def submit(
        self,
        job_type: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
        tenant_id: str | None = None,
        auth_subject: str | None = None,
    ) -> JobHandle:
        job_id = secrets.token_urlsafe(12)
        now = time.time()
        status = JobStatus(
            job_id=job_id,
            state=JobState.QUEUED,
            job_type=job_type,
            tenant_id=tenant_id,
            auth_subject=auth_subject,
            created_at=now,
            updated_at=now,
        )
        self._local[job_id] = status
        try:
            # Application supplies a callable registered under job_type via queue.connection.
            fn = getattr(self._queue, "default_worker", None)
            if callable(job_type):
                rq_job = self._queue.enqueue(job_type, dict(payload), job_id=job_id)
                self._rq_jobs[job_id] = rq_job
            elif fn is not None:
                rq_job = self._queue.enqueue(fn, job_type, dict(payload), job_id=job_id)
                self._rq_jobs[job_id] = rq_job
        except Exception:  # noqa: BLE001
            pass
        return JobHandle(job_id=job_id, idempotency_key=idempotency_key)

    def get(
        self,
        job_id: str,
        *,
        auth_subject: str | None = None,
        tenant_id: str | None = None,
    ) -> JobStatus | None:
        status = self._local.get(job_id)
        if status is None:
            return None
        if auth_subject is not None and status.auth_subject not in (None, auth_subject):
            return None
        if tenant_id is not None and status.tenant_id not in (None, tenant_id):
            return None
        return status

    def request_cancel(
        self,
        job_id: str,
        *,
        auth_subject: str | None = None,
        tenant_id: str | None = None,
    ) -> bool:
        status = self.get(job_id, auth_subject=auth_subject, tenant_id=tenant_id)
        if status is None:
            return False
        self._local[job_id] = JobStatus(
            job_id=status.job_id,
            state=JobState.CANCELLED if status.state is JobState.QUEUED else status.state,
            job_type=status.job_type,
            tenant_id=status.tenant_id,
            auth_subject=status.auth_subject,
            result=status.result,
            error=status.error,
            retry_after=status.retry_after,
            created_at=status.created_at,
            updated_at=time.time(),
            cancel_requested=True,
        )
        rq_job = self._rq_jobs.get(job_id)
        if rq_job is not None:
            try:
                rq_job.cancel()
            except Exception:  # noqa: BLE001
                pass
        return True
