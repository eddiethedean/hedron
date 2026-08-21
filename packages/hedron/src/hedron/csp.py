"""CSP nonce helpers and bounded report ingestion (CSP-055)."""

from __future__ import annotations

import json
import secrets
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True, slots=True)
class CspReporting:
    """Optional CSP reporting configuration (beta)."""

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


def compose_csp(
    base: str | None,
    *,
    nonce: str | None,
    reporting: CspReporting | None = None,
) -> tuple[str | None, str | None]:
    """Return (enforcing CSP, report-only CSP)."""
    reporting = reporting or CspReporting()
    if reporting.mode == "off":
        return base, None
    parts: list[str] = []
    if base:
        parts.append(base.rstrip(";"))
    if nonce:
        parts.append(f"script-src 'nonce-{nonce}'")
        parts.append(f"style-src 'nonce-{nonce}'")
    if reporting.report_path:
        parts.append(f"report-uri {reporting.report_path}")
    if reporting.report_to:
        parts.append(f"report-to {reporting.report_to}")
    policy = "; ".join(parts) + ";"
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
    # Redact sensitive fields — never log document/blocked URLs raw in operators' dumps
    return {
        "effective_directive": str(
            report.get("effective-directive") or report.get("effectiveDirective") or ""
        )[:128],
        "violated_directive": str(
            report.get("violated-directive") or report.get("violatedDirective") or ""
        )[:128],
        "disposition": str(report.get("disposition") or "")[:32],
        "status_code": int(report["status-code"])
        if isinstance(report.get("status-code"), int)
        else None,
        "redacted": True,
    }
