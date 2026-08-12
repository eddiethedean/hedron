"""Optional Celery JobBackend bridge with Redis-durable status (phase 0.13)."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any, cast

from hedron_core.job_status_store import RedisStatusStore, require_redis_status_client
from hedron_core.jobs import JobHandle, JobState, JobStatus, RedisClient
from hedron_core.typing_aliases import JsonValue

__all__ = ["CeleryJobBackend"]

_logger = logging.getLogger("hedron.jobs.celery")


class CeleryJobBackend:
    """``JobBackend`` that enqueues Celery tasks and stores status in shared Redis.

    Requires an application-supplied Celery ``app`` and a Redis ``redis_client`` for
    multi-worker durable status and idempotency (phase 0.13 / #11).
    """

    def __init__(
        self,
        celery_app: Any,
        *,
        redis_client: RedisClient | None = None,
        key_prefix: str = "h1:job:",
        ttl_seconds: int = 86400,
    ) -> None:
        self._app = celery_app
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
            self._app.send_task(job_type, args=[dict(payload)], task_id=handle.job_id)
        except Exception:
            self._store.mark(
                handle.job_id,
                JobState.FAILED,
                error="Celery enqueue failed",
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
        try:
            self._app.control.revoke(job_id, terminate=False)
        except Exception:
            _logger.exception(
                "HED-JOB-0001 Celery revoke failed for job_id=%s; restoring prior status",
                job_id,
            )
            if prior is not None and cancelled is not None:
                # CAS restore only if no concurrent mark advanced the record.
                restored = self._store.restore_snapshot(
                    prior,
                    expected_updated_at=float(
                        cast(float | int | str, cancelled.get("updated_at", -1))
                    ),
                )
                if not restored:
                    _logger.warning(
                        "HED-JOB-0001 Celery revoke restore skipped for job_id=%s "
                        "(status advanced concurrently)",
                        job_id,
                    )
            return False
        return True

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
