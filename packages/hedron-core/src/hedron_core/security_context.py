"""Immutable request-local security context (CTX-056)."""

from __future__ import annotations

import contextvars
import hashlib
import hmac
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import Any

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


class SecurityContextError(ValueError):
    """Raised when a security context is missing, stale, broadened, or foreign."""


@dataclass(frozen=True, slots=True)
class SecurityContext:
    """Request-bound authority that may only narrow."""

    version: int = 1
    application_id: str = ""
    subject_id: str = ""
    tenant_id: str = ""
    scopes: frozenset[str] = field(default_factory=frozenset)
    auth_level: int = 0
    profile_name: str = "standard"
    policy_version: int = 1
    correlation_id: str = ""
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if not self.fingerprint:
            object.__setattr__(self, "fingerprint", self.compute_fingerprint())

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

    @classmethod
    def from_serializable(
        cls,
        payload: Mapping[str, Any],
        *,
        expected_application_id: str | None = None,
    ) -> SecurityContext:
        if not isinstance(payload, Mapping):
            raise SecurityContextError("security context payload must be a mapping")
        unknown = set(payload) - _SERIALIZABLE_FIELDS
        if unknown:
            raise SecurityContextError(f"foreign security context fields: {sorted(unknown)}")
        required = ("version", "application_id", "fingerprint")
        missing = [key for key in required if key not in payload]
        if missing:
            raise SecurityContextError(f"missing security context fields: {missing}")
        expected_fp = str(payload.get("fingerprint", "")).strip()
        if not expected_fp:
            raise SecurityContextError("missing security context fingerprint")
        app_id = str(payload.get("application_id", ""))
        if expected_application_id is not None and app_id != expected_application_id:
            raise SecurityContextError("foreign application security context")
        scopes_raw = payload.get("scopes", ())
        if isinstance(scopes_raw, (str, bytes)):
            raise SecurityContextError("scopes must be a sequence of strings")
        if scopes_raw is None:
            scopes: frozenset[str] = frozenset()
        elif isinstance(scopes_raw, Sequence):
            scopes = frozenset(str(item) for item in scopes_raw)
        else:
            raise SecurityContextError("scopes must be a sequence of strings")
        ctx = cls(
            version=int(payload.get("version", 1)),
            application_id=app_id,
            subject_id=str(payload.get("subject_id", "")),
            tenant_id=str(payload.get("tenant_id", "")),
            scopes=scopes,
            auth_level=int(payload.get("auth_level", 0)),
            profile_name=str(payload.get("profile_name", "standard")),
            policy_version=int(payload.get("policy_version", 1)),
            correlation_id=str(payload.get("correlation_id", "")),
            fingerprint="",
        )
        if not hmac.compare_digest(expected_fp, ctx.fingerprint):
            raise SecurityContextError("stale or tampered security context fingerprint")
        return ctx


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
