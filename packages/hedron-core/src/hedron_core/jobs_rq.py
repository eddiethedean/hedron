"""Optional RQ JobBackend bridge with Redis-durable status (phase 0.13)."""

from __future__ import annotations

import contextlib
from collections.abc import Callable, Mapping
from typing import Any

from hedron_core.job_status_store import RedisStatusStore, require_redis_status_client
from hedron_core.jobs import JobHandle, JobState, JobStatus, RedisClient
from hedron_core.typing_aliases import JsonValue

__all__ = ["RQJobBackend"]


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
        handle = self._store.submit(
            job_type,
            payload,
            idempotency_key=idempotency_key,
            tenant_id=tenant_id,
            auth_subject=auth_subject,
        )
        fn = self._registry.get(job_type)
        if fn is not None:
            with contextlib.suppress(Exception):
                rq_job = self._queue.enqueue(fn, dict(payload), job_id=handle.job_id)
                self._rq_jobs[handle.job_id] = rq_job
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
        ok = self._store.request_cancel(job_id, auth_subject=auth_subject, tenant_id=tenant_id)
        if ok:
            rq_job = self._rq_jobs.get(job_id)
            if rq_job is not None:
                with contextlib.suppress(Exception):
                    rq_job.cancel()
        return ok

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
