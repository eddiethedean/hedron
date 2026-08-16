"""Shared Redis status store for Celery/RQ JobBackend bridges (phase 0.13)."""

from __future__ import annotations

import json
import secrets
import time
from collections.abc import Iterable, Mapping
from typing import Any, cast

from hedron_core.jobs.auth import job_authorized
from hedron_core.jobs.backend import RedisClient, RedisPipeline
from hedron_core.jobs.codec import (
    _idempotency_scope_key,
    _legacy_idempotency_scope_key,
    _status_from_dict,
    _status_to_dict,
)
from hedron_core.jobs.types import JobHandle, JobState, JobStatus
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "CELERY_ENQUEUE_FAILED",
    "ENQUEUE_FAILED_ERRORS",
    "RQ_ENQUEUE_FAILED",
    "RedisStatusStore",
    "require_redis_status_client",
]

# Broker never accepted the task — reclaimable under the same idempotency key (#199).
CELERY_ENQUEUE_FAILED = "Celery enqueue failed"
RQ_ENQUEUE_FAILED = "RQ enqueue failed"
ENQUEUE_FAILED_ERRORS = frozenset({CELERY_ENQUEUE_FAILED, RQ_ENQUEUE_FAILED})

_TERMINAL = frozenset({JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED})
_CANCEL_FORCE = frozenset({JobState.RUNNING, JobState.SUCCEEDED, JobState.FAILED})

# Atomic owner check + delete for idempotency pointers (#236 / #269).
_COMPARE_AND_DELETE_LUA = (
    "if redis.call('get', KEYS[1]) == ARGV[1] then "
    "return redis.call('del', KEYS[1]) else return 0 end"
)


def _decode_redis(raw: bytes | str | None) -> str | None:
    if raw is None:
        return None
    if isinstance(raw, bytes):
        return raw.decode("utf-8")
    return str(raw)


def _watch_error_type() -> type[BaseException]:
    try:
        from redis.exceptions import WatchError as _WatchError  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "RedisStatusStore requires redis.exceptions.WatchError for CAS; "
            "install redis-py or use a client with WATCH support."
        ) from exc
    return _WatchError


def _compare_and_delete_if_owner(client: RedisClient, key: str, expected: str) -> bool:
    """Delete ``key`` only when it still equals ``expected``.

    Prefer Lua ``EVAL`` (atomic GET+DEL). Without ``eval``, WATCH/MULTI +
    ``pipeline.delete``. Never GET-then-DELETE (#236 / #269).
    """
    eval_fn = getattr(client, "eval", None)
    if callable(eval_fn):
        result = eval_fn(_COMPARE_AND_DELETE_LUA, 1, key, expected)
        return bool(result) and result != 0

    pipeline_factory = getattr(client, "pipeline", None)
    if not callable(pipeline_factory):
        raise RuntimeError("idempotency compare-and-delete requires Redis EVAL or a WATCH pipeline")
    watch_error = _watch_error_type()
    pipe = cast(RedisPipeline, pipeline_factory())
    deleter = getattr(pipe, "delete", None)
    if not callable(deleter):
        raise RuntimeError(
            "idempotency compare-and-delete requires pipeline.delete when EVAL is unavailable"
        )
    for _ in range(8):
        try:
            pipe.watch(key)
            pointed = _decode_redis(pipe.get(key) if hasattr(pipe, "get") else client.get(key))
            if pointed != expected:
                pipe.unwatch()
                return False
            pipe.multi()
            deleter(key)
            pipe.execute()
            return True
        except Exception as exc:
            if isinstance(exc, watch_error):
                continue
            raise
    return False


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
        return _decode_redis(raw)

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

    def _idem_redis_key_from_data(self, data: Mapping[str, object]) -> str | None:
        scope = data.get("idempotency_scope_key")
        if isinstance(scope, str) and scope:
            return f"{self._prefix}idem:{scope}"
        return None

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

        Refreshes the associated idempotency key TTL in the same transaction so
        long-running jobs cannot outlive the write-once idempotency TTL (#210).
        """
        job_id = str(data["job_id"])
        key = self._key(job_id)
        idem_key = self._idem_redis_key_from_data(data)
        pipeline_factory = getattr(self._client, "pipeline", None)
        if not callable(pipeline_factory):
            raise RuntimeError(
                "RedisStatusStore requires a client with pipeline()/WATCH for CAS; "
                "blind overwrite is not allowed for production job state."
            )
        pipe = cast(RedisPipeline, pipeline_factory())
        watch_error = _watch_error_type()
        for _ in range(8):
            try:
                pipe.watch(key)
                if idem_key is not None:
                    pipe.watch(idem_key)
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
                refresh_idem = False
                if idem_key is not None:
                    pointed = self._decode(
                        pipe.get(idem_key) if hasattr(pipe, "get") else self._client.get(idem_key)
                    )
                    # Refresh when we still own the key, or recreate when TTL skew
                    # expired it while the job body remains (#210).
                    refresh_idem = pointed is None or pointed == job_id
                pipe.multi()
                pipe.set(
                    key,
                    json.dumps(merged, default=str, separators=(",", ":")),
                    ex=self._ttl,
                )
                if idem_key is not None and refresh_idem:
                    pipe.set(idem_key, job_id, ex=self._ttl)
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
        self._release_idempotency_pointer(job_id, data)

    def release_idempotency(self, job_id: str) -> None:
        """Drop the idempotency pointer if it still names ``job_id`` (keep the job body)."""
        data = self._load(job_id)
        if data is None:
            return
        self._release_idempotency_pointer(job_id, data)

    def _release_idempotency_pointer(self, job_id: str, data: Mapping[str, object]) -> None:
        """Drop the idempotency pointer only when it still names ``job_id``.

        Uses atomic compare-and-delete so a concurrent submit cannot lose a
        newer claim (#198 / #236 / #269).
        """
        idem_key = self._idem_redis_key_from_data(data)
        if idem_key is None:
            idem = data.get("idempotency_key")
            if isinstance(idem, str) and idem:
                status = _status_from_dict(data)
                idem_key = self._idem_key(
                    idem,
                    tenant_id=status.tenant_id,
                    auth_subject=status.auth_subject,
                )
            else:
                return
        _compare_and_delete_if_owner(self._client, idem_key, job_id)

    def mark_enqueue_failed(self, job_id: str, *, error: str) -> JobStatus | None:
        """Mark FAILED for a broker enqueue miss and reclaim the idempotency key (#199)."""
        status = self.mark(job_id, JobState.FAILED, error=error)
        self.release_idempotency(job_id)
        return status

    def submit(
        self,
        job_type: str,
        payload: Mapping[str, JsonValue],
        *,
        idempotency_key: str | None = None,
        tenant_id: str | None = None,
        auth_subject: str | None = None,
    ) -> tuple[JobHandle, bool]:
        """Persist a queued job; return ``(handle, created)``.

        ``created`` is ``False`` on an idempotency replay so broker bridges can
        skip re-enqueue and avoid marking a live job failed.

        Jobs that never reached the broker (``ENQUEUE_FAILED_ERRORS``) release the
        idempotency key so a later submit can create a fresh job (#199).
        """
        idem_redis_key: str | None = None
        if idempotency_key:
            idem_redis_key = self._idem_key(
                idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
            )
            legacy_scoped = _legacy_idempotency_scope_key(
                idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
            )
            legacy_redis_key = f"{self._prefix}idem:{legacy_scoped}"
            # Mirror RedisJobBackend: honor new + legacy keys; fail closed on
            # cross-scope pointers instead of reclaiming them (#145 / #146).
            for candidate_key in (idem_redis_key, legacy_redis_key):
                existing_raw = self._decode(self._client.get(candidate_key))
                if existing_raw is None:
                    continue
                loaded = self._load(existing_raw)
                if loaded is not None:
                    status = _status_from_dict(loaded)
                    if not job_authorized(status, auth_subject=auth_subject, tenant_id=tenant_id):
                        raise PermissionError("Idempotency key is already bound to another scope")
                    if status.state is JobState.FAILED and status.error in ENQUEUE_FAILED_ERRORS:
                        # Heal pre-fix stuck pointers: broker never accepted the task.
                        self.release_idempotency(status.job_id)
                        # Legacy pointers are not owned by release_idempotency().
                        _compare_and_delete_if_owner(self._client, candidate_key, existing_raw)
                        continue
                    return (
                        JobHandle(job_id=status.job_id, idempotency_key=idempotency_key),
                        False,
                    )
                # The pointed-to job expired or was removed, so reclaim the key
                # only if we still own it (concurrent SET NX may have claimed it).
                _compare_and_delete_if_owner(self._client, candidate_key, existing_raw)

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
                            return (
                                JobHandle(job_id=existing, idempotency_key=idempotency_key),
                                False,
                            )
                        time.sleep(0.01)
                    if self._load(existing) is not None:
                        return (
                            JobHandle(job_id=existing, idempotency_key=idempotency_key),
                            False,
                        )
                raise RuntimeError(
                    "Idempotent job submit lost the race and the winner record is unavailable"
                )

        return JobHandle(job_id=job_id, idempotency_key=idempotency_key), True

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
