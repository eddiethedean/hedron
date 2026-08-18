"""Process-local in-memory job backend."""

from __future__ import annotations

import secrets
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass, field

from hedron_core.jobs.auth import job_authorized, job_authorized_http
from hedron_core.jobs.codec import _idempotency_scope_key, _legacy_idempotency_scope_key
from hedron_core.jobs.types import JobHandle, JobState, JobStatus
from hedron_core.typing_aliases import JsonValue


@dataclass
class _JobRecord:
    status: JobStatus
    payload: dict[str, JsonValue] = field(default_factory=dict)
    idempotency_key: str | None = None
    idempotency_scope_key: str | None = None


class InMemoryJobBackend:
    process_local = True

    def __init__(self) -> None:
        self._jobs: dict[str, _JobRecord] = {}
        self._idempotency: dict[str, str] = {}
        self._lock = threading.RLock()

    def submit(
        self,
        job_type: str,
        payload: Mapping[str, JsonValue],
        *,
        idempotency_key: str | None = None,
        tenant_id: str | None = None,
        auth_subject: str | None = None,
    ) -> JobHandle:
        with self._lock:
            scoped: str | None = None
            if idempotency_key:
                scoped = _idempotency_scope_key(
                    idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
                )
                legacy_scoped = _legacy_idempotency_scope_key(
                    idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
                )
                matched_scope = scoped
                existing_id = self._idempotency.get(scoped)
                if existing_id is None and legacy_scoped != scoped:
                    matched_scope = legacy_scoped
                    existing_id = self._idempotency.get(legacy_scoped)
                if existing_id is not None:
                    existing = self._jobs.get(existing_id)
                    if existing is not None:
                        if job_authorized(
                            existing.status, auth_subject=auth_subject, tenant_id=tenant_id
                        ):
                            return JobHandle(job_id=existing_id, idempotency_key=idempotency_key)
                        raise PermissionError("Idempotency key is already bound to another scope")
                    # The pointed-to job expired or was removed, so reclaim the key.
                    del self._idempotency[matched_scope]
            job_id = secrets.token_urlsafe(16)
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
            self._jobs[job_id] = _JobRecord(
                status=status,
                payload=dict(payload),
                idempotency_key=idempotency_key,
                idempotency_scope_key=scoped,
            )
            if scoped is not None:
                self._idempotency[scoped] = job_id
            return JobHandle(job_id=job_id, idempotency_key=idempotency_key)

    def get(
        self,
        job_id: str,
        *,
        auth_subject: str | None = None,
        tenant_id: str | None = None,
    ) -> JobStatus | None:
        with self._lock:
            rec = self._jobs.get(job_id)
            if rec is None:
                return None
            # Unrestricted read when caller omits both scope kwargs (internal/workers).
            # HTTP helpers must pass credentials and call job_authorized explicitly, or
            # pass matching kwargs here to filter.
            if auth_subject is None and tenant_id is None:
                return rec.status
            if not job_authorized(rec.status, auth_subject=auth_subject, tenant_id=tenant_id):
                return None
            return rec.status

    def request_cancel(
        self,
        job_id: str,
        *,
        auth_subject: str | None = None,
        tenant_id: str | None = None,
    ) -> bool:
        with self._lock:
            rec = self._jobs.get(job_id)
            if rec is None:
                return False
            st = rec.status
            if not job_authorized_http(st, auth_subject=auth_subject, tenant_id=tenant_id):
                return False
            if st.state in {JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED}:
                return False
            rec.status = JobStatus(
                job_id=st.job_id,
                state=JobState.CANCELLED if st.state == JobState.QUEUED else st.state,
                job_type=st.job_type,
                tenant_id=st.tenant_id,
                auth_subject=st.auth_subject,
                result=st.result,
                error=st.error,
                retry_after=st.retry_after,
                created_at=st.created_at,
                updated_at=time.time(),
                cancel_requested=True,
            )
            return True

    def cleanup_expired(self, *, older_than_seconds: float = 86400) -> int:
        cutoff = time.time() - older_than_seconds
        removed = 0
        with self._lock:
            for job_id, rec in list(self._jobs.items()):
                if rec.status.updated_at < cutoff and rec.status.state in {
                    JobState.SUCCEEDED,
                    JobState.FAILED,
                    JobState.CANCELLED,
                }:
                    del self._jobs[job_id]
                    scoped = rec.idempotency_scope_key
                    if scoped and self._idempotency.get(scoped) == job_id:
                        del self._idempotency[scoped]
                    removed += 1
        return removed

    def mark(
        self,
        job_id: str,
        state: JobState,
        *,
        result: object = None,
        error: str | None = None,
    ) -> JobStatus | None:
        terminal = frozenset({JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED})
        cancel_force = frozenset({JobState.RUNNING, JobState.SUCCEEDED, JobState.FAILED})
        with self._lock:
            rec = self._jobs.get(job_id)
            if rec is None:
                return None
            st = rec.status
            if st.state in terminal and state not in terminal:
                return st
            if (
                st.state in terminal
                and state in terminal
                and state is not st.state
                and not (st.cancel_requested and state is JobState.CANCELLED)
            ):
                return st
            effective = state
            if st.cancel_requested and effective in cancel_force:
                effective = JobState.CANCELLED
            rec.status = JobStatus(
                job_id=st.job_id,
                state=effective,
                job_type=st.job_type,
                tenant_id=st.tenant_id,
                auth_subject=st.auth_subject,
                result=result if result is not None else st.result,
                error=error if error is not None else st.error,
                retry_after=st.retry_after,
                created_at=st.created_at,
                updated_at=time.time(),
                cancel_requested=st.cancel_requested,
            )
            return rec.status
