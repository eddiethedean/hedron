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
    ) -> None: ...


@dataclass
class _Entry:
    fingerprint: str
    status: int | None = None
    body: bytes | None = None
    expires_at: float = 0.0
    in_flight: bool = True


class MemoryReplayStore:
    """Process-local replay store for tests and single-worker deployments."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._entries: dict[tuple[str, str], _Entry] = {}

    def _purge(self, now: float) -> None:
        expired = [k for k, v in self._entries.items() if v.expires_at <= now and not v.in_flight]
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
            )

    def complete(
        self,
        *,
        key: str,
        scope: str,
        fingerprint: str,
        status: int,
        body: bytes,
    ) -> None:
        with self._lock:
            slot = (scope, key)
            entry = self._entries.get(slot)
            if entry is None or entry.fingerprint != fingerprint:
                return
            entry.in_flight = False
            entry.status = status
            entry.body = body


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


def extract_idempotency_key(request: Any, policy: IdempotencyPolicy) -> str | None:
    headers = getattr(request, "headers", {}) or {}
    key = headers.get(policy.header_name) or headers.get(policy.header_name.lower())
    if key:
        return str(key).strip() or None
    form = getattr(request, "_hedron_form", None)
    if isinstance(form, dict) and policy.form_field in form:
        value = form[policy.form_field]
        return str(value).strip() or None
    return None


def resolve_replay_store(request: Any) -> ReplayStore:
    app = getattr(request, "app", None)
    state = getattr(app, "state", None) if app is not None else None
    store = getattr(state, "hedron_replay_store", None) if state is not None else None
    if store is not None:
        return store
    # Lazy default for single-process apps/tests
    if state is not None and not hasattr(state, "hedron_replay_store"):
        state.hedron_replay_store = MemoryReplayStore()
        return state.hedron_replay_store
    return MemoryReplayStore()
