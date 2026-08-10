"""Optional RQ JobBackend bridge with Redis-durable status (phase 0.13)."""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from typing import Any, cast

from hedron_core.job_status_store import RedisStatusStore, require_redis_status_client
from hedron_core.jobs import JobHandle, JobState, JobStatus, RedisClient
from hedron_core.typing_aliases import JsonValue

__all__ = ["RQJobBackend"]

_logger = logging.getLogger("hedron.jobs.rq")


class RQJobBackend:
    """``JobBackend`` over an RQ Queue with Redis-durable status.

    ``task_registry`` maps job_type strings to callables enqueued via ``queue.enqueue``.
    Status and idempotency require a shared ``redis_client`` (phase 0.13 / #11).
    """

    def __init__(
        self,
        queue: Any,
        *,
        redis_client: RedisClient | None = None,
        task_registry: Mapping[str, Callable[..., Any]] | None = None,
        key_prefix: str = "h1:job:",
        ttl_seconds: int = 86400,
    ) -> None:
        self._queue = queue
        self._registry = dict(task_registry or {})
        self._rq_jobs: dict[str, Any] = {}
        self._store = RedisStatusStore(
            require_redis_status_client(redis_client),
            prefix=key_prefix,
            ttl_seconds=ttl_seconds,
        )

    def submit(
        self,
        job_type: str,
        payload: Mapping[str, JsonValue],
        *,
        idempotency_key: str | None = None,
        tenant_id: str | None = None,
        auth_subject: str | None = None,
    ) -> JobHandle:
        fn = self._registry.get(job_type)
        if fn is None:
            raise KeyError(f"Unknown RQ job_type {job_type!r}")
        handle = self._store.submit(
            job_type,
            payload,
            idempotency_key=idempotency_key,
            tenant_id=tenant_id,
            auth_subject=auth_subject,
        )
        try:
            rq_job = self._queue.enqueue(fn, dict(payload), job_id=handle.job_id)
            self._rq_jobs[handle.job_id] = rq_job
        except Exception:
            self._store.mark(
                handle.job_id,
                JobState.FAILED,
                error="RQ enqueue failed",
            )
            raise
        return handle

    def get(
        self,
        job_id: str,
        *,
        auth_subject: str | None = None,
        tenant_id: str | None = None,
    ) -> JobStatus | None:
        return self._store.get(job_id, auth_subject=auth_subject, tenant_id=tenant_id)

    def request_cancel(
        self,
        job_id: str,
        *,
        auth_subject: str | None = None,
        tenant_id: str | None = None,
    ) -> bool:
        prior = self._store._load(job_id)
        ok = self._store.request_cancel(job_id, auth_subject=auth_subject, tenant_id=tenant_id)
        if not ok:
            return False
        cancelled = self._store._load(job_id)
        rq_job = self._rq_jobs.get(job_id)
        if rq_job is None:
            rq_job = self._fetch_rq_job(job_id)
        if rq_job is None:
            # Status cancelled; broker job already gone — treat as success.
            return True
        try:
            rq_job.cancel()
            self._rq_jobs[job_id] = rq_job
        except Exception:
            _logger.exception(
                "HED-JOB-0001 RQ cancel failed for job_id=%s; restoring prior status",
                job_id,
            )
            if prior is not None and cancelled is not None:
                restored = self._store.restore_snapshot(
                    prior,
                    expected_updated_at=float(
                        cast(float | int | str, cancelled.get("updated_at", -1))
                    ),
                )
                if not restored:
                    _logger.warning(
                        "HED-JOB-0001 RQ cancel restore skipped for job_id=%s "
                        "(status advanced concurrently)",
                        job_id,
                    )
            return False
        return True

    def _fetch_rq_job(self, job_id: str) -> Any | None:
        """Resolve an RQ job across workers via the shared connection.

        Missing jobs return ``None``. Unexpected fetch failures are logged and
        also return ``None`` so callers keep the durable-status fallback path.
        """
        connection = getattr(self._queue, "connection", None)
        if connection is None:
            return None
        try:
            from rq.job import Job  # type: ignore[import-not-found]
        except ImportError:
            _logger.debug("rq is not installed; cannot fetch job_id=%s", job_id)
            return None
        try:
            return Job.fetch(job_id, connection=connection)
        except Exception as exc:
            # Prefer typed NoSuchJobError when present; fall back to class name.
            try:
                from rq.exceptions import NoSuchJobError  # type: ignore[import-not-found]
            except ImportError:
                NoSuchJobError = ()  # type: ignore[misc,assignment]
            if NoSuchJobError and isinstance(exc, NoSuchJobError):
                return None
            if type(exc).__name__ == "NoSuchJobError":
                return None
            _logger.warning("RQ Job.fetch failed for job_id=%s: %s", job_id, exc)
            return None

    def cleanup_expired(self, *, older_than_seconds: float = 86400) -> int:
        return self._store.cleanup_expired(older_than_seconds=older_than_seconds)

    def mark(
        self,
        job_id: str,
        state: JobState,
        *,
        result: Any = None,
        error: str | None = None,
    ) -> JobStatus | None:
        return self._store.mark(job_id, state, result=result, error=error)
