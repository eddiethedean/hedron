"""Portable security policy profiles and response-header helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

from hedron_core.csrf_strategy import CsrfStrategy, DoubleSubmitCookieCsrf

SecurityProfileName = Literal["development", "standard", "strict"]
SecurityHeadersMode = bool | Literal["app"]


class SecurityProfile(StrEnum):
    DEVELOPMENT = "development"
    STANDARD = "standard"
    STRICT = "strict"


@dataclass(frozen=True, slots=True)
class SecurityHeadersPolicy:
    """Per-header overrides merged onto profile defaults (HEADERS-022).

    ``None`` on a field means unspecified — keep the profile/top-level default.
    Pass an empty string for ``content_security_policy`` to omit CSP.
    """

    content_security_policy: str | None = None
    frame_options: str | None = None
    content_type_options: str | None = None
    referrer_policy: str | None = None
    hsts_max_age: int | None = None


@dataclass(frozen=True, slots=True)
class SecurityPolicy:
    """Versioned security decisions shared by FastAPI, Flask, and Django adapters."""

    profile: SecurityProfile = SecurityProfile.STANDARD
    version: int = 1
    csrf_enabled: bool = True
    csrf_cookie_name: str = "hedron_csrf"
    csrf_header_name: str = "X-CSRF-Token"
    csrf_form_field: str = "csrf_token"
    # Strategies may hold callables (unhashable); exclude from policy equality/hash.
    csrf: CsrfStrategy | None = field(default=None, hash=False, compare=False)
    private_authenticated_cache: bool = True
    security_headers: SecurityHeadersMode | SecurityHeadersPolicy = True
    content_security_policy: str | None = None
    frame_options: str = "DENY"
    content_type_options: str = "nosniff"
    referrer_policy: str = "no-referrer"
    explorer_enabled: bool = False
    allow_external_redirects: bool = False
    # HTMX-020: inject hardened htmx-config on PAGE responses when True.
    htmx_browser_preset: bool = True
    # EVAL-020 / HDJ htmx.eval: allow js: on hx-vals / hx-headers (default deny).
    allow_htmx_eval: bool = False
    findings: tuple[str, ...] = field(default_factory=tuple)

    def resolve_csrf_strategy(self) -> CsrfStrategy | None:
        """Return the active CSRF strategy, or None when CSRF is disabled."""
        if not self.csrf_enabled:
            return None
        if self.csrf is not None:
            return self.csrf
        return DoubleSubmitCookieCsrf(
            cookie_name=self.csrf_cookie_name,
            form_field=self.csrf_form_field,
            header_name=self.csrf_header_name,
        )

    @classmethod
    def from_name(cls, name: SecurityProfileName | str | SecurityPolicy) -> SecurityPolicy:
        if isinstance(name, SecurityPolicy):
            return name
        profile = SecurityProfile(str(name).lower())
        if profile is SecurityProfile.DEVELOPMENT:
            return cls(
                profile=profile,
                csrf_enabled=True,
                security_headers=True,
                content_security_policy=None,
                explorer_enabled=True,
                # Softer HTMX history defaults than standard/strict (no history cache wipe).
                htmx_browser_preset=True,
                allow_htmx_eval=False,
                findings=(
                    "development profile: Explorer may be mounted; HTMX history cache allowed",
                ),
            )
        if profile is SecurityProfile.STRICT:
            return cls(
                profile=profile,
                csrf_enabled=True,
                security_headers=True,
                content_security_policy=(
                    "default-src 'self'; script-src 'self'; "
                    "style-src 'self'; "
                    "img-src 'self' data:; object-src 'none'; "
                    "base-uri 'self'; frame-ancestors 'none'"
                ),
                explorer_enabled=False,
                allow_external_redirects=False,
                htmx_browser_preset=True,
                allow_htmx_eval=False,
                findings=(
                    "strict profile: CSP, private caching, and HTMX history hardening enforced",
                ),
            )
        return cls(
            profile=SecurityProfile.STANDARD,
            csrf_enabled=True,
            security_headers=True,
            content_security_policy=(
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; object-src 'none'; base-uri 'self'"
            ),
            explorer_enabled=False,
            htmx_browser_preset=True,
            allow_htmx_eval=False,
            findings=(
                "standard profile: CSRF, private authenticated caching, and HTMX browser "
                "hardening enabled",
            ),
        )

    def htmx_config_json(self) -> str:
        """Return the JSON body for ``<meta name="htmx-config">`` for this profile."""
        # Shared secure floor for all presets when htmx_browser_preset is on.
        parts = [
            '"allowEval":false',
            '"allowScriptTags":false',
            '"historyRestoreAsHxRequest":false',
            '"includeIndicatorStyles":false',
            '"reportValidityOfForms":true',
            '"selfRequestsOnly":true',
        ]
        if self.profile is not SecurityProfile.DEVELOPMENT:
            parts.extend(
                [
                    '"historyEnabled":false',
                    '"historyCacheSize":0',
                ]
            )
        return "{" + ",".join(parts) + "}"

    def response_headers(self, *, authenticated: bool = False) -> dict[str, str]:
        headers: dict[str, str] = {}
        mode = self.security_headers
        if mode is False or mode == "app":
            pass
        elif isinstance(mode, SecurityHeadersPolicy):
            cto = (
                mode.content_type_options
                if mode.content_type_options is not None
                else self.content_type_options
            )
            frame = mode.frame_options if mode.frame_options is not None else self.frame_options
            referrer = (
                mode.referrer_policy if mode.referrer_policy is not None else self.referrer_policy
            )
            csp = (
                mode.content_security_policy
                if mode.content_security_policy is not None
                else self.content_security_policy
            )
            headers["X-Content-Type-Options"] = cto
            headers["X-Frame-Options"] = frame
            headers["Referrer-Policy"] = referrer
            if csp:
                headers["Content-Security-Policy"] = csp
            if mode.hsts_max_age is not None and mode.hsts_max_age >= 0:
                headers["Strict-Transport-Security"] = f"max-age={mode.hsts_max_age}"
        else:
            headers["X-Content-Type-Options"] = self.content_type_options
            headers["X-Frame-Options"] = self.frame_options
            headers["Referrer-Policy"] = self.referrer_policy
            if self.content_security_policy:
                headers["Content-Security-Policy"] = self.content_security_policy
        if authenticated and self.private_authenticated_cache:
            headers["Cache-Control"] = "private, no-store"
            headers["Pragma"] = "no-cache"
        return headers
