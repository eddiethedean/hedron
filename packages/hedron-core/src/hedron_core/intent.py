"""Signing keyring and short-lived signed action intents (INTENT-056)."""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import secrets
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol, cast

from hedron_core.compat import StrEnum


class IntentState(StrEnum):
    MINTED = "minted"
    CLAIMED = "claimed"
    CONSUMED = "consumed"
    EXPIRED = "expired"
    REJECTED = "rejected"


class IntentError(ValueError):
    """Raised when an intent is missing, stale, substituted, or already used."""


@dataclass(frozen=True, slots=True)
class KeyRecord:
    key_id: str
    purpose: str
    secret: bytes
    status: str = "active"  # active | verify_only | revoked
    not_before: float = 0.0
    not_after: float = 0.0


class SecurityKeyring:
    """Purpose-bound key lifecycle with bounded verification overlap."""

    def __init__(self) -> None:
        self._keys: dict[str, KeyRecord] = {}
        self._lock = threading.Lock()

    def add(self, record: KeyRecord) -> None:
        with self._lock:
            self._keys[record.key_id] = record

    def mint_key(
        self,
        *,
        key_id: str | None = None,
        purpose: str = "intent",
        secret: bytes | None = None,
    ) -> KeyRecord:
        record = KeyRecord(
            key_id=key_id or secrets.token_hex(8),
            purpose=purpose,
            secret=secret or secrets.token_bytes(32),
            status="active",
        )
        self.add(record)
        return record

    def rotate(self, key_id: str, *, successor: KeyRecord) -> None:
        with self._lock:
            current = self._keys.get(key_id)
            if current is None:
                raise IntentError(f"unknown key {key_id!r}")
            self._keys[key_id] = KeyRecord(
                key_id=current.key_id,
                purpose=current.purpose,
                secret=current.secret,
                status="verify_only",
                not_before=current.not_before,
                not_after=current.not_after,
            )
            self._keys[successor.key_id] = successor

    def revoke(self, key_id: str) -> None:
        with self._lock:
            current = self._keys.get(key_id)
            if current is None:
                raise IntentError(f"unknown key {key_id!r}")
            self._keys[key_id] = KeyRecord(
                key_id=current.key_id,
                purpose=current.purpose,
                secret=current.secret,
                status="revoked",
                not_before=current.not_before,
                not_after=current.not_after,
            )

    def _window_ok(self, record: KeyRecord, *, now: float) -> bool:
        try:
            finite = all(
                not isinstance(value, bool) and math.isfinite(value)
                for value in (now, record.not_before, record.not_after)
            )
        except TypeError:
            return False
        if not finite:
            return False
        if record.not_before and now < record.not_before:
            return False
        return not (record.not_after and now > record.not_after)

    def get_for_mint(self, purpose: str = "intent", *, now: float | None = None) -> KeyRecord:
        ts = time.time() if now is None else now
        with self._lock:
            for record in self._keys.values():
                if (
                    record.purpose == purpose
                    and record.status == "active"
                    and self._window_ok(record, now=ts)
                ):
                    return record
        raise IntentError(f"no active mint key for purpose {purpose!r}")

    def get_for_verify(
        self, key_id: str, purpose: str = "intent", *, now: float | None = None
    ) -> KeyRecord:
        ts = time.time() if now is None else now
        with self._lock:
            record = self._keys.get(key_id)
        if record is None:
            raise IntentError(f"unknown key {key_id!r}")
        if record.purpose != purpose:
            raise IntentError("key purpose mismatch")
        if record.status == "revoked":
            raise IntentError("key revoked")
        if record.status not in {"active", "verify_only"}:
            raise IntentError("key not usable for verify")
        if not self._window_ok(record, now=ts):
            raise IntentError("key outside validity window")
        return record


@dataclass(frozen=True, slots=True)
class SignedIntent:
    version: int
    intent_id: str
    key_id: str
    actor: str
    tenant: str
    action: str
    method: str
    resource: str
    revision: str
    payload_fingerprint: str
    target: str
    expires_at: float
    signature: str

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "intent_id": self.intent_id,
            "key_id": self.key_id,
            "actor": self.actor,
            "tenant": self.tenant,
            "action": self.action,
            "method": self.method,
            "resource": self.resource,
            "revision": self.revision,
            "payload_fingerprint": self.payload_fingerprint,
            "target": self.target,
            "expires_at": self.expires_at,
        }


def fingerprint_payload(payload: Mapping[str, Any] | None) -> str:
    body = json.dumps(payload or {}, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:32]


def _sign(secret: bytes, canonical: Mapping[str, Any]) -> str:
    message = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def mint_intent(
    *,
    keyring: SecurityKeyring,
    actor: str,
    tenant: str,
    action: str,
    method: str,
    resource: str,
    revision: str,
    target: str,
    payload: Mapping[str, Any] | None = None,
    ttl_seconds: object = 300.0,
    now: object | None = None,
    store: IntentStore | None = None,
) -> SignedIntent:
    ts = time.time() if now is None else now
    if (
        isinstance(ts, bool)
        or not isinstance(ts, (int, float))
        or not math.isfinite(ts)
        or isinstance(ttl_seconds, bool)
        or not isinstance(ttl_seconds, (int, float))
        or not math.isfinite(ttl_seconds)
        or ttl_seconds < 0
    ):
        raise ValueError("now and ttl_seconds must be finite, with ttl_seconds >= 0")
    ts = float(ts)
    ttl_seconds = float(ttl_seconds)
    key = keyring.get_for_mint("intent", now=ts)
    intent_id = secrets.token_hex(16)
    payload_fp = fingerprint_payload(payload)
    expires_at = ts + ttl_seconds
    canonical = {
        "version": 1,
        "intent_id": intent_id,
        "key_id": key.key_id,
        "actor": actor,
        "tenant": tenant,
        "action": action,
        "method": method.upper(),
        "resource": resource,
        "revision": revision,
        "payload_fingerprint": payload_fp,
        "target": target,
        "expires_at": expires_at,
    }
    signature = _sign(key.secret, canonical)
    intent = SignedIntent(
        version=1,
        intent_id=intent_id,
        key_id=key.key_id,
        actor=actor,
        tenant=tenant,
        action=action,
        method=method.upper(),
        resource=resource,
        revision=revision,
        payload_fingerprint=payload_fp,
        target=target,
        expires_at=expires_at,
        signature=signature,
    )
    if store is not None:
        store.put_minted(intent.intent_id)
    return intent


def verify_intent(
    intent: SignedIntent,
    *,
    keyring: SecurityKeyring,
    actor: str,
    tenant: str,
    action: str,
    method: str,
    resource: str,
    revision: str,
    target: str,
    payload: Mapping[str, Any] | None = None,
    now: object | None = None,
) -> None:
    ts = time.time() if now is None else now
    expires_at = cast(object, intent.expires_at)
    if (
        isinstance(ts, bool)
        or not isinstance(ts, (int, float))
        or not math.isfinite(ts)
        or isinstance(expires_at, bool)
        or not isinstance(expires_at, (int, float))
        or not math.isfinite(expires_at)
    ):
        raise IntentError("intent timestamp invalid")
    if float(ts) > float(expires_at):
        raise IntentError("intent expired")
    key = keyring.get_for_verify(intent.key_id, "intent", now=ts)
    expected_sig = _sign(key.secret, intent.canonical_payload())
    if not hmac.compare_digest(expected_sig, intent.signature):
        raise IntentError("intent signature invalid")
    checks = {
        "actor": (intent.actor, actor),
        "tenant": (intent.tenant, tenant),
        "action": (intent.action, action),
        "method": (intent.method, method.upper()),
        "resource": (intent.resource, resource),
        "revision": (intent.revision, revision),
        "target": (intent.target, target),
        "payload_fingerprint": (intent.payload_fingerprint, fingerprint_payload(payload)),
    }
    for _name, (left, right) in checks.items():
        if left != right:
            # Fail closed without disclosing which field mismatched to clients.
            raise IntentError("intent binding mismatch")


def verify_and_consume(
    intent: SignedIntent,
    *,
    keyring: SecurityKeyring,
    store: IntentStore,
    actor: str,
    tenant: str,
    action: str,
    method: str,
    resource: str,
    revision: str,
    target: str,
    payload: Mapping[str, Any] | None = None,
    now: float | None = None,
) -> None:
    """Verify bindings then atomically consume the intent (single-use)."""
    verify_intent(
        intent,
        keyring=keyring,
        actor=actor,
        tenant=tenant,
        action=action,
        method=method,
        resource=resource,
        revision=revision,
        target=target,
        payload=payload,
        now=now,
    )
    store.consume(intent.intent_id)


class IntentStore(Protocol):
    def put_minted(self, intent_id: str) -> None: ...

    def claim(self, intent_id: str) -> IntentState: ...

    def consume(self, intent_id: str) -> IntentState: ...

    def get(self, intent_id: str) -> IntentState | None: ...


class MemoryIntentStore:
    """Process-local intent store with atomic claim/consume."""

    def __init__(self) -> None:
        self._states: dict[str, IntentState] = {}
        self._lock = threading.Lock()

    def put_minted(self, intent_id: str) -> None:
        with self._lock:
            self._states[intent_id] = IntentState.MINTED

    def claim(self, intent_id: str) -> IntentState:
        with self._lock:
            state = self._states.get(intent_id)
            if state is None:
                raise IntentError("intent missing")
            if state is IntentState.CONSUMED:
                raise IntentError("intent already consumed")
            if state is IntentState.CLAIMED:
                raise IntentError("intent already claimed")
            if state is IntentState.EXPIRED:
                raise IntentError("intent expired")
            self._states[intent_id] = IntentState.CLAIMED
            return IntentState.CLAIMED

    def consume(self, intent_id: str) -> IntentState:
        with self._lock:
            state = self._states.get(intent_id)
            if state is None:
                raise IntentError("intent missing")
            if state is IntentState.CONSUMED:
                raise IntentError("intent already consumed")
            if state not in {IntentState.MINTED, IntentState.CLAIMED}:
                raise IntentError("intent not consumable")
            self._states[intent_id] = IntentState.CONSUMED
            return IntentState.CONSUMED

    def get(self, intent_id: str) -> IntentState | None:
        with self._lock:
            return self._states.get(intent_id)
