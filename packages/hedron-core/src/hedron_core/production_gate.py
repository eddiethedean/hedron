"""Production / strict profile backend and security configuration gates."""

from __future__ import annotations

import os
import warnings
from collections.abc import Iterable

from hedron_core.cache import InMemoryCacheBackend, get_cache_backend
from hedron_core.compile_gate import is_production_env
from hedron_core.jobs import InMemoryJobBackend, get_job_backend

__all__ = [
    "DEFAULT_SESSION_SECRET_MARKERS",
    "MIN_SESSION_SECRET_LENGTH",
    "RISK_ACCEPTANCE_ENV",
    "assert_durable_backends",
    "assert_production_security_config",
    "parsed_risk_acceptance",
    "refuse_in_memory_backends",
]

RISK_ACCEPTANCE_ENV = "HEDRON_SECURITY_RISK_ACCEPTANCE"
# Match ``secrets.token_urlsafe(32)`` guidance used in first-party examples.
MIN_SESSION_SECRET_LENGTH = 32
DEFAULT_SESSION_SECRET_MARKERS = frozenset(
    {
        "hedron-dev-secret-change-me",
        "replace-in-production",
        "replace-me",
        "changeme",
        "change-me",
        "password",
        "secret",
        "dev",
        "dev-only",
        "test",
        "test-secret",
    }
)

# Stable risk codes for HEDRON_SECURITY_RISK_ACCEPTANCE (comma-separated).
RISK_WEAK_SECRET = "weak-session-secret"
RISK_DEVELOPMENT_PROFILE = "security-development"
RISK_EXPLORER_DEVELOPMENT = "explorer-development"
RISK_EXTERNAL_REDIRECTS = "external-redirects"
RISK_NO_CSP = "missing-csp"


def parsed_risk_acceptance(raw: str | None = None) -> frozenset[str]:
    """Parse ``HEDRON_SECURITY_RISK_ACCEPTANCE`` into normalized risk codes."""
    text = raw if raw is not None else os.environ.get(RISK_ACCEPTANCE_ENV, "")
    return frozenset(part.strip().lower() for part in text.split(",") if part.strip())


def refuse_in_memory_backends(*, jobs: bool = True, cache: bool = True) -> None:
    """Raise when process-local job/cache backends are active under production."""
    if jobs and isinstance(get_job_backend(), InMemoryJobBackend):
        from hedron_core.audit import SecurityAuditEventType, emit_security_audit

        emit_security_audit(
            SecurityAuditEventType.PRODUCTION_GATE_FAILED,
            "InMemoryJobBackend refused in production",
            attributes={"backend": "InMemoryJobBackend"},
        )
        raise RuntimeError(
            "InMemoryJobBackend is not allowed under HEDRON_ENV=production. "
            "Call set_job_backend(...) with Redis/Celery/RQ, or unset production "
            "for local demos."
        )
    if cache and isinstance(get_cache_backend(), InMemoryCacheBackend):
        from hedron_core.audit import SecurityAuditEventType, emit_security_audit

        emit_security_audit(
            SecurityAuditEventType.PRODUCTION_GATE_FAILED,
            "InMemoryCacheBackend refused in production",
            attributes={"backend": "InMemoryCacheBackend"},
        )
        raise RuntimeError(
            "InMemoryCacheBackend is not allowed under HEDRON_ENV=production. "
            "Call set_cache_backend(...) with an external store, or unset production "
            "for local demos."
        )


def assert_durable_backends(
    *,
    production: bool | None = None,
    strict_profile: bool = False,
) -> None:
    """Enforce durable backends in production; warn under strict-only profiles."""
    if is_production_env(production=production):
        refuse_in_memory_backends()
        return
    if strict_profile and (
        isinstance(get_job_backend(), InMemoryJobBackend)
        or isinstance(get_cache_backend(), InMemoryCacheBackend)
    ):
        warnings.warn(
            "security='strict' with in-memory job/cache backends is not multi-worker safe; "
            "configure set_job_backend / set_cache_backend before production.",
            UserWarning,
            stacklevel=3,
        )


def _is_weak_secret(secret: str) -> bool:
    lowered = secret.strip().lower()
    if not lowered:
        return True
    if len(lowered) < MIN_SESSION_SECRET_LENGTH:
        return True
    if lowered in DEFAULT_SESSION_SECRET_MARKERS:
        return True
    if "replace-in-production" in lowered or "change-me" in lowered:
        return True
    # Low-entropy: single character or all digits (#238).
    if len(set(lowered)) == 1:
        return True
    if lowered.isdigit():
        return True
    # Repeated denylist markers that only meet the length floor via repetition.
    for marker in DEFAULT_SESSION_SECRET_MARKERS:
        if not marker:
            continue
        if (
            len(lowered) >= len(marker)
            and len(lowered) % len(marker) == 0
            and marker * (len(lowered) // len(marker)) == lowered
        ):
            return True
    return False


def assert_production_security_config(
    *,
    production: bool | None = None,
    security_profile: str,
    session_secret: str | None,
    explorer_mode: str,
    allow_external_redirects: bool = False,
    content_security_policy: str | None = None,
    risk_acceptance: Iterable[str] | None = None,
) -> None:
    """Fail closed on insecure production configuration unless risks are accepted.

    Accepted risks are listed in ``HEDRON_SECURITY_RISK_ACCEPTANCE`` (or ``risk_acceptance``)
    as comma-separated codes: ``weak-session-secret``, ``security-development``,
    ``explorer-development``, ``external-redirects``, ``missing-csp``.
    """
    if not is_production_env(production=production):
        return

    accepted = (
        frozenset(code.strip().lower() for code in risk_acceptance if str(code).strip())
        if risk_acceptance is not None
        else parsed_risk_acceptance()
    )
    failures: list[tuple[str, str]] = []

    if session_secret is not None and _is_weak_secret(session_secret):
        failures.append(
            (
                RISK_WEAK_SECRET,
                "session_secret is missing, short, or a known development placeholder",
            )
        )
    if str(security_profile).lower() == "development":
        failures.append(
            (
                RISK_DEVELOPMENT_PROFILE,
                "security='development' is not allowed under HEDRON_ENV=production",
            )
        )
    if str(explorer_mode).lower() == "development":
        failures.append(
            (
                RISK_EXPLORER_DEVELOPMENT,
                "Explorer development mode must be off or secured in production",
            )
        )
    if allow_external_redirects:
        failures.append(
            (
                RISK_EXTERNAL_REDIRECTS,
                "allow_external_redirects=True requires explicit risk acceptance in production",
            )
        )
    if not content_security_policy:
        failures.append(
            (
                RISK_NO_CSP,
                "Content-Security-Policy is unset; set a profile CSP or accept missing-csp",
            )
        )

    blocked = [(code, msg) for code, msg in failures if code not in accepted]
    if not blocked:
        return

    from hedron_core.audit import SecurityAuditEventType, emit_security_audit

    detail = "; ".join(f"{code}: {msg}" for code, msg in blocked)
    emit_security_audit(
        SecurityAuditEventType.PRODUCTION_GATE_FAILED,
        "Production security configuration refused",
        attributes={"failures": [code for code, _ in blocked]},
    )
    accepted_hint = ",".join(sorted(code for code, _ in blocked))
    raise RuntimeError(
        f"Production security gate failed ({detail}). "
        f"Fix the configuration or set {RISK_ACCEPTANCE_ENV}={accepted_hint} "
        "to document explicit risk acceptance."
    )
