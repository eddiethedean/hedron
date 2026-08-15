"""Optional RQ JobBackend bridge with Redis-durable status (phase 0.13)."""

from __future__ import annotations

import logging
from collections import OrderedDict
from collections.abc import Callable, Mapping
from typing import Any, cast

from hedron_core.job_status_store import (
    RQ_ENQUEUE_FAILED,
    RedisStatusStore,
    require_redis_status_client,
)
from hedron_core.jobs import JobHandle, JobState, JobStatus, RedisClient
from hedron_core.typing_aliases import JsonValue

__all__ = ["RQJobBackend"]

_logger = logging.getLogger("hedron.jobs.rq")

_TERMINAL_STATES = frozenset(
    {
        JobState.SUCCEEDED,
        JobState.FAILED,
        JobState.CANCELLED,
    }
)


class RQJobBackend:
    """``JobBackend`` over an RQ Queue with Redis-durable status.

    ``task_registry`` maps job_type strings to callables enqueued via ``queue.enqueue``.
    Status and idempotency require a shared ``redis_client`` (phase 0.13 / #11).
    The process-local ``_rq_jobs`` map is a cancel cache only — finished jobs are
    evicted so long-lived workers do not retain unbounded RQ ``Job`` objects (#243).
    """

    def __init__(
        self,
        queue: Any,
        *,
        redis_client: RedisClient | None = None,
        task_registry: Mapping[str, Callable[..., Any]] | None = None,
        key_prefix: str = "h1:job:",
        ttl_seconds: int = 86400,
        max_cached_jobs: int = 1_024,
    ) -> None:
        self._queue = queue
        self._registry = dict(task_registry or {})
        self._rq_jobs: OrderedDict[str, Any] = OrderedDict()
        self._max_cached_jobs = max(1, int(max_cached_jobs))
        self._store = RedisStatusStore(
            require_redis_status_client(redis_client),
            prefix=key_prefix,
            ttl_seconds=ttl_seconds,
        )

    def _remember_rq_job(self, job_id: str, rq_job: Any) -> None:
        self._rq_jobs[job_id] = rq_job
        self._rq_jobs.move_to_end(job_id)
        while len(self._rq_jobs) > self._max_cached_jobs:
            self._rq_jobs.popitem(last=False)

    def _forget_rq_job(self, job_id: str) -> None:
        self._rq_jobs.pop(job_id, None)

    def _prune_rq_jobs(self) -> None:
        for job_id in list(self._rq_jobs):
            status = self._store.get(job_id)
            if status is None or status.state in _TERMINAL_STATES:
                self._forget_rq_job(job_id)

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
        handle, created = self._store.submit(
            job_type,
            payload,
            idempotency_key=idempotency_key,
            tenant_id=tenant_id,
            auth_subject=auth_subject,
        )
        if not created:
            return handle
        try:
            rq_job = self._queue.enqueue(fn, dict(payload), job_id=handle.job_id)
            self._remember_rq_job(handle.job_id, rq_job)
        except Exception:
            # Release idempotency so a later submit can retry after a broker blip (#199).
            self._store.mark_enqueue_failed(handle.job_id, error=RQ_ENQUEUE_FAILED)
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
            try:
                rq_job = self._fetch_rq_job(job_id)
            except Exception:
                _logger.exception(
                    "HED-JOB-0001 RQ Job.fetch failed during cancel for job_id=%s; "
                    "restoring prior status",
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
        if rq_job is None:
            # Status cancelled; broker job genuinely missing — treat as success.
            self._forget_rq_job(job_id)
            return True
        try:
            rq_job.cancel()
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
        self._forget_rq_job(job_id)
        return True

    def _fetch_rq_job(self, job_id: str) -> Any | None:
        """Resolve an RQ job across workers via the shared connection.

        Missing jobs (``NoSuchJobError``) return ``None``. Unexpected fetch
        failures raise so callers can fail closed instead of reporting success (#206).
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
        except Exception as exc:  # noqa: BLE001
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
            raise

    def cleanup_expired(self, *, older_than_seconds: float = 86400) -> int:
        removed = self._store.cleanup_expired(older_than_seconds=older_than_seconds)
        self._prune_rq_jobs()
        return removed

    def mark(
        self,
        job_id: str,
        state: JobState,
        *,
        result: Any = None,
        error: str | None = None,
    ) -> JobStatus | None:
        status = self._store.mark(job_id, state, result=result, error=error)
        if status is not None and status.state in _TERMINAL_STATES:
            self._forget_rq_job(job_id)
        return status
