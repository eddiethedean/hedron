"""Durable job backend protocol and in-memory / Redis implementations."""

from __future__ import annotations

import json
import secrets
import threading
import time
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Protocol, cast, runtime_checkable

from hedron_core.typing_aliases import JobStatusDict, JsonValue

if TYPE_CHECKING:
    from hedron_core.interaction import InteractionResult

__all__ = [
    "InMemoryJobBackend",
    "JobBackend",
    "JobHandle",
    "JobState",
    "JobStatus",
    "RedisJobBackend",
    "get_job_backend",
    "job_authorized",
    "job_authorized_http",
    "job_status_interaction",
    "reset_jobs_for_tests",
    "set_job_backend",
]


class JobState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Brief poll while the idempotency winner's job body becomes visible under Redis lag.
_IDEMPOTENCY_WINNER_POLL_ATTEMPTS = 5
_IDEMPOTENCY_WINNER_POLL_SECONDS = 0.01


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


@runtime_checkable
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


def job_authorized(
    status: JobStatus,
    *,
    auth_subject: str | None = None,
    tenant_id: str | None = None,
) -> bool:
    """Return True when caller credentials exactly match the job's auth/tenant scope.

    Each dimension is compared for equality (including ``None``). A tenant-only job
    (``auth_subject=None``) does **not** authorize an arbitrary subject in that tenant —
    the caller must also pass ``auth_subject=None``. Unscoped jobs authorize only when
    the caller likewise omits both scopes — use :func:`job_authorized_http` for HTTP
    observers (unscoped jobs are never HTTP-readable).
    """
    return status.auth_subject == auth_subject and status.tenant_id == tenant_id


def job_authorized_http(
    status: JobStatus,
    *,
    auth_subject: str | None = None,
    tenant_id: str | None = None,
) -> bool:
    """Authorize job observation over HTTP (fail closed for unscoped jobs).

    Jobs without stored scope are never readable via HTTP helpers. Callers must
    supply credentials that **exactly** match every scope dimension on the job
    (including ``None`` on unset dimensions).
    """
    if status.auth_subject is None and status.tenant_id is None:
        return False
    if auth_subject is None and tenant_id is None:
        return False
    return job_authorized(status, auth_subject=auth_subject, tenant_id=tenant_id)


def _idempotency_scope_key(
    idempotency_key: str,
    *,
    tenant_id: str | None,
    auth_subject: str | None,
) -> str:
    # JSON preserves the distinction between an omitted scope and an explicit
    # empty-string scope, while also avoiding delimiter collisions in user input.
    return json.dumps([tenant_id, auth_subject, idempotency_key], separators=(",", ":"))


def _legacy_idempotency_scope_key(
    idempotency_key: str,
    *,
    tenant_id: str | None,
    auth_subject: str | None,
) -> str:
    """Return the pre-0.29 scope format for safe rolling-upgrade reads."""
    return f"{tenant_id or ''}\x1f{auth_subject or ''}\x1f{idempotency_key}"


@dataclass
class _JobRecord:
    status: JobStatus
    payload: dict[str, JsonValue] = field(default_factory=dict)
    idempotency_key: str | None = None
    idempotency_scope_key: str | None = None


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _status_from_dict(data: Mapping[str, object]) -> JobStatus:
    return JobStatus(
        job_id=str(data["job_id"]),
        state=JobState(str(data["state"])),
        job_type=str(data["job_type"]),
        tenant_id=_optional_str(data.get("tenant_id")),
        auth_subject=_optional_str(data.get("auth_subject")),
        result=data.get("result"),
        error=_optional_str(data.get("error")),
        retry_after=int(cast(int | float | str, data.get("retry_after", 2))),
        created_at=float(cast(int | float | str, data.get("created_at", 0))),
        updated_at=float(cast(int | float | str, data.get("updated_at", 0))),
        cancel_requested=bool(data.get("cancel_requested", False)),
    )


def _status_to_dict(
    status: JobStatus,
    *,
    payload: Mapping[str, JsonValue] | None = None,
) -> JobStatusDict:
    data: JobStatusDict = {
        "job_id": status.job_id,
        "state": status.state.value,
        "job_type": status.job_type,
        "tenant_id": status.tenant_id,
        "auth_subject": status.auth_subject,
        "result": status.result,
        "error": status.error,
        "retry_after": status.retry_after,
        "created_at": status.created_at,
        "updated_at": status.updated_at,
        "cancel_requested": status.cancel_requested,
    }
    if payload is not None:
        data["payload"] = dict(payload)
    return data


class InMemoryJobBackend:
    def __init__(self) -> None:
        self._jobs: dict[str, _JobRecord] = {}
        self._idempotency: dict[str, str] = {}
        self._lock = threading.RLock()

    def submit(
        self,
        job_type: str,
        payload: Mapping[str, JsonValue],
        *,
        idempotency_key: str | None = None,
        tenant_id: str | None = None,
        auth_subject: str | None = None,
    ) -> JobHandle:
        with self._lock:
            scoped: str | None = None
            if idempotency_key:
                scoped = _idempotency_scope_key(
                    idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
                )
                legacy_scoped = _legacy_idempotency_scope_key(
                    idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
                )
                matched_scope = scoped
                existing_id = self._idempotency.get(scoped)
                if existing_id is None and legacy_scoped != scoped:
                    matched_scope = legacy_scoped
                    existing_id = self._idempotency.get(legacy_scoped)
                if existing_id is not None:
                    existing = self._jobs.get(existing_id)
                    if existing is not None:
                        if job_authorized(
                            existing.status, auth_subject=auth_subject, tenant_id=tenant_id
                        ):
                            return JobHandle(job_id=existing_id, idempotency_key=idempotency_key)
                        raise PermissionError("Idempotency key is already bound to another scope")
                    # The pointed-to job expired or was removed, so reclaim the key.
                    del self._idempotency[matched_scope]
            job_id = secrets.token_urlsafe(16)
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
            self._jobs[job_id] = _JobRecord(
                status=status,
                payload=dict(payload),
                idempotency_key=idempotency_key,
                idempotency_scope_key=scoped,
            )
            if scoped is not None:
                self._idempotency[scoped] = job_id
            return JobHandle(job_id=job_id, idempotency_key=idempotency_key)

    def get(
        self,
        job_id: str,
        *,
        auth_subject: str | None = None,
        tenant_id: str | None = None,
    ) -> JobStatus | None:
        with self._lock:
            rec = self._jobs.get(job_id)
            if rec is None:
                return None
            # Unrestricted read when caller omits both scope kwargs (internal/workers).
            # HTTP helpers must pass credentials and call job_authorized explicitly, or
            # pass matching kwargs here to filter.
            if auth_subject is None and tenant_id is None:
                return rec.status
            if not job_authorized(rec.status, auth_subject=auth_subject, tenant_id=tenant_id):
                return None
            return rec.status

    def request_cancel(
        self,
        job_id: str,
        *,
        auth_subject: str | None = None,
        tenant_id: str | None = None,
    ) -> bool:
        with self._lock:
            rec = self._jobs.get(job_id)
            if rec is None:
                return False
            st = rec.status
            if not job_authorized(st, auth_subject=auth_subject, tenant_id=tenant_id):
                return False
            if st.state in {JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED}:
                return False
            rec.status = JobStatus(
                job_id=st.job_id,
                state=JobState.CANCELLED if st.state == JobState.QUEUED else st.state,
                job_type=st.job_type,
                tenant_id=st.tenant_id,
                auth_subject=st.auth_subject,
                result=st.result,
                error=st.error,
                retry_after=st.retry_after,
                created_at=st.created_at,
                updated_at=time.time(),
                cancel_requested=True,
            )
            return True

    def cleanup_expired(self, *, older_than_seconds: float = 86400) -> int:
        cutoff = time.time() - older_than_seconds
        removed = 0
        with self._lock:
            for job_id, rec in list(self._jobs.items()):
                if rec.status.updated_at < cutoff and rec.status.state in {
                    JobState.SUCCEEDED,
                    JobState.FAILED,
                    JobState.CANCELLED,
                }:
                    del self._jobs[job_id]
                    scoped = rec.idempotency_scope_key
                    if scoped and self._idempotency.get(scoped) == job_id:
                        del self._idempotency[scoped]
                    removed += 1
        return removed

    def mark(
        self,
        job_id: str,
        state: JobState,
        *,
        result: object = None,
        error: str | None = None,
    ) -> JobStatus | None:
        terminal = frozenset({JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED})
        cancel_force = frozenset({JobState.RUNNING, JobState.SUCCEEDED, JobState.FAILED})
        with self._lock:
            rec = self._jobs.get(job_id)
            if rec is None:
                return None
            st = rec.status
            if st.state in terminal and state not in terminal:
                return st
            if (
                st.state in terminal
                and state in terminal
                and state is not st.state
                and not (st.cancel_requested and state is JobState.CANCELLED)
            ):
                return st
            effective = state
            if st.cancel_requested and effective in cancel_force:
                effective = JobState.CANCELLED
            rec.status = JobStatus(
                job_id=st.job_id,
                state=effective,
                job_type=st.job_type,
                tenant_id=st.tenant_id,
                auth_subject=st.auth_subject,
                result=result if result is not None else st.result,
                error=error if error is not None else st.error,
                retry_after=st.retry_after,
                created_at=st.created_at,
                updated_at=time.time(),
                cancel_requested=st.cancel_requested,
            )
            return rec.status


class RedisJobBackend:
    """Redis-backed JobBackend using JSON values and shared idempotency keys."""

    def __init__(
        self, client: RedisClient, *, prefix: str = "h1:job:", ttl_seconds: int = 86400
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
        tenant_id: str | None = None,
        auth_subject: str | None = None,
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
        loaded = json.loads(raw)
        return cast(dict[str, object], loaded)

    def _store(self, data: Mapping[str, object]) -> None:
        self._client.set(
            self._key(str(data["job_id"])),
            json.dumps(data, default=str, separators=(",", ":")),
            ex=self._ttl,
        )

    def _store_cas(self, data: Mapping[str, object], *, expected_updated_at: float) -> bool:
        """Compare-and-swap store when Redis WATCH/pipeline is available."""
        key = self._key(str(data["job_id"]))
        pipeline_factory = getattr(self._client, "pipeline", None)
        if not callable(pipeline_factory):
            raise RuntimeError(
                "RedisJobBackend requires a client with pipeline()/WATCH for CAS; "
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
                "RedisJobBackend requires redis.exceptions.WatchError for CAS; "
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
                if current.get("cancel_requested"):
                    merged["cancel_requested"] = True
                if merged.get("cancel_requested") and merged.get("state") in {
                    JobState.RUNNING.value,
                    JobState.SUCCEEDED.value,
                    JobState.FAILED.value,
                }:
                    merged["state"] = JobState.CANCELLED.value
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
            legacy_scoped = _legacy_idempotency_scope_key(
                idempotency_key, tenant_id=tenant_id, auth_subject=auth_subject
            )
            legacy_redis_key = f"{self._prefix}idem:{legacy_scoped}"
            for candidate_key in (idem_redis_key, legacy_redis_key):
                existing = self._decode(self._client.get(candidate_key))
                if existing is None:
                    continue
                loaded = self._load(existing)
                if loaded is not None:
                    status = _status_from_dict(loaded)
                    if job_authorized(status, auth_subject=auth_subject, tenant_id=tenant_id):
                        return JobHandle(job_id=existing, idempotency_key=idempotency_key)
                    raise PermissionError("Idempotency key is already bound to another scope")
                # The pointed-to job expired or was removed, so reclaim the key.
                self._client.delete(candidate_key)

        job_id = secrets.token_urlsafe(16)
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
                # Another worker won; drop our orphan and return their handle.
                self._client.delete(self._key(job_id))
                existing = self._decode(self._client.get(idem_redis_key))
                if existing is not None:
                    for _ in range(_IDEMPOTENCY_WINNER_POLL_ATTEMPTS):
                        loaded = self._load(existing)
                        if loaded is not None:
                            return JobHandle(job_id=existing, idempotency_key=idempotency_key)
                        time.sleep(_IDEMPOTENCY_WINNER_POLL_SECONDS)
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
            if not job_authorized(status, auth_subject=auth_subject, tenant_id=tenant_id):
                return False
            if status.state in {JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED}:
                return False
            updated = JobStatus(
                job_id=status.job_id,
                state=JobState.CANCELLED if status.state == JobState.QUEUED else status.state,
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
            raw_payload = data.get("payload")
            payload: dict[str, JsonValue] = (
                cast(dict[str, JsonValue], raw_payload) if isinstance(raw_payload, dict) else {}
            )
            stored = _status_to_dict(updated, payload=payload)
            if isinstance(data.get("idempotency_key"), str):
                stored["idempotency_key"] = str(data["idempotency_key"])
            if isinstance(data.get("idempotency_scope_key"), str):
                stored["idempotency_scope_key"] = str(data["idempotency_scope_key"])
            if self._store_cas(stored, expected_updated_at=status.updated_at):
                return True
        return False

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
            status = _status_from_dict(data)
            if status.updated_at < cutoff and status.state in {
                JobState.SUCCEEDED,
                JobState.FAILED,
                JobState.CANCELLED,
            }:
                self._client.delete(key_s)
                scope = data.get("idempotency_scope_key")
                if isinstance(scope, str) and scope:
                    self._client.delete(f"{self._prefix}idem:{scope}")
                else:
                    idem = data.get("idempotency_key")
                    if isinstance(idem, str) and idem:
                        self._client.delete(
                            self._idem_key(
                                idem,
                                tenant_id=status.tenant_id,
                                auth_subject=status.auth_subject,
                            )
                        )
                removed += 1
        return removed

    def mark(
        self,
        job_id: str,
        state: JobState,
        *,
        result: object = None,
        error: str | None = None,
    ) -> JobStatus | None:
        terminal = frozenset({JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED})
        for _ in range(5):
            data = self._load(job_id)
            if data is None:
                return None
            status = _status_from_dict(data)
            # Refuse transitions out of terminal states.
            if status.state in terminal and state not in terminal:
                return status
            if (
                status.state in terminal
                and state in terminal
                and state is not status.state
                and not (status.cancel_requested and state is JobState.CANCELLED)
            ):
                return status
            cancel_requested = status.cancel_requested
            effective = state
            if cancel_requested and effective in {
                JobState.RUNNING,
                JobState.SUCCEEDED,
                JobState.FAILED,
            }:
                effective = JobState.CANCELLED
            # Refuse to clear a cancel request via a non-cancel terminal overwrite from a
            # stale worker snapshot — keep cancel_requested sticky.
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
            raw_payload = data.get("payload")
            payload: dict[str, JsonValue] = (
                cast(dict[str, JsonValue], raw_payload) if isinstance(raw_payload, dict) else {}
            )
            stored = _status_to_dict(updated, payload=payload)
            if isinstance(data.get("idempotency_key"), str):
                stored["idempotency_key"] = str(data["idempotency_key"])
            if isinstance(data.get("idempotency_scope_key"), str):
                stored["idempotency_scope_key"] = str(data["idempotency_scope_key"])
            if self._store_cas(stored, expected_updated_at=status.updated_at):
                final = self._load(job_id)
                return _status_from_dict(final) if final is not None else updated
        # Contended beyond retries — return latest known status without blind overwrite.
        data = self._load(job_id)
        return _status_from_dict(data) if data is not None else None


def _iter_redis_keys(client: object, pattern: str) -> list[str]:
    """Prefer SCAN; fall back to KEYS only for test stubs without scan."""
    scan_fn = getattr(client, "scan_iter", None)
    if callable(scan_fn):
        return [
            (k.decode("utf-8") if isinstance(k, bytes) else str(k))
            for k in cast(Iterable[object], scan_fn(match=pattern))
        ]
    scan = getattr(client, "scan", None)
    if callable(scan):
        keys: list[str] = []
        cursor: int | bytes | str = 0
        while True:
            result = cast(
                tuple[Any, Iterable[object]], scan(cursor=cursor, match=pattern, count=100)
            )
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
        for k in cast(Iterable[object], keys_fn(pattern))
    ]


_backend: JobBackend = InMemoryJobBackend()


def get_job_backend() -> JobBackend:
    return _backend


def set_job_backend(backend: JobBackend) -> None:
    import logging

    from hedron_core.compile_gate import is_production_env

    if is_production_env() and isinstance(backend, InMemoryJobBackend):
        from hedron_core.audit import SecurityAuditEventType, emit_security_audit

        emit_security_audit(
            SecurityAuditEventType.PRODUCTION_GATE_FAILED,
            "InMemoryJobBackend refused in production",
            attributes={"backend": "InMemoryJobBackend", "via": "set_job_backend"},
        )
        raise RuntimeError(
            "InMemoryJobBackend is not allowed under HEDRON_ENV=production. "
            "Call set_job_backend(...) with Redis/Celery/RQ, or unset production "
            "for local demos."
        )
    global _backend
    _backend = backend
    if isinstance(backend, InMemoryJobBackend) and not is_production_env():
        logging.getLogger("hedron.jobs").warning(
            "InMemoryJobBackend does not span processes; use Redis/Celery/RQ "
            "(set_job_backend) for multi-worker deployments. Refused automatically "
            "under HEDRON_ENV=production."
        )
    if is_production_env():
        from hedron_core.production_gate import assert_durable_backends

        assert_durable_backends(production=True)


def reset_jobs_for_tests() -> None:
    global _backend
    _backend = InMemoryJobBackend()


def job_status_interaction(status: JobStatus) -> InteractionResult:
    """Portable 202 InteractionResult with Retry-After and accessible polling UI."""
    from hedron_core.builtins import Status
    from hedron_core.interaction import InteractionResult

    label = f"Job {status.job_id}: {status.state.value}"
    content = Status(label, tone="info", live=True)
    return InteractionResult(
        content=content,
        status_code=202,
        cache="no-store",
        headers={"Retry-After": str(status.retry_after)},
        explanation=(
            "Bounded polling job status (SSE observation available via job_status_sse_events)"
        ),
    )
