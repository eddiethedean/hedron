"""Portable security policy profiles and response-header helpers."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any, Literal

from hedron_core.compat import StrEnum
from hedron_core.csrf_strategy import (
    DEFAULT_CSRF_COOKIE_NAME,
    DEFAULT_CSRF_FORM_FIELD,
    DEFAULT_CSRF_HEADER_NAME,
    CsrfStrategy,
    DoubleSubmitCookieCsrf,
)
from hedron_core.request_budget import RequestBudgetLimits

# Avoid circular import of EgressPolicy at type-check time by using Any for optional policy.


def _policy_field_values_without_csrf(policy: SecurityPolicy) -> tuple[Any, ...]:
    """Field values for equality/hash excluding the ``csrf`` strategy object."""
    return tuple(
        (f.name, getattr(policy, f.name)) for f in fields(policy) if f.name != "csrf" and f.compare
    )


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
    Pass an empty string to omit that header (including CSP, frame, CTO, referrer).
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
    # Compatibility seeds for the default DoubleSubmitCookieCsrf when ``csrf`` is None.
    # Active names are owned by ``resolve_csrf_strategy()``.
    csrf_cookie_name: str = DEFAULT_CSRF_COOKIE_NAME
    csrf_header_name: str = DEFAULT_CSRF_HEADER_NAME
    csrf_form_field: str = DEFAULT_CSRF_FORM_FIELD
    # Strategies may hold callables; equality uses _csrf_identity() below.
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
    # 0.56 control-plane composition knobs (compat with SecurityPolicy.from_name presets).
    control_plane_version: int = 1
    conformance_profile_version: str = "hedron-security-1"
    intent_required: bool = False
    posture_strict: bool = False
    request_budget_limits: RequestBudgetLimits | None = None
    egress_allow_hosts: frozenset[str] = field(default_factory=frozenset)
    egress_deny_by_default: bool = True

    @staticmethod
    def _csrf_identity(strategy: CsrfStrategy | None) -> tuple[object, ...]:
        """Stable identity so distinct strategies never compare equal."""
        if strategy is None:
            return ("none",)
        form_field = getattr(strategy, "form_field", "")
        header_name = getattr(strategy, "header_name", "")
        cookie_name = getattr(strategy, "cookie_name", None)
        get_expected = getattr(strategy, "get_expected", None)
        return (
            type(strategy).__name__,
            form_field,
            header_name,
            cookie_name,
            id(get_expected) if get_expected is not None else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SecurityPolicy):
            return NotImplemented
        if _policy_field_values_without_csrf(self) != _policy_field_values_without_csrf(other):
            return False
        return self._csrf_identity(self.csrf) == self._csrf_identity(other.csrf)

    def __hash__(self) -> int:
        return hash((_policy_field_values_without_csrf(self), self._csrf_identity(self.csrf)))

    def resolve_csrf_strategy(self) -> CsrfStrategy | None:
        """Return the active CSRF strategy, or None when CSRF is disabled.

        Cookie/header/field names are owned by the strategy. Policy name fields
        exist only to construct the default double-submit strategy.
        """
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
                intent_required=True,
                posture_strict=True,
                request_budget_limits=RequestBudgetLimits(),
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
            request_budget_limits=RequestBudgetLimits(),
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
        # Host owns all headers — including authenticated cache — when False/"app".
        if mode is False or mode == "app":
            return headers
        if isinstance(mode, SecurityHeadersPolicy):
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
            if cto:
                headers["X-Content-Type-Options"] = cto
            if frame:
                headers["X-Frame-Options"] = frame
            if referrer:
                headers["Referrer-Policy"] = referrer
            if csp:
                headers["Content-Security-Policy"] = csp
            if mode.hsts_max_age is not None and mode.hsts_max_age >= 0:
                headers["Strict-Transport-Security"] = f"max-age={mode.hsts_max_age}"
        else:
            if self.content_type_options:
                headers["X-Content-Type-Options"] = self.content_type_options
            if self.frame_options:
                headers["X-Frame-Options"] = self.frame_options
            if self.referrer_policy:
                headers["Referrer-Policy"] = self.referrer_policy
            if self.content_security_policy:
                headers["Content-Security-Policy"] = self.content_security_policy
        if authenticated and self.private_authenticated_cache:
            headers["Cache-Control"] = "private, no-store"
            headers["Pragma"] = "no-cache"
        return headers
