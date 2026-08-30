"""Immutable request-local security context (CTX-056)."""

from __future__ import annotations

import contextvars
import hashlib
import hmac
import json
import math
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import Any, cast

_current_security_context: contextvars.ContextVar[SecurityContext | None] = contextvars.ContextVar(
    "hedron_security_context", default=None
)

# Fields allowed when serializing across jobs/caches/MCP/background work.
_SERIALIZABLE_FIELDS = frozenset(
    {
        "version",
        "application_id",
        "subject_id",
        "tenant_id",
        "scopes",
        "auth_level",
        "profile_name",
        "policy_version",
        "correlation_id",
        "fingerprint",
    }
)
_AUTHENTICATED_FIELDS = frozenset(
    {"schema_version", "key_id", "audience", "issued_at", "expires_at", "context", "signature"}
)
_MAX_CONTEXT_BYTES = 64 * 1024
_MAX_STRING_LENGTH = 4096
_MAX_SCOPES = 128
_MAX_SCOPE_LENGTH = 256


class SecurityContextError(ValueError):
    """Raised when a security context is missing, stale, broadened, or foreign."""


@dataclass(frozen=True, slots=True)
class SecurityContext:
    """Request-bound authority that may only narrow."""

    version: int = 1
    application_id: str = ""
    subject_id: str = ""
    tenant_id: str = ""
    scopes: frozenset[str] = field(default_factory=frozenset[str])
    auth_level: int = 0
    profile_name: str = "standard"
    policy_version: int = 1
    correlation_id: str = ""
    fingerprint: str = ""

    def __post_init__(self) -> None:
        expected = self.compute_fingerprint()
        if self.fingerprint and not hmac.compare_digest(self.fingerprint, expected):
            raise SecurityContextError("stale or tampered security context fingerprint")
        object.__setattr__(self, "fingerprint", expected)

    def compute_fingerprint(self) -> str:
        payload = {
            "version": self.version,
            "application_id": self.application_id,
            "subject_id": self.subject_id,
            "tenant_id": self.tenant_id,
            "scopes": sorted(self.scopes),
            "auth_level": self.auth_level,
            "profile_name": self.profile_name,
            "policy_version": self.policy_version,
            "correlation_id": self.correlation_id,
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return digest[:32]

    def narrow(
        self,
        *,
        scopes: frozenset[str] | None = None,
        auth_level: int | None = None,
        subject_id: str | None = None,
        tenant_id: str | None = None,
    ) -> SecurityContext:
        """Return a context that never broadens authority."""
        next_scopes = self.scopes if scopes is None else (scopes & self.scopes)
        next_auth = self.auth_level if auth_level is None else min(auth_level, self.auth_level)
        if subject_id is not None:
            if self.subject_id and subject_id != self.subject_id:
                raise SecurityContextError("subject_id cannot change during narrowing")
            if not self.subject_id and subject_id:
                raise SecurityContextError("subject_id cannot be introduced during narrowing")
            next_subject = self.subject_id
        else:
            next_subject = self.subject_id
        if tenant_id is not None:
            if self.tenant_id and tenant_id != self.tenant_id:
                raise SecurityContextError("tenant_id cannot change during narrowing")
            if not self.tenant_id and tenant_id:
                raise SecurityContextError("tenant_id cannot be introduced during narrowing")
            next_tenant = self.tenant_id
        else:
            next_tenant = self.tenant_id
        if next_auth > self.auth_level:
            raise SecurityContextError("auth_level cannot increase")
        if scopes is not None and not scopes <= self.scopes:
            raise SecurityContextError("scopes cannot broaden")
        return replace(
            self,
            scopes=next_scopes,
            auth_level=next_auth,
            subject_id=next_subject,
            tenant_id=next_tenant,
            fingerprint="",
        )

    def bind_identity(
        self,
        *,
        subject_id: str | None = None,
        tenant_id: str | None = None,
    ) -> SecurityContext:
        """Bind empty identity fields once; never overwrite an existing identity."""
        next_subject = self.subject_id
        next_tenant = self.tenant_id
        if subject_id is not None:
            if self.subject_id and subject_id != self.subject_id:
                raise SecurityContextError("subject_id already bound")
            next_subject = subject_id
        if tenant_id is not None:
            if self.tenant_id and tenant_id != self.tenant_id:
                raise SecurityContextError("tenant_id already bound")
            next_tenant = tenant_id
        return replace(self, subject_id=next_subject, tenant_id=next_tenant, fingerprint="")

    def to_serializable(self) -> dict[str, Any]:
        """Return the local canonical payload used inside a signed envelope.

        This method is retained for local compatibility and for
        :meth:`to_authenticated`. It is not an authorization token: never
        send this unsigned mapping across a process, job, cache, MCP, or client
        boundary. Use :meth:`to_authenticated` and verify with
        :meth:`from_authenticated` instead.
        """
        data = {
            "version": self.version,
            "application_id": self.application_id,
            "subject_id": self.subject_id,
            "tenant_id": self.tenant_id,
            "scopes": sorted(self.scopes),
            "auth_level": self.auth_level,
            "profile_name": self.profile_name,
            "policy_version": self.policy_version,
            "correlation_id": self.correlation_id,
            "fingerprint": self.fingerprint or self.compute_fingerprint(),
        }
        return {k: v for k, v in data.items() if k in _SERIALIZABLE_FIELDS}

    def to_authenticated(
        self,
        secret: str | bytes,
        *,
        key_id: str = "default",
        audience: str = "hedron",
        ttl_seconds: int = 300,
        now: float | None = None,
    ) -> dict[str, Any]:
        """Serialize this context in an authenticated, short-lived envelope.

        ``to_serializable`` remains as a local compatibility representation. Any
        context crossing a process, job, cache, MCP, or client boundary should use
        this method and :meth:`from_authenticated`.
        """
        key = _secret_bytes(secret)
        if not key:
            raise SecurityContextError("security context signing secret is required")
        if type(key_id) is not str or not key_id or len(key_id) > 128:
            raise SecurityContextError("invalid security context key_id")
        if type(audience) is not str or not audience or len(audience) > _MAX_STRING_LENGTH:
            raise SecurityContextError("invalid security context audience")
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= 86_400:
            raise SecurityContextError("ttl_seconds must be between 1 and 86400")
        timestamp: Any = time.time() if now is None else now
        if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
            raise SecurityContextError("security context clock must be a finite number")
        if not math.isfinite(float(timestamp)):
            raise SecurityContextError("security context clock must be a finite number")
        issued_at = int(timestamp)
        envelope: dict[str, Any] = {
            "schema_version": 1,
            "key_id": key_id,
            "audience": audience,
            "issued_at": issued_at,
            "expires_at": issued_at + ttl_seconds,
            "context": self.to_serializable(),
        }
        envelope["signature"] = _sign_envelope(envelope, key)
        return envelope

    @classmethod
    def from_serializable(
        cls,
        payload: Mapping[str, Any],
        *,
        expected_application_id: str | None = None,
    ) -> SecurityContext:
        """Restore a local payload after an already-authenticated handoff.

        Callers handling untrusted or cross-process data must use
        :meth:`from_authenticated`; this parser validates shape and the
        context fingerprint but does not authenticate the sender.
        """
        _validate_payload_size(payload)
        unknown = set(payload) - _SERIALIZABLE_FIELDS
        if unknown:
            raise SecurityContextError(f"foreign security context fields: {sorted(unknown)}")
        required = ("version", "application_id", "fingerprint")
        missing = [key for key in required if key not in payload]
        if missing:
            raise SecurityContextError(f"missing security context fields: {missing}")
        expected_fp = _bounded_string(payload.get("fingerprint", ""), "fingerprint").strip()
        if not expected_fp:
            raise SecurityContextError("missing security context fingerprint")
        app_id = _bounded_string(payload.get("application_id", ""), "application_id")
        if expected_application_id is not None and app_id != expected_application_id:
            raise SecurityContextError("foreign application security context")
        scopes_raw = payload.get("scopes", ())
        if isinstance(scopes_raw, (str, bytes)):
            raise SecurityContextError("scopes must be a sequence of strings")
        if scopes_raw is None:
            scopes: frozenset[str] = frozenset[str]()
        elif isinstance(scopes_raw, Sequence):
            if len(cast(Sequence[Any], scopes_raw)) > _MAX_SCOPES:
                raise SecurityContextError("too many security context scopes")
            values: list[str] = []
            for item in cast(Sequence[object], scopes_raw):
                if not isinstance(item, str) or len(item) > _MAX_SCOPE_LENGTH:
                    raise SecurityContextError("security context scopes must be bounded strings")
                values.append(item)
            scopes = frozenset(values)
        else:
            raise SecurityContextError("scopes must be a sequence of strings")
        ctx = cls(
            version=_bounded_int(payload.get("version", 1), "version", minimum=1),
            application_id=app_id,
            subject_id=_bounded_string(payload.get("subject_id", ""), "subject_id"),
            tenant_id=_bounded_string(payload.get("tenant_id", ""), "tenant_id"),
            scopes=scopes,
            auth_level=_bounded_int(payload.get("auth_level", 0), "auth_level"),
            profile_name=_bounded_string(payload.get("profile_name", "standard"), "profile_name"),
            policy_version=_bounded_int(payload.get("policy_version", 1), "policy_version"),
            correlation_id=_bounded_string(payload.get("correlation_id", ""), "correlation_id"),
            fingerprint="",
        )
        if not hmac.compare_digest(expected_fp, ctx.fingerprint):
            raise SecurityContextError("stale or tampered security context fingerprint")
        return ctx

    @classmethod
    def from_authenticated(
        cls,
        payload: Mapping[str, Any],
        *,
        secret: str | bytes,
        expected_application_id: str | None = None,
        expected_audience: str = "hedron",
        now: float | None = None,
        clock_skew_seconds: int = 30,
    ) -> SecurityContext:
        """Restore a context only after verifying its signed envelope and expiry."""
        raw_clock_skew: Any = clock_skew_seconds
        if (
            isinstance(raw_clock_skew, bool)
            or not isinstance(raw_clock_skew, int)
            or not 0 <= raw_clock_skew <= 3600
        ):
            raise SecurityContextError("clock_skew_seconds must be between 0 and 3600")
        _validate_payload_size(payload)
        if frozenset(payload) != _AUTHENTICATED_FIELDS:
            raise SecurityContextError("invalid security context envelope fields")
        key = _secret_bytes(secret)
        if not key:
            raise SecurityContextError("security context verification secret is required")
        key_id = payload.get("key_id")
        audience = payload.get("audience")
        issued_at = payload.get("issued_at")
        expires_at = payload.get("expires_at")
        signature = payload.get("signature")
        context = payload.get("context")
        if (
            not isinstance(key_id, str)
            or not key_id
            or not isinstance(audience, str)
            or audience != expected_audience
            or not isinstance(signature, str)
            or not isinstance(context, Mapping)
        ):
            raise SecurityContextError("malformed security context envelope")
        key_id = _bounded_string(key_id, "key_id")
        audience = _bounded_string(audience, "audience")
        issued_at = _bounded_int(issued_at, "issued_at", maximum=2**63 - 1)
        expires_at = _bounded_int(expires_at, "expires_at", maximum=2**63 - 1)
        if len(key_id) > 128 or len(signature) != 64:
            raise SecurityContextError("oversized security context envelope field")
        if expires_at <= issued_at or expires_at - issued_at > 86_400:
            raise SecurityContextError("invalid security context lifetime")
        timestamp: Any = time.time() if now is None else now
        if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
            raise SecurityContextError("security context clock must be a finite number")
        if not math.isfinite(float(timestamp)):
            raise SecurityContextError("security context clock must be a finite number")
        current = int(timestamp)
        if issued_at > current + clock_skew_seconds or expires_at < current - clock_skew_seconds:
            raise SecurityContextError("expired or not-yet-valid security context")
        unsigned = {key: value for key, value in payload.items() if key != "signature"}
        expected_signature = _sign_envelope(unsigned, key)
        if not hmac.compare_digest(signature, expected_signature):
            raise SecurityContextError("invalid security context signature")
        return cls.from_serializable(
            cast(Mapping[str, Any], context),
            expected_application_id=expected_application_id,
        )


def _secret_bytes(secret: str | bytes) -> bytes:
    if type(secret) is str:
        return secret.encode("utf-8")
    if type(secret) is bytes:
        return secret
    raise SecurityContextError("security context secret must be str or bytes")


def _bounded_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or len(value) > _MAX_STRING_LENGTH:
        raise SecurityContextError(f"security context {field_name} must be a bounded string")
    return value


def _bounded_int(
    value: object,
    field_name: str,
    *,
    minimum: int = 0,
    maximum: int = 2**31 - 1,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise SecurityContextError(f"security context {field_name} must be a bounded integer")
    return value


def _validate_payload_size(payload: Mapping[str, Any]) -> None:
    if not hasattr(payload, "items"):
        raise SecurityContextError("security context payload must be an object")
    try:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise SecurityContextError("security context payload is not JSON-compatible") from exc
    if len(encoded.encode("utf-8")) > _MAX_CONTEXT_BYTES:
        raise SecurityContextError("security context payload is too large")


def _sign_envelope(payload: Mapping[str, Any], secret: bytes) -> str:
    try:
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise SecurityContextError("security context payload is not JSON-compatible") from exc
    return hmac.new(secret, encoded, hashlib.sha256).hexdigest()


def get_security_context() -> SecurityContext | None:
    return _current_security_context.get()


def set_security_context(ctx: SecurityContext | None) -> contextvars.Token[SecurityContext | None]:
    return _current_security_context.set(ctx)


def reset_security_context(token: contextvars.Token[SecurityContext | None]) -> None:
    _current_security_context.reset(token)


def require_security_context() -> SecurityContext:
    ctx = get_security_context()
    if ctx is None:
        raise SecurityContextError("security context missing")
    return ctx
