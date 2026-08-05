"""Optional RQ JobBackend bridge (phase 0.11)."""

from __future__ import annotations

import contextlib
import secrets
import time
from collections.abc import Callable, Mapping
from typing import Any

from hedron_core.jobs import JobHandle, JobState, JobStatus, job_authorized

__all__ = ["RQJobBackend"]


def _idempotency_scope_key(
    key: str, *, tenant_id: str | None, auth_subject: str | None
) -> str:
    return f"{tenant_id or ''}|{auth_subject or ''}|{key}"


class RQJobBackend:
    """Thin ``JobBackend`` over an application-supplied RQ Queue.

    ``task_registry`` maps job_type strings to callables enqueued via ``queue.enqueue``.
    """

    def __init__(
        self,
        queue: Any,
        *,
        task_registry: Mapping[str, Callable[..., Any]] | None = None,
        key_prefix: str = "h1:job:",
    ) -> None:
        self._queue = queue
        self._prefix = key_prefix
        self._registry = dict(task_registry or {})
        self._local: dict[str, JobStatus] = {}
        self._rq_jobs: dict[str, Any] = {}
        self._idempotency: dict[str, str] = {}

    def submit(
        self,
        job_type: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
        tenant_id: str | None = None,
        auth_subject: str | None = None,
    ) -> JobHandle:
        if idempotency_key:
            scoped = _idempotency_scope_key(
                idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
            )
            existing_id = self._idempotency.get(scoped)
            if existing_id is not None and existing_id in self._local:
                return JobHandle(job_id=existing_id, idempotency_key=idempotency_key)
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
        if idempotency_key:
            scoped = _idempotency_scope_key(
                idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
            )
            self._idempotency[scoped] = job_id
        fn = self._registry.get(job_type)
        if fn is not None:
            with contextlib.suppress(Exception):
                rq_job = self._queue.enqueue(fn, dict(payload), job_id=job_id)
                self._rq_jobs[job_id] = rq_job
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
        if auth_subject is None and tenant_id is None:
            return status
        if not job_authorized(status, auth_subject=auth_subject, tenant_id=tenant_id):
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
        if status.state in {JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED}:
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
            with contextlib.suppress(Exception):
                rq_job.cancel()
        return True

    def cleanup_expired(self, *, older_than_seconds: float = 86400) -> int:
        cutoff = time.time() - older_than_seconds
        removed = 0
        for job_id, status in list(self._local.items()):
            if status.updated_at < cutoff and status.state in {
                JobState.SUCCEEDED,
                JobState.FAILED,
                JobState.CANCELLED,
            }:
                del self._local[job_id]
                self._rq_jobs.pop(job_id, None)
                removed += 1
        return removed

    def mark(
        self,
        job_id: str,
        state: JobState,
        *,
        result: Any = None,
        error: str | None = None,
    ) -> JobStatus | None:
        status = self._local.get(job_id)
        if status is None:
            return None
        updated = JobStatus(
            job_id=status.job_id,
            state=state,
            job_type=status.job_type,
            tenant_id=status.tenant_id,
            auth_subject=status.auth_subject,
            result=result if result is not None else status.result,
            error=error if error is not None else status.error,
            retry_after=status.retry_after,
            created_at=status.created_at,
            updated_at=time.time(),
            cancel_requested=status.cancel_requested,
        )
        self._local[job_id] = updated
        return updated
