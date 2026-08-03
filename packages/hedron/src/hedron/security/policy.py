"""Security policy profiles and enforcement helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

SecurityProfileName = Literal["development", "standard", "strict"]


class SecurityProfile(StrEnum):
    DEVELOPMENT = "development"
    STANDARD = "standard"
    STRICT = "strict"


@dataclass(frozen=True, slots=True)
class SecurityPolicy:
    """Versioned security decisions for Hedron FastAPI integration."""

    profile: SecurityProfile = SecurityProfile.STANDARD
    version: int = 1
    csrf_enabled: bool = True
    csrf_cookie_name: str = "hedron_csrf"
    csrf_header_name: str = "X-CSRF-Token"
    csrf_form_field: str = "csrf_token"
    private_authenticated_cache: bool = True
    security_headers: bool = True
    content_security_policy: str | None = None
    frame_options: str = "DENY"
    content_type_options: str = "nosniff"
    referrer_policy: str = "no-referrer"
    explorer_enabled: bool = False
    allow_external_redirects: bool = False
    findings: tuple[str, ...] = field(default_factory=tuple)

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
                findings=("development profile: Explorer may be mounted",),
            )
        if profile is SecurityProfile.STRICT:
            return cls(
                profile=profile,
                csrf_enabled=True,
                security_headers=True,
                content_security_policy=(
                    "default-src 'self'; script-src 'self'; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data:; object-src 'none'; "
                    "base-uri 'self'; frame-ancestors 'none'"
                ),
                explorer_enabled=False,
                allow_external_redirects=False,
                findings=("strict profile: CSP and private caching enforced",),
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
            findings=("standard profile: CSRF and private authenticated caching enabled",),
        )

    def response_headers(self, *, authenticated: bool = False) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.security_headers:
            headers["X-Content-Type-Options"] = self.content_type_options
            headers["X-Frame-Options"] = self.frame_options
            headers["Referrer-Policy"] = self.referrer_policy
            if self.content_security_policy:
                headers["Content-Security-Policy"] = self.content_security_policy
        if authenticated and self.private_authenticated_cache:
            headers["Cache-Control"] = "private, no-store"
            headers["Pragma"] = "no-cache"
        return headers
