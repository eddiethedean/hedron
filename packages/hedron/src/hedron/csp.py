"""CSP nonce helpers and bounded report ingestion (CSP-055)."""

from __future__ import annotations

import json
import random
import secrets
from dataclasses import dataclass, field
from typing import Any, Literal

__all__ = [
    "CspReporting",
    "NonceContext",
    "bind_nonce",
    "compose_csp",
    "ingest_csp_report",
    "new_nonce",
    "nonce_for_request",
]


@dataclass(frozen=True, slots=True)
class CspReporting:
    """Optional CSP reporting configuration (beta).

    These helpers compose policy strings and redact reports. Apps must opt in to
    managed headers; Hedron does not auto-author CSP for every response.
    """

    mode: Literal["off", "report-only", "enforcing"] = "off"
    report_path: str = "/hedron/csp-report"
    report_to: str | None = None
    max_body_bytes: int = 8_192
    sample_rate: float = 1.0


@dataclass(slots=True)
class NonceContext:
    """Request-scoped nonce; never reuse across requests."""

    value: str = field(default_factory=lambda: secrets.token_urlsafe(16))

    def attr(self) -> str:
        return self.value


def new_nonce() -> NonceContext:
    return NonceContext()


def bind_nonce(request: Any, nonce: NonceContext | None = None) -> NonceContext:
    ctx = nonce or new_nonce()
    scope = getattr(request, "state", None)
    if scope is not None:
        scope.hedron_csp_nonce = ctx.value
    return ctx


def nonce_for_request(request: Any) -> str | None:
    scope = getattr(request, "state", None)
    if scope is None:
        return None
    value = getattr(scope, "hedron_csp_nonce", None)
    return str(value) if value else None


def _directive_map(policy: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in policy.split(";"):
        chunk = part.strip()
        if not chunk:
            continue
        name, _, rest = chunk.partition(" ")
        key = name.lower()
        if key in out:
            # Merge source lists for duplicate directives.
            out[key] = f"{out[key]} {rest}".strip()
        else:
            out[key] = rest.strip()
    return out


def _format_policy(directives: dict[str, str]) -> str:
    parts = [f"{name} {value}".strip() if value else name for name, value in directives.items()]
    return "; ".join(parts) + ";"


def compose_csp(
    base: str | None,
    *,
    nonce: str | None,
    reporting: CspReporting | None = None,
) -> tuple[str | None, str | None]:
    """Return (enforcing CSP, report-only CSP).

    Nonces are merged into existing ``script-src`` / ``style-src`` directives
    instead of appending duplicate directive names.
    """
    reporting = reporting or CspReporting()
    if reporting.mode == "off":
        return base, None
    directives = _directive_map(base or "")
    if nonce:
        token = f"'nonce-{nonce}'"
        for name in ("script-src", "style-src"):
            existing = directives.get(name, "")
            if token not in existing:
                directives[name] = f"{existing} {token}".strip() or token
    if reporting.report_path:
        directives["report-uri"] = reporting.report_path
    if reporting.report_to:
        directives["report-to"] = reporting.report_to
    policy = _format_policy(directives)
    if reporting.mode == "report-only":
        return base, policy
    return policy, None


def ingest_csp_report(
    body: bytes,
    *,
    content_type: str | None,
    reporting: CspReporting | None = None,
) -> dict[str, Any] | None:
    """Parse and redact a CSP violation report. Never mutates policy."""
    reporting = reporting or CspReporting()
    if reporting.sample_rate < 1.0:
        rate = max(0.0, min(1.0, reporting.sample_rate))
        if random.random() > rate:
            return None
    if len(body) > reporting.max_body_bytes:
        return None
    ctype = (content_type or "").split(";", 1)[0].strip().lower()
    if ctype not in {
        "application/csp-report",
        "application/json",
        "application/reports+json",
    }:
        return None
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    report = payload.get("csp-report") if isinstance(payload, dict) else None
    if not isinstance(report, dict):
        report = payload if isinstance(payload, dict) else {}
    status_raw = report.get("status-code", report.get("statusCode"))
    status_code: int | None
    try:
        status_code = int(status_raw) if status_raw is not None else None
    except (TypeError, ValueError):
        status_code = None
    return {
        "effective_directive": str(
            report.get("effective-directive") or report.get("effectiveDirective") or ""
        )[:128],
        "violated_directive": str(
            report.get("violated-directive") or report.get("violatedDirective") or ""
        )[:128],
        "disposition": str(report.get("disposition") or "")[:32],
        "status_code": status_code,
        "redacted": True,
    }
