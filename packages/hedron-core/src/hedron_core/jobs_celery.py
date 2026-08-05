"""Optional Celery JobBackend bridge (phase 0.11)."""

from __future__ import annotations

import json
import secrets
import time
from collections.abc import Mapping
from typing import Any

from hedron_core.jobs import JobHandle, JobState, JobStatus

__all__ = ["CeleryJobBackend"]


class CeleryJobBackend:
    """Thin ``JobBackend`` that stores status in a Celery result backend.

    Requires an application-supplied Celery ``app``. Job execution is application-owned;
    this bridge only implements submit/get/cancel/status semantics.
    """

    def __init__(self, celery_app: Any, *, key_prefix: str = "h1:job:") -> None:
        self._app = celery_app
        self._prefix = key_prefix
        self._local: dict[str, JobStatus] = {}

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
        # Best-effort enqueue when a task name matches job_type.
        try:
            self._app.send_task(job_type, args=[dict(payload)], task_id=job_id)
        except Exception:  # noqa: BLE001 — application may register tasks later
            pass
        try:
            backend = getattr(self._app, "backend", None)
            if backend is not None and hasattr(backend, "set"):
                backend.set(self._key(job_id), json.dumps({"state": status.state.value}))
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
            state=status.state,
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
        try:
            self._app.control.revoke(job_id, terminate=False)
        except Exception:  # noqa: BLE001
            pass
        return True
