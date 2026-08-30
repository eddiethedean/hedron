"""Redis JobBackend that delegates to the shared status store."""

from __future__ import annotations

from collections.abc import Mapping

from hedron_core.job_status_store import RedisStatusStore
from hedron_core.jobs.backend import RedisClient
from hedron_core.jobs.types import JobHandle, JobState, JobStatus
from hedron_core.typing_aliases import JsonValue


class RedisJobBackend:
    """Redis-backed JobBackend using JSON values and shared idempotency keys.

    Default prefix ``h1:job:`` does not nest under ``RedisCacheBackend`` (``h1:c:``).
    """

    process_local = False

    def __init__(
        self, client: RedisClient, *, prefix: str = "h1:job:", ttl_seconds: int = 86400
    ) -> None:
        self._store = RedisStatusStore(client, prefix=prefix, ttl_seconds=ttl_seconds)
        self._client = client
        self._prefix = prefix
        self._ttl = ttl_seconds

    def _load(self, job_id: str) -> dict[str, object] | None:
        return self._store.load(job_id)

    def submit(
        self,
        job_type: str,
        payload: Mapping[str, JsonValue],
        *,
        idempotency_key: str | None = None,
        tenant_id: str | None = None,
        auth_subject: str | None = None,
    ) -> JobHandle:
        handle, _created = self._store.submit(
            job_type,
            payload,
            idempotency_key=idempotency_key,
            tenant_id=tenant_id,
            auth_subject=auth_subject,
        )
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
        return self._store.request_cancel(job_id, auth_subject=auth_subject, tenant_id=tenant_id)

    def cleanup_expired(self, *, older_than_seconds: float = 86400) -> int:
        return self._store.cleanup_expired(older_than_seconds=older_than_seconds)

    def mark(
        self,
        job_id: str,
        state: JobState,
        *,
        result: object = None,
        error: str | None = None,
    ) -> JobStatus | None:
        return self._store.mark(job_id, state, result=result, error=error)
