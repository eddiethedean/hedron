"""Durable job backend protocol and in-memory / Redis implementations."""

from __future__ import annotations

import json
import secrets
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable

__all__ = [
    "InMemoryJobBackend",
    "JobBackend",
    "JobHandle",
    "JobState",
    "JobStatus",
    "RedisJobBackend",
    "get_job_backend",
    "job_status_interaction",
    "reset_jobs_for_tests",
    "set_job_backend",
]


class JobState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class JobHandle:
    job_id: str
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class JobStatus:
    job_id: str
    state: JobState
    job_type: str
    tenant_id: str | None = None
    auth_subject: str | None = None
    result: Any = None
    error: str | None = None
    retry_after: int = 2
    created_at: float = 0.0
    updated_at: float = 0.0
    cancel_requested: bool = False


@runtime_checkable
class JobBackend(Protocol):
    def submit(
        self,
        job_type: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
        tenant_id: str | None = None,
        auth_subject: str | None = None,
    ) -> JobHandle: ...

    def get(self, job_id: str) -> JobStatus | None: ...

    def request_cancel(self, job_id: str) -> bool: ...

    def cleanup_expired(self, *, older_than_seconds: float = 86400) -> int: ...

    def mark(
        self,
        job_id: str,
        state: JobState,
        *,
        result: Any = None,
        error: str | None = None,
    ) -> JobStatus | None: ...


@dataclass
class _JobRecord:
    status: JobStatus
    payload: dict[str, Any] = field(default_factory=dict)


class InMemoryJobBackend:
    def __init__(self) -> None:
        self._jobs: dict[str, _JobRecord] = {}
        self._idempotency: dict[str, str] = {}
        self._lock = threading.RLock()

    def submit(
        self,
        job_type: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
        tenant_id: str | None = None,
        auth_subject: str | None = None,
    ) -> JobHandle:
        with self._lock:
            if idempotency_key and idempotency_key in self._idempotency:
                return JobHandle(
                    job_id=self._idempotency[idempotency_key],
                    idempotency_key=idempotency_key,
                )
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
            self._jobs[job_id] = _JobRecord(status=status, payload=dict(payload))
            if idempotency_key:
                self._idempotency[idempotency_key] = job_id
            return JobHandle(job_id=job_id, idempotency_key=idempotency_key)

    def get(self, job_id: str) -> JobStatus | None:
        with self._lock:
            rec = self._jobs.get(job_id)
            return rec.status if rec else None

    def request_cancel(self, job_id: str) -> bool:
        with self._lock:
            rec = self._jobs.get(job_id)
            if rec is None:
                return False
            st = rec.status
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
        with self._lock:
            rec = self._jobs.get(job_id)
            if rec is None:
                return None
            st = rec.status
            if st.cancel_requested and state == JobState.RUNNING:
                state = JobState.CANCELLED
            rec.status = JobStatus(
                job_id=st.job_id,
                state=state,
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


class RedisJobBackend:
    """Redis-backed JobBackend using JSON values and ``h1:job:`` keys."""

    def __init__(self, client: Any, *, prefix: str = "h1:job:") -> None:
        self._client = client
        self._prefix = prefix
        self._memory = InMemoryJobBackend()  # idempotency map fallback for tests

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
        handle = self._memory.submit(
            job_type,
            payload,
            idempotency_key=idempotency_key,
            tenant_id=tenant_id,
            auth_subject=auth_subject,
        )
        status = self._memory.get(handle.job_id)
        assert status is not None
        self._client.set(
            self._key(handle.job_id),
            json.dumps(
                {
                    "job_id": status.job_id,
                    "state": status.state.value,
                    "job_type": status.job_type,
                    "tenant_id": status.tenant_id,
                    "auth_subject": status.auth_subject,
                    "retry_after": status.retry_after,
                    "created_at": status.created_at,
                    "updated_at": status.updated_at,
                    "payload": dict(payload),
                },
                separators=(",", ":"),
            ),
            ex=86400,
        )
        return handle

    def get(self, job_id: str) -> JobStatus | None:
        raw = self._client.get(self._key(job_id))
        if raw is None:
            return self._memory.get(job_id)
        data = json.loads(raw)
        return JobStatus(
            job_id=data["job_id"],
            state=JobState(data["state"]),
            job_type=data["job_type"],
            tenant_id=data.get("tenant_id"),
            auth_subject=data.get("auth_subject"),
            result=data.get("result"),
            error=data.get("error"),
            retry_after=int(data.get("retry_after", 2)),
            created_at=float(data.get("created_at", 0)),
            updated_at=float(data.get("updated_at", 0)),
            cancel_requested=bool(data.get("cancel_requested", False)),
        )

    def request_cancel(self, job_id: str) -> bool:
        ok = self._memory.request_cancel(job_id)
        status = self._memory.get(job_id)
        if status is not None:
            self.mark(job_id, status.state, error=status.error)
        return ok

    def cleanup_expired(self, *, older_than_seconds: float = 86400) -> int:
        return self._memory.cleanup_expired(older_than_seconds=older_than_seconds)

    def mark(
        self,
        job_id: str,
        state: JobState,
        *,
        result: Any = None,
        error: str | None = None,
    ) -> JobStatus | None:
        status = self._memory.mark(job_id, state, result=result, error=error)
        if status is None:
            return None
        self._client.set(
            self._key(job_id),
            json.dumps(
                {
                    "job_id": status.job_id,
                    "state": status.state.value,
                    "job_type": status.job_type,
                    "tenant_id": status.tenant_id,
                    "auth_subject": status.auth_subject,
                    "result": status.result,
                    "error": status.error,
                    "retry_after": status.retry_after,
                    "created_at": status.created_at,
                    "updated_at": status.updated_at,
                    "cancel_requested": status.cancel_requested,
                },
                default=str,
                separators=(",", ":"),
            ),
            ex=86400,
        )
        return status


_backend: JobBackend = InMemoryJobBackend()


def get_job_backend() -> JobBackend:
    return _backend


def set_job_backend(backend: JobBackend) -> None:
    global _backend
    _backend = backend


def reset_jobs_for_tests() -> None:
    global _backend
    _backend = InMemoryJobBackend()


def job_status_interaction(status: JobStatus) -> Any:
    """Portable 202 InteractionResult with Retry-After and accessible polling UI."""
    from hedron_core.builtins import Status
    from hedron_core.interaction import InteractionResult

    label = f"Job {status.job_id}: {status.state.value}"
    content = Status(label, tone="info", live=True)
    return InteractionResult(
        content=content,
        status_code=202,
        cache="no-store",
        headers={"Retry-After": str(status.retry_after)},
        explanation="Bounded polling job status (SSE deferred post-1.0)",
    )
