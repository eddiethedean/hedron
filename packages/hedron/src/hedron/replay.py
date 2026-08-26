"""Idempotent / replay-safe action policies (REPLAY-055)."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal, Protocol


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
    ) -> bool: ...

    def abort(self, *, key: str, scope: str, fingerprint: str) -> None: ...


@dataclass
class _Entry:
    fingerprint: str
    status: int | None = None
    body: bytes | None = None
    media_type: str | None = None
    expires_at: float = 0.0
    in_flight: bool = True


class MemoryReplayStore:
    """Process-local replay store for tests and single-worker deployments."""

    def __init__(self, *, max_keys: int = 10_000) -> None:
        self._lock = threading.Lock()
        self._entries: dict[tuple[str, str], _Entry] = {}
        self._max_keys = max_keys

    def _purge(self, now: float) -> None:
        # Expire completed and abandoned in-flight claims past retention.
        expired = [k for k, v in self._entries.items() if v.expires_at <= now]
        for key in expired:
            self._entries.pop(key, None)

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
                self._entries[slot] = _Entry(
                    fingerprint=fingerprint,
                    expires_at=now + retention_seconds,
                    in_flight=True,
                )
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
    ) -> bool:
        with self._lock:
            slot = (scope, key)
            entry = self._entries.get(slot)
            if entry is None or entry.fingerprint != fingerprint:
                return False
            entry.in_flight = False
            entry.status = status
            entry.body = body
            entry.media_type = media_type or "text/html"
            return True

    def abort(self, *, key: str, scope: str, fingerprint: str) -> None:
        with self._lock:
            slot = (scope, key)
            entry = self._entries.get(slot)
            if entry is None or entry.fingerprint != fingerprint:
                return
            if entry.in_flight and entry.status is None:
                self._entries.pop(slot, None)


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
        value = form[policy.form_field]
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
