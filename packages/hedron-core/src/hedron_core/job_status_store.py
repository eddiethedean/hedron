"""Shared Redis status store for Celery/RQ JobBackend bridges (phase 0.13)."""

from __future__ import annotations

import json
import secrets
import time
from collections.abc import Mapping
from typing import Any, cast

from hedron_core.jobs import (
    JobHandle,
    JobState,
    JobStatus,
    RedisClient,
    _idempotency_scope_key,
    _status_from_dict,
    _status_to_dict,
    job_authorized,
)
from hedron_core.typing_aliases import JsonValue

__all__ = ["RedisStatusStore", "require_redis_status_client"]


def require_redis_status_client(client: RedisClient | None) -> RedisClient:
    """Refuse process-local durability claims when Redis is missing."""
    if client is None:
        raise RuntimeError(
            "Celery/RQ JobBackend durability requires a shared Redis status client "
            "(pass redis_client=...). Process-local status is not multi-worker safe."
        )
    return client


class RedisStatusStore:
    """Redis-backed job status + idempotency used by Celery/RQ bridges."""

    def __init__(
        self,
        client: RedisClient,
        *,
        prefix: str = "h1:job:",
        ttl_seconds: int = 86400,
    ) -> None:
        self._client = client
        self._prefix = prefix
        self._ttl = ttl_seconds

    def _key(self, job_id: str) -> str:
        return f"{self._prefix}{job_id}"

    def _idem_key(
        self,
        idempotency_key: str,
        *,
        tenant_id: str | None,
        auth_subject: str | None,
    ) -> str:
        scoped = _idempotency_scope_key(
            idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
        )
        return f"{self._prefix}idem:{scoped}"

    def _decode(self, raw: bytes | str | None) -> str | None:
        if raw is None:
            return None
        if isinstance(raw, bytes):
            return raw.decode("utf-8")
        return str(raw)

    def _load(self, job_id: str) -> dict[str, object] | None:
        raw = self._decode(self._client.get(self._key(job_id)))
        if raw is None:
            return None
        return cast(dict[str, object], json.loads(raw))

    def _store(self, data: Mapping[str, object]) -> None:
        self._client.set(
            self._key(str(data["job_id"])),
            json.dumps(data, default=str, separators=(",", ":")),
            ex=self._ttl,
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
        if idempotency_key:
            idem_key = self._idem_key(
                idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
            )
            existing_raw = self._decode(self._client.get(idem_key))
            if existing_raw:
                existing = self.get(existing_raw, auth_subject=auth_subject, tenant_id=tenant_id)
                if existing is not None:
                    return JobHandle(job_id=existing.job_id, idempotency_key=idempotency_key)
        job_id = secrets.token_urlsafe(12)
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
            data["idempotency_scope_key"] = _idempotency_scope_key(
                idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
            )
            self._client.set(
                self._idem_key(idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject),
                job_id,
                ex=self._ttl,
            )
        self._store(data)
        return JobHandle(job_id=job_id, idempotency_key=idempotency_key)

    def get(
        self,
        job_id: str,
        *,
        auth_subject: str | None = None,
        tenant_id: str | None = None,
    ) -> JobStatus | None:
        data = self._load(job_id)
        if data is None:
            return None
        status = _status_from_dict(data)
        if auth_subject is None and tenant_id is None:
            return status
        if not job_authorized(status, auth_subject=auth_subject, tenant_id=tenant_id):
            return None
        return status

    def request_cancel(
        self,
        job_id: str,
        *,
        auth_subject: str | None = None,
        tenant_id: str | None = None,
    ) -> bool:
        status = self.get(job_id, auth_subject=auth_subject, tenant_id=tenant_id)
        if status is None:
            return False
        if status.state in {JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED}:
            return False
        updated = JobStatus(
            job_id=status.job_id,
            state=JobState.CANCELLED if status.state is JobState.QUEUED else status.state,
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
        data = self._load(job_id) or {}
        payload = data.get("payload")
        stored: dict[str, object] = dict(
            _status_to_dict(
                updated,
                payload=cast(Mapping[str, JsonValue], payload)
                if isinstance(payload, dict)
                else None,
            )
        )
        scope = data.get("idempotency_scope_key")
        if isinstance(scope, str):
            stored["idempotency_scope_key"] = scope
        self._store(stored)
        return True

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
        payload = data.get("payload")
        stored = dict(
            _status_to_dict(
                updated,
                payload=cast(Mapping[str, JsonValue], payload)
                if isinstance(payload, dict)
                else None,
            )
        )
        scope = data.get("idempotency_scope_key")
        if isinstance(scope, str):
            stored["idempotency_scope_key"] = scope
        self._store(stored)
        return updated

    def cleanup_expired(self, *, older_than_seconds: float = 86400) -> int:
        keys_fn = getattr(self._client, "keys", None)
        if not callable(keys_fn):
            return 0
        removed = 0
        cutoff = time.time() - older_than_seconds
        raw_keys = cast(list[Any], keys_fn(f"{self._prefix}*"))
        for key in raw_keys:
            key_s = key.decode("utf-8") if isinstance(key, bytes) else str(key)
            if ":idem:" in key_s:
                continue
            raw = self._decode(self._client.get(key_s))
            if raw is None:
                continue
            data = json.loads(raw)
            updated_at = float(data.get("updated_at", 0))
            state = str(data.get("state", ""))
            if updated_at < cutoff and state in {
                JobState.SUCCEEDED.value,
                JobState.FAILED.value,
                JobState.CANCELLED.value,
            }:
                self._client.delete(key_s)
                removed += 1
        return removed
