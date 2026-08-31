"""Idempotent / replay-safe action policies (REPLAY-055)."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass
from typing import Any, Literal, Protocol, cast

from hedron_core.compat import StrEnum


class ReplayState(StrEnum):
    FIRST = "first"
    REPLAYED = "replayed"
    CONFLICT = "conflict"
    IN_FLIGHT = "in_flight"


@dataclass(frozen=True, slots=True)
class IdempotencyPolicy:
    """Opt-in mutation replay policy (beta)."""

    mode: Literal["off", "optional", "required"] = "off"
    header_name: str = "Idempotency-Key"
    form_field: str = "idempotency_key"
    retention_seconds: int = 86_400
    policy_version: str = "1"


@dataclass(frozen=True, slots=True)
class ReplayOutcome:
    state: ReplayState
    key: str
    fingerprint: str
    cached_status: int | None = None
    cached_body: bytes | None = None
    cached_media_type: str | None = None
    cached_headers: tuple[tuple[str, str], ...] | None = None


class ReplayStore(Protocol):
    def claim(
        self,
        *,
        key: str,
        fingerprint: str,
        scope: str,
        retention_seconds: int,
    ) -> ReplayOutcome: ...

    def complete(
        self,
        *,
        key: str,
        scope: str,
        fingerprint: str,
        status: int,
        body: bytes,
        media_type: str | None = None,
        headers: tuple[tuple[str, str], ...] | None = None,
    ) -> bool: ...

    def abort(self, *, key: str, scope: str, fingerprint: str) -> None: ...


@dataclass
class _Entry:
    fingerprint: str
    status: int | None = None
    body: bytes | None = None
    media_type: str | None = None
    headers: tuple[tuple[str, str], ...] | None = None
    expires_at: float = 0.0
    in_flight: bool = True


class MemoryReplayStore:
    """Process-local replay store for tests and single-worker deployments."""

    def __init__(
        self,
        *,
        max_keys: int = 10_000,
        max_entry_bytes: int = 4 * 1024 * 1024,
        max_total_bytes: int = 64 * 1024 * 1024,
    ) -> None:
        if isinstance(max_keys, bool) or max_keys < 1:
            raise ValueError("max_keys must be positive")
        if isinstance(max_entry_bytes, bool) or max_entry_bytes < 1:
            raise ValueError("max_entry_bytes must be positive")
        if isinstance(max_total_bytes, bool) or max_total_bytes < 1:
            raise ValueError("max_total_bytes must be positive")
        if max_entry_bytes > max_total_bytes:
            raise ValueError("max_entry_bytes must be <= max_total_bytes")
        self._lock = threading.Lock()
        self._entries: dict[tuple[str, str], _Entry] = {}
        self._max_keys = max_keys
        self._max_entry_bytes = max_entry_bytes
        self._max_total_bytes = max_total_bytes
        self._total_bytes = 0

    @staticmethod
    def _text_bytes(value: str) -> int:
        return len(value.encode("utf-8"))

    @classmethod
    def _entry_bytes(cls, slot: tuple[str, str], entry: _Entry) -> int:
        scope, key = slot
        size = cls._text_bytes(scope) + cls._text_bytes(key) + cls._text_bytes(entry.fingerprint)
        if entry.body is not None:
            size += len(entry.body)
        if entry.media_type is not None:
            size += cls._text_bytes(entry.media_type)
        if entry.headers is not None:
            size += sum(
                cls._text_bytes(name) + cls._text_bytes(value) for name, value in entry.headers
            )
        return size

    def _remove(self, slot: tuple[str, str]) -> _Entry | None:
        entry = self._entries.pop(slot, None)
        if entry is not None:
            self._total_bytes -= self._entry_bytes(slot, entry)
        return entry

    def _purge(self, now: float) -> None:
        # Expire completed and abandoned in-flight claims past retention.
        expired = [k for k, v in self._entries.items() if v.expires_at <= now]
        for key in expired:
            self._remove(key)

    def claim(
        self,
        *,
        key: str,
        fingerprint: str,
        scope: str,
        retention_seconds: int,
    ) -> ReplayOutcome:
        now = time.monotonic()
        with self._lock:
            self._purge(now)
            slot = (scope, key)
            existing = self._entries.get(slot)
            if existing is None:
                if len(self._entries) >= self._max_keys:
                    raise RuntimeError("Replay store key budget exceeded")
                entry = _Entry(
                    fingerprint=fingerprint,
                    expires_at=now + retention_seconds,
                    in_flight=True,
                )
                entry_bytes = self._entry_bytes(slot, entry)
                if (
                    entry_bytes > self._max_entry_bytes
                    or self._total_bytes + entry_bytes > self._max_total_bytes
                ):
                    # Execute the request without retaining an unbounded claim.
                    return ReplayOutcome(
                        state=ReplayState.FIRST,
                        key=key,
                        fingerprint=fingerprint,
                    )
                self._entries[slot] = entry
                self._total_bytes += entry_bytes
                return ReplayOutcome(state=ReplayState.FIRST, key=key, fingerprint=fingerprint)
            if existing.fingerprint != fingerprint:
                return ReplayOutcome(state=ReplayState.CONFLICT, key=key, fingerprint=fingerprint)
            if existing.in_flight or existing.status is None:
                return ReplayOutcome(state=ReplayState.IN_FLIGHT, key=key, fingerprint=fingerprint)
            return ReplayOutcome(
                state=ReplayState.REPLAYED,
                key=key,
                fingerprint=fingerprint,
                cached_status=existing.status,
                cached_body=existing.body,
                cached_media_type=existing.media_type,
                cached_headers=existing.headers,
            )

    def complete(
        self,
        *,
        key: str,
        scope: str,
        fingerprint: str,
        status: int,
        body: bytes,
        media_type: str | None = None,
        headers: tuple[tuple[str, str], ...] | None = None,
    ) -> bool:
        with self._lock:
            slot = (scope, key)
            entry = self._entries.get(slot)
            if entry is None or entry.fingerprint != fingerprint:
                return False
            current_bytes = self._entry_bytes(slot, entry)
            completed = _Entry(
                fingerprint=entry.fingerprint,
                status=status,
                body=body,
                media_type=media_type or "text/html",
                headers=headers,
                expires_at=entry.expires_at,
                in_flight=False,
            )
            completed_bytes = self._entry_bytes(slot, completed)
            if completed_bytes > self._max_entry_bytes or (
                self._total_bytes - current_bytes + completed_bytes > self._max_total_bytes
            ):
                # Do not retain an in-flight claim that cannot be replayed;
                # callers still receive their original response, while a
                # retry can execute normally instead of seeing IN_FLIGHT.
                self._remove(slot)
                return False
            self._entries[slot] = completed
            self._total_bytes += completed_bytes - current_bytes
            return True

    def abort(self, *, key: str, scope: str, fingerprint: str) -> None:
        with self._lock:
            slot = (scope, key)
            entry = self._entries.get(slot)
            if entry is None or entry.fingerprint != fingerprint:
                return
            if entry.in_flight and entry.status is None:
                self._remove(slot)


def fingerprint_request(
    *,
    action_id: str,
    subject: str,
    tenant: str,
    inputs: dict[str, Any],
    policy_version: str,
) -> str:
    payload = {
        "action": action_id,
        "subject": subject,
        "tenant": tenant,
        "inputs": inputs,
        "policy": policy_version,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


async def extract_idempotency_key(request: Any, policy: IdempotencyPolicy) -> str | None:
    headers = getattr(request, "headers", {}) or {}
    key = headers.get(policy.header_name) or headers.get(policy.header_name.lower())
    if key:
        return str(key).strip() or None
    cached = getattr(getattr(request, "state", None), "hedron_idempotency_key", None)
    if cached:
        return str(cached).strip() or None
    # Prefer already-parsed CSRF form token path; otherwise parse multipart/urlencoded once.
    form = getattr(request, "_hedron_form", None)
    if not isinstance(form, dict):
        content_type = str(headers.get("content-type") or "")
        if (
            "multipart/form-data" in content_type
            or "application/x-www-form-urlencoded" in content_type
        ):
            try:
                parsed = await request.form()
                form = {str(k): parsed.get(k) for k in parsed}
                request._hedron_form = form  # type: ignore[attr-defined]
            except (RuntimeError, ValueError, TypeError, AttributeError, OSError):
                form = None
    if isinstance(form, dict) and policy.form_field in form:
        value: object = cast(dict[str, object], form)[policy.form_field]
        if hasattr(value, "read"):
            return None
        return str(value).strip() or None
    return None


def resolve_replay_store(request: Any) -> ReplayStore:
    app = getattr(request, "app", None)
    state = getattr(app, "state", None) if app is not None else None
    if state is not None and hasattr(state, "hedron_replay_store"):
        store = state.hedron_replay_store
        if store is None:
            from hedron_core.diagnostics import error

            raise error(
                "HED-REPLAY-0004",
                title="Replay store misconfigured",
                explanation="app.state.hedron_replay_store is explicitly None.",
                remediation=(
                    "Install a ReplayStore or omit the attribute for the default memory store."
                ),
            )
        return store
    if state is not None:
        state.hedron_replay_store = MemoryReplayStore()
        return state.hedron_replay_store
    return MemoryReplayStore()


def replay_scope(*, tenant: str, subject: str, action_id: str, session: str) -> str:
    # Unauthenticated callers share "anonymous" unless a session id is present.
    identity = subject if subject and subject != "anonymous" else f"anon:{session or 'none'}"
    return f"{tenant}:{identity}:{action_id}"


__all__ = [
    "IdempotencyPolicy",
    "MemoryReplayStore",
    "ReplayOutcome",
    "ReplayState",
    "ReplayStore",
    "digest_bytes",
    "extract_idempotency_key",
    "fingerprint_request",
    "replay_scope",
    "resolve_replay_store",
]
