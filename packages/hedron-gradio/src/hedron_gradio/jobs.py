"""Gradio job handles and Hedron polling integration helpers."""

from __future__ import annotations

import math
import time
import uuid
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from hedron_gradio.errors import GradioRemoteError

__all__ = [
    "GradioJobHandle",
    "GradioJobManager",
    "GradioPollingStatus",
    "job_scope_key",
]

JobState = Literal["pending", "running", "complete", "failed", "cancelled"]


def job_scope_key(*, tenant_id: str | None = None, auth_subject: str | None = None) -> str:
    tenant = tenant_id if tenant_id is not None else ""
    subject = auth_subject if auth_subject is not None else ""
    return f"{tenant}\0{subject}"


@dataclass
class GradioJobHandle:
    job_id: str
    endpoint_name: str
    payload: Mapping[str, Any]
    scope_key: str
    created_at: float = field(default_factory=time.monotonic)
    deadline_at: float | None = None
    status: JobState = "pending"
    result: dict[str, Any] | None = None
    error: str | None = None

    def is_expired(self, *, now: float | None = None) -> bool:
        if self.deadline_at is None:
            return False
        current = time.monotonic() if now is None else now
        return current >= self.deadline_at


@dataclass
class GradioPollingStatus:
    job_id: str
    status: JobState
    result: dict[str, Any] | None = None
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"job_id": self.job_id, "status": self.status}
        if self.result is not None:
            payload["result"] = self.result
        if self.error is not None:
            payload["error"] = self.error
        return payload


class GradioJobManager:
    """In-process job registry with scope isolation and deadlines."""

    def __init__(self, *, default_timeout_seconds: float = 30.0) -> None:
        if (
            isinstance(default_timeout_seconds, bool)
            or not isinstance(default_timeout_seconds, (int, float))
            or not math.isfinite(float(default_timeout_seconds))
            or default_timeout_seconds <= 0
        ):
            raise ValueError("default_timeout_seconds must be > 0")
        self._default_timeout_seconds = default_timeout_seconds
        self._jobs: dict[str, GradioJobHandle] = {}

    def submit(
        self,
        endpoint_name: str,
        payload: Mapping[str, Any],
        *,
        scope_key: str,
        timeout_seconds: float | None = None,
    ) -> str:
        job_id = uuid.uuid4().hex
        timeout = timeout_seconds if timeout_seconds is not None else self._default_timeout_seconds
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(float(timeout))
            or timeout <= 0
        ):
            raise ValueError("timeout_seconds must be finite and > 0")
        now = time.monotonic()
        self._jobs[job_id] = GradioJobHandle(
            job_id=job_id,
            endpoint_name=endpoint_name,
            payload=dict(payload),
            scope_key=scope_key,
            created_at=now,
            deadline_at=now + timeout,
        )
        return job_id

    def _get_scoped(self, job_id: str, scope_key: str) -> GradioJobHandle:
        record = self._jobs.get(job_id)
        if record is None:
            raise GradioRemoteError(f"Unknown job id: {job_id}")
        if record.scope_key != scope_key:
            raise GradioRemoteError("Job scope mismatch")
        if record.is_expired():
            record.status = "failed"
            record.error = "Job deadline exceeded"
            raise GradioRemoteError(record.error)
        return record

    def mark_running(self, job_id: str, *, scope_key: str) -> None:
        record = self._get_scoped(job_id, scope_key)
        if record.status in {"complete", "cancelled", "failed"}:
            raise GradioRemoteError(f"Job already terminal: {record.status}")
        record.status = "running"

    def complete(
        self,
        job_id: str,
        *,
        scope_key: str,
        result: dict[str, Any],
    ) -> GradioPollingStatus:
        record = self._get_scoped(job_id, scope_key)
        if record.status == "cancelled":
            raise GradioRemoteError("Job was cancelled")
        record.status = "complete"
        record.result = dict(result)
        return GradioPollingStatus(job_id=job_id, status="complete", result=record.result)

    def fail(self, job_id: str, *, scope_key: str, error: str) -> GradioPollingStatus:
        record = self._get_scoped(job_id, scope_key)
        record.status = "failed"
        record.error = error
        return GradioPollingStatus(job_id=job_id, status="failed", error=error)

    def poll(self, job_id: str, *, scope_key: str) -> GradioPollingStatus:
        record = self._get_scoped(job_id, scope_key)
        if record.status == "pending":
            record.status = "running"
        return GradioPollingStatus(
            job_id=job_id,
            status=record.status,
            result=record.result,
            error=record.error,
        )

    def cancel(self, job_id: str, *, scope_key: str) -> bool:
        try:
            record = self._get_scoped(job_id, scope_key)
        except GradioRemoteError:
            return False
        if record.status in {"complete", "failed", "cancelled"}:
            return False
        record.status = "cancelled"
        record.error = "cancelled"
        return True

    def clear(self) -> None:
        self._jobs.clear()
