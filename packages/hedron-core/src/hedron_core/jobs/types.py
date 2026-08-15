"""Job status types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


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
    result: object = None
    error: str | None = None
    retry_after: int = 2
    created_at: float = 0.0
    updated_at: float = 0.0
    cancel_requested: bool = False
