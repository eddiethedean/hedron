"""Optional Celery JobBackend bridge (phase 0.11)."""

from __future__ import annotations

import contextlib
import secrets
import time
from collections.abc import Mapping
from typing import Any

from hedron_core.jobs import JobHandle, JobState, JobStatus, job_authorized

__all__ = ["CeleryJobBackend"]


def _idempotency_scope_key(
    key: str, *, tenant_id: str | None, auth_subject: str | None
) -> str:
    return f"{tenant_id or ''}|{auth_subject or ''}|{key}"


class CeleryJobBackend:
    """Thin ``JobBackend`` that tracks status locally and best-effort enqueues Celery tasks.

    Requires an application-supplied Celery ``app``. Job execution is application-owned;
    this bridge implements the full ``JobBackend`` contract for status/cancel/mark.
    """

    def __init__(self, celery_app: Any, *, key_prefix: str = "h1:job:") -> None:
        self._app = celery_app
        self._prefix = key_prefix
        self._local: dict[str, JobStatus] = {}
        self._payloads: dict[str, dict[str, Any]] = {}
        self._idempotency: dict[str, str] = {}

    def _key(self, job_id: str) -> str:
        return f"{self._prefix}{job_id}"

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
        self._payloads[job_id] = dict(payload)
        if idempotency_key:
            scoped = _idempotency_scope_key(
                idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
            )
            self._idempotency[scoped] = job_id
        with contextlib.suppress(Exception):
            self._app.send_task(job_type, args=[dict(payload)], task_id=job_id)
        with contextlib.suppress(Exception):
            backend = getattr(self._app, "backend", None)
            if backend is not None and hasattr(backend, "set"):
                import json

                backend.set(self._key(job_id), json.dumps({"state": status.state.value}))
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
        with contextlib.suppress(Exception):
            self._app.control.revoke(job_id, terminate=False)
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
                self._payloads.pop(job_id, None)
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
