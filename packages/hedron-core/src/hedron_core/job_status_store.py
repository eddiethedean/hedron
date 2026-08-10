"""Shared Redis status store for Celery/RQ JobBackend bridges (phase 0.13)."""

from __future__ import annotations

import json
import secrets
import time
from collections.abc import Iterable, Mapping
from typing import Any, cast

from hedron_core.jobs import (
    JobHandle,
    JobState,
    JobStatus,
    RedisClient,
    RedisPipeline,
    _idempotency_scope_key,
    _status_from_dict,
    _status_to_dict,
    job_authorized,
)
from hedron_core.typing_aliases import JsonValue

__all__ = ["RedisStatusStore", "require_redis_status_client"]

_TERMINAL = frozenset({JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED})
_CANCEL_FORCE = frozenset({JobState.RUNNING, JobState.SUCCEEDED, JobState.FAILED})


def require_redis_status_client(client: RedisClient | None) -> RedisClient:
    """Refuse process-local durability claims when Redis is missing."""
    if client is None:
        raise RuntimeError(
            "Celery/RQ JobBackend durability requires a shared Redis status client "
            "(pass redis_client=...). Process-local status is not multi-worker safe."
        )
    return client


def _apply_cancel_sticky(merged: dict[str, object]) -> None:
    """Keep cancel sticky and force CANCELLED for worker success/fail/running marks."""
    if not merged.get("cancel_requested"):
        return
    state = str(merged.get("state", ""))
    if state in {s.value for s in _CANCEL_FORCE}:
        merged["state"] = JobState.CANCELLED.value


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

    def _store_cas(
        self,
        data: Mapping[str, object],
        *,
        expected_updated_at: float,
        sticky_cancel: bool = True,
    ) -> bool:
        """Compare-and-swap store when Redis WATCH/pipeline is available.

        Fail closed without pipeline/WATCH — never blind-overwrite production job state.
        When ``sticky_cancel`` is true (default), preserve ``cancel_requested`` from the
        current record. Snapshot restore sets ``sticky_cancel=False`` so a failed broker
        cancel can roll status back exactly.
        """
        key = self._key(str(data["job_id"]))
        pipeline_factory = getattr(self._client, "pipeline", None)
        if not callable(pipeline_factory):
            raise RuntimeError(
                "RedisStatusStore requires a client with pipeline()/WATCH for CAS; "
                "blind overwrite is not allowed for production job state."
            )
        pipe = cast(RedisPipeline, pipeline_factory())
        watch_error: type[BaseException] | None = None
        try:
            from redis.exceptions import WatchError as _WatchError  # type: ignore[import-not-found]

            watch_error = _WatchError
        except ImportError:
            watch_error = None
        if watch_error is None:
            raise RuntimeError(
                "RedisStatusStore requires redis.exceptions.WatchError for CAS; "
                "install redis-py or use a client with WATCH support."
            )
        for _ in range(8):
            try:
                pipe.watch(key)
                raw = self._decode(pipe.get(key) if hasattr(pipe, "get") else self._client.get(key))
                if raw is None:
                    pipe.unwatch()
                    return False
                current = json.loads(raw)
                if float(current.get("updated_at", -1)) != float(expected_updated_at):
                    pipe.unwatch()
                    return False
                merged = dict(data)
                if sticky_cancel:
                    if current.get("cancel_requested"):
                        merged["cancel_requested"] = True
                    _apply_cancel_sticky(merged)
                pipe.multi()
                pipe.set(
                    key,
                    json.dumps(merged, default=str, separators=(",", ":")),
                    ex=self._ttl,
                )
                pipe.execute()
                return True
            except Exception as exc:
                if isinstance(exc, watch_error):
                    continue
                raise
        return False

    def restore_snapshot(
        self,
        data: Mapping[str, object],
        *,
        expected_updated_at: float | None = None,
    ) -> bool:
        """Restore a prior snapshot when broker cancel fails after a status update.

        When ``expected_updated_at`` is set, restore only via CAS so a concurrent
        worker ``mark()`` is not rolled back. Without an expected version, refuse
        (fail closed) — blind restore is no longer supported.
        """
        if expected_updated_at is None:
            raise RuntimeError(
                "RedisStatusStore.restore_snapshot requires expected_updated_at for CAS; "
                "blind overwrite is not allowed."
            )
        return self._store_cas(
            dict(data),
            expected_updated_at=expected_updated_at,
            sticky_cancel=False,
        )

    def delete(self, job_id: str) -> None:
        """Remove a job body and any idempotency pointer it owns."""
        data = self._load(job_id)
        self._client.delete(self._key(job_id))
        if data is None:
            return
        scope = data.get("idempotency_scope_key")
        if isinstance(scope, str) and scope:
            idem_key = f"{self._prefix}idem:{scope}"
            pointed = self._decode(self._client.get(idem_key))
            if pointed == job_id:
                self._client.delete(idem_key)

    def submit(
        self,
        job_type: str,
        payload: Mapping[str, JsonValue],
        *,
        idempotency_key: str | None = None,
        tenant_id: str | None = None,
        auth_subject: str | None = None,
    ) -> JobHandle:
        idem_redis_key: str | None = None
        if idempotency_key:
            idem_redis_key = self._idem_key(
                idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
            )
            existing_raw = self._decode(self._client.get(idem_redis_key))
            if existing_raw:
                existing = self.get(existing_raw, auth_subject=auth_subject, tenant_id=tenant_id)
                if existing is not None:
                    return JobHandle(job_id=existing.job_id, idempotency_key=idempotency_key)
                # Stale or cross-scope pointer — drop and continue.
                self._client.delete(idem_redis_key)

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
            data["idempotency_key"] = idempotency_key
            data["idempotency_scope_key"] = _idempotency_scope_key(
                idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
            )
        # Persist the job body before claiming the idempotency key so losers never
        # observe a key that points at a missing record.
        self._store(data)

        if idem_redis_key is not None:
            created = self._client.set(
                idem_redis_key,
                job_id,
                nx=True,
                ex=self._ttl,
            )
            if not created:
                self._client.delete(self._key(job_id))
                existing = self._decode(self._client.get(idem_redis_key))
                if existing is not None:
                    for _ in range(5):
                        loaded = self._load(existing)
                        if loaded is not None:
                            return JobHandle(job_id=existing, idempotency_key=idempotency_key)
                        time.sleep(0.01)
                    if self._load(existing) is not None:
                        return JobHandle(job_id=existing, idempotency_key=idempotency_key)
                raise RuntimeError(
                    "Idempotent job submit lost the race and the winner record is unavailable"
                )

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
        for _ in range(5):
            data = self._load(job_id)
            if data is None:
                return False
            status = _status_from_dict(data)
            # Fail closed for scoped jobs when credentials are omitted (match RedisJobBackend).
            if not job_authorized(status, auth_subject=auth_subject, tenant_id=tenant_id):
                return False
            if status.state in _TERMINAL:
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
            if isinstance(data.get("idempotency_key"), str):
                stored["idempotency_key"] = str(data["idempotency_key"])
            if self._store_cas(stored, expected_updated_at=status.updated_at):
                return True
        return False

    def mark(
        self,
        job_id: str,
        state: JobState,
        *,
        result: Any = None,
        error: str | None = None,
    ) -> JobStatus | None:
        for _ in range(5):
            data = self._load(job_id)
            if data is None:
                return None
            status = _status_from_dict(data)
            if status.state in _TERMINAL and state not in _TERMINAL:
                return status
            if (
                status.state in _TERMINAL
                and state in _TERMINAL
                and state is not status.state
                and not (status.cancel_requested and state is JobState.CANCELLED)
            ):
                return status
            cancel_requested = status.cancel_requested
            effective = state
            if cancel_requested and effective in _CANCEL_FORCE:
                effective = JobState.CANCELLED
            updated = JobStatus(
                job_id=status.job_id,
                state=effective,
                job_type=status.job_type,
                tenant_id=status.tenant_id,
                auth_subject=status.auth_subject,
                result=result if result is not None else status.result,
                error=error if error is not None else status.error,
                retry_after=status.retry_after,
                created_at=status.created_at,
                updated_at=time.time(),
                cancel_requested=cancel_requested,
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
            if isinstance(data.get("idempotency_key"), str):
                stored["idempotency_key"] = str(data["idempotency_key"])
            if self._store_cas(stored, expected_updated_at=status.updated_at):
                final = self._load(job_id)
                return _status_from_dict(final) if final is not None else updated
        data = self._load(job_id)
        return _status_from_dict(data) if data is not None else None

    def cleanup_expired(self, *, older_than_seconds: float = 86400) -> int:
        # Prefer SCAN over KEYS to avoid blocking production Redis.
        removed = 0
        cutoff = time.time() - older_than_seconds
        for key_s in _iter_redis_keys(self._client, f"{self._prefix}*"):
            if ":idem:" in key_s:
                continue
            raw = self._decode(self._client.get(key_s))
            if raw is None:
                continue
            data = cast(dict[str, object], json.loads(raw))
            updated_at = float(cast(float | int | str, data.get("updated_at", 0)))
            state = str(data.get("state", ""))
            if updated_at < cutoff and state in {
                JobState.SUCCEEDED.value,
                JobState.FAILED.value,
                JobState.CANCELLED.value,
            }:
                job_id = str(data.get("job_id", ""))
                if job_id:
                    self.delete(job_id)
                else:
                    self._client.delete(key_s)
                removed += 1
        return removed


def _iter_redis_keys(client: object, pattern: str) -> list[str]:
    """Prefer SCAN; fall back to KEYS only for test stubs without scan."""
    scan_fn = getattr(client, "scan_iter", None)
    if callable(scan_fn):
        return [
            (k.decode("utf-8") if isinstance(k, bytes) else str(k))
            for k in cast(Iterable[Any], scan_fn(match=pattern))
        ]
    scan = getattr(client, "scan", None)
    if callable(scan):
        keys: list[str] = []
        cursor: int | bytes | str = 0
        while True:
            result = cast(tuple[Any, Iterable[Any]], scan(cursor=cursor, match=pattern, count=100))
            cursor, batch = result
            for key in batch:
                keys.append(key.decode("utf-8") if isinstance(key, bytes) else str(key))
            if cursor in {0, b"0", "0"}:
                break
        return keys
    keys_fn = getattr(client, "keys", None)
    if not callable(keys_fn):
        return []
    return [
        (k.decode("utf-8") if isinstance(k, bytes) else str(k))
        for k in cast(list[Any], keys_fn(pattern))
    ]
