"""Durable job backend protocol and in-memory / Redis implementations."""

from __future__ import annotations

import json
import secrets
import threading
import time
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol, cast, runtime_checkable

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
    idempotency_key: str | None = None


def _status_from_dict(data: Mapping[str, Any]) -> JobStatus:
    return JobStatus(
        job_id=str(data["job_id"]),
        state=JobState(str(data["state"])),
        job_type=str(data["job_type"]),
        tenant_id=data.get("tenant_id"),
        auth_subject=data.get("auth_subject"),
        result=data.get("result"),
        error=data.get("error"),
        retry_after=int(data.get("retry_after", 2)),
        created_at=float(data.get("created_at", 0)),
        updated_at=float(data.get("updated_at", 0)),
        cancel_requested=bool(data.get("cancel_requested", False)),
    )


def _status_to_dict(
    status: JobStatus,
    *,
    payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {
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
    }
    if payload is not None:
        data["payload"] = dict(payload)
    return data


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
            self._jobs[job_id] = _JobRecord(
                status=status,
                payload=dict(payload),
                idempotency_key=idempotency_key,
            )
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
                    if rec.idempotency_key and self._idempotency.get(rec.idempotency_key) == job_id:
                        del self._idempotency[rec.idempotency_key]
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
    """Redis-backed JobBackend using JSON values and shared idempotency keys."""

    def __init__(self, client: Any, *, prefix: str = "h1:job:", ttl_seconds: int = 86400) -> None:
        self._client = client
        self._prefix = prefix
        self._ttl = ttl_seconds

    def _key(self, job_id: str) -> str:
        return f"{self._prefix}{job_id}"

    def _idem_key(self, idempotency_key: str) -> str:
        return f"{self._prefix}idem:{idempotency_key}"

    def _decode(self, raw: Any) -> str | None:
        if raw is None:
            return None
        if isinstance(raw, bytes):
            return raw.decode("utf-8")
        return str(raw)

    def _load(self, job_id: str) -> dict[str, Any] | None:
        raw = self._decode(self._client.get(self._key(job_id)))
        if raw is None:
            return None
        return json.loads(raw)

    def _store(self, data: Mapping[str, Any]) -> None:
        self._client.set(
            self._key(str(data["job_id"])),
            json.dumps(data, default=str, separators=(",", ":")),
            ex=self._ttl,
        )

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
            existing = self._decode(self._client.get(self._idem_key(idempotency_key)))
            if existing is not None:
                return JobHandle(job_id=existing, idempotency_key=idempotency_key)

        job_id = secrets.token_urlsafe(16)
        if idempotency_key:
            # SET NX so concurrent workers share one job id.
            created = self._client.set(
                self._idem_key(idempotency_key),
                job_id,
                nx=True,
                ex=self._ttl,
            )
            if not created:
                existing = self._decode(self._client.get(self._idem_key(idempotency_key)))
                if existing is not None:
                    return JobHandle(job_id=existing, idempotency_key=idempotency_key)

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
        data = _status_to_dict(status, payload=payload)
        if idempotency_key:
            data["idempotency_key"] = idempotency_key
        self._store(data)
        return JobHandle(job_id=job_id, idempotency_key=idempotency_key)

    def get(self, job_id: str) -> JobStatus | None:
        data = self._load(job_id)
        if data is None:
            return None
        return _status_from_dict(data)

    def request_cancel(self, job_id: str) -> bool:
        data = self._load(job_id)
        if data is None:
            return False
        status = _status_from_dict(data)
        if status.state in {JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED}:
            return False
        updated = JobStatus(
            job_id=status.job_id,
            state=JobState.CANCELLED if status.state == JobState.QUEUED else status.state,
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
        payload = data.get("payload") if isinstance(data.get("payload"), dict) else {}
        stored = _status_to_dict(updated, payload=payload)  # type: ignore[arg-type]
        if "idempotency_key" in data:
            stored["idempotency_key"] = data["idempotency_key"]
        self._store(stored)
        return True

    def cleanup_expired(self, *, older_than_seconds: float = 86400) -> int:
        # Redis TTLs own expiry; scan is best-effort for tests/stubs without SCAN.
        removed = 0
        cutoff = time.time() - older_than_seconds
        keys_fn = getattr(self._client, "keys", None)
        if not callable(keys_fn):
            return 0
        for key in cast(Iterable[object], keys_fn(f"{self._prefix}*")):
            key_s = self._decode(key) or ""
            if ":idem:" in key_s:
                continue
            raw = self._decode(self._client.get(key))
            if raw is None:
                continue
            data = json.loads(raw)
            status = _status_from_dict(data)
            if status.updated_at < cutoff and status.state in {
                JobState.SUCCEEDED,
                JobState.FAILED,
                JobState.CANCELLED,
            }:
                self._client.delete(key)
                idem = data.get("idempotency_key")
                if isinstance(idem, str) and idem:
                    self._client.delete(self._idem_key(idem))
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
        data = self._load(job_id)
        if data is None:
            return None
        status = _status_from_dict(data)
        if status.cancel_requested and state == JobState.RUNNING:
            state = JobState.CANCELLED
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
        payload = data.get("payload") if isinstance(data.get("payload"), dict) else {}
        stored = _status_to_dict(updated, payload=payload)  # type: ignore[arg-type]
        if "idempotency_key" in data:
            stored["idempotency_key"] = data["idempotency_key"]
        self._store(stored)
        return updated


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
