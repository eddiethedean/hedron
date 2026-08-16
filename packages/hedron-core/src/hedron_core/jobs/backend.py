"""Job backend protocols."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from hedron_core.jobs.types import JobHandle, JobState, JobStatus
from hedron_core.typing_aliases import JsonValue


class RedisPipeline(Protocol):
    def watch(self, *names: str) -> object: ...

    def unwatch(self) -> object: ...

    def multi(self) -> object: ...

    def get(self, name: str) -> bytes | str | None: ...

    def set(
        self,
        name: str,
        value: str,
        ex: int | None = None,
        nx: bool = False,
    ) -> object: ...

    def delete(self, *names: str) -> object: ...

    def execute(self) -> object: ...

    def reset(self) -> object: ...


@runtime_checkable
class RedisClient(Protocol):
    def get(self, name: str) -> bytes | str | None: ...

    def set(
        self,
        name: str,
        value: str,
        ex: int | None = None,
        nx: bool = False,
    ) -> object: ...

    def delete(self, *names: str) -> object: ...

    def pipeline(self, transaction: bool = True) -> RedisPipeline: ...


@runtime_checkable
class JobBackend(Protocol):
    """Durable job store used by status polling and inference admission.

    Implementations must scope observation and cancel by ``auth_subject`` /
    ``tenant_id`` when those values are present. In-memory backends do not span
    processes — use Redis (or Celery/RQ bridges) for multi-worker deployments.

    Implementations may set ``process_local = True`` when they cannot span
    processes. Production gates treat a missing attribute as durable.

    Methods:
        submit: Enqueue work and return a ``JobHandle``.
        get: Fetch status when authorized; return ``None`` when missing/denied.
        request_cancel: Request cancellation; return whether the request was accepted.
        cleanup_expired: Drop stale records; return the number removed.
        mark: Update lifecycle state / result payload for an existing job.
    """

    def submit(
        self,
        job_type: str,
        payload: Mapping[str, JsonValue],
        *,
        idempotency_key: str | None = None,
        tenant_id: str | None = None,
        auth_subject: str | None = None,
    ) -> JobHandle:
        """Enqueue a job.

        Args:
            job_type: Application-defined job type string.
            payload: JSON-compatible job payload.
            idempotency_key: Optional deduplication key.
            tenant_id: Optional tenant scope for authorization.
            auth_subject: Optional subject scope for authorization.

        Returns:
            Handle containing the assigned ``job_id``.
        """
        ...

    def get(
        self,
        job_id: str,
        *,
        auth_subject: str | None = None,
        tenant_id: str | None = None,
    ) -> JobStatus | None:
        """Return job status when the caller is authorized to observe it.

        Args:
            job_id: Job identifier.
            auth_subject: Optional subject scope; fail closed when mismatched.
            tenant_id: Optional tenant scope; fail closed when mismatched.

        Returns:
            ``JobStatus`` or ``None`` when missing or unauthorized.
        """
        ...

    def request_cancel(
        self,
        job_id: str,
        *,
        auth_subject: str | None = None,
        tenant_id: str | None = None,
    ) -> bool:
        """Request cancellation for a job.

        Args:
            job_id: Job identifier.
            auth_subject: Optional subject scope.
            tenant_id: Optional tenant scope.

        Returns:
            ``True`` when the cancel request was accepted.
        """
        ...

    def cleanup_expired(self, *, older_than_seconds: float = 86400) -> int:
        """Remove expired job records.

        Args:
            older_than_seconds: Age threshold for cleanup.

        Returns:
            Number of records removed.
        """
        ...

    def mark(
        self,
        job_id: str,
        state: JobState,
        *,
        result: object = None,
        error: str | None = None,
    ) -> JobStatus | None:
        """Update lifecycle state for an existing job.

        Args:
            job_id: Job identifier.
            state: New ``JobState`` value.
            result: Optional successful result payload.
            error: Optional failure message.

        Returns:
            Updated ``JobStatus``, or ``None`` when the job is missing.
        """
        ...
