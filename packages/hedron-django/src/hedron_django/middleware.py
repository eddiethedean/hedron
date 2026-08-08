"""Django middleware applying portable Hedron security-profile headers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import replace
from typing import Any

from django.http import HttpRequest, HttpResponse

from hedron_core.security_policy import SecurityHeadersPolicy, SecurityPolicy

__all__ = ["HedronSecurityHeadersMiddleware", "security_policy_from_settings"]

_SETTINGS_PROFILE = "HEDRON_SECURITY_PROFILE"
_SETTINGS_POLICY = "HEDRON_SECURITY_POLICY"
_SETTINGS_HEADERS = "HEDRON_SECURITY_HEADERS"


def _headers_policy_from_mapping(raw: Mapping[str, Any]) -> SecurityHeadersPolicy:
    allowed = {
        "content_security_policy",
        "frame_options",
        "content_type_options",
        "referrer_policy",
        "hsts_max_age",
    }
    kwargs = {key: raw[key] for key in allowed if key in raw}
    return SecurityHeadersPolicy(**kwargs)


def security_policy_from_settings(settings: Any | None = None) -> SecurityPolicy:
    """Resolve ``SecurityPolicy`` from Django settings (default ``standard``).

    Precedence:
    1. ``HEDRON_SECURITY_POLICY`` — a ``SecurityPolicy`` instance or zero-arg callable
    2. ``HEDRON_SECURITY_PROFILE`` name + optional ``HEDRON_SECURITY_HEADERS`` merge
       (``SecurityHeadersPolicy`` or a dict of overrides)
    """
    if settings is None:
        from django.conf import settings as django_settings

        settings = django_settings

    configured = getattr(settings, _SETTINGS_POLICY, None)
    if callable(configured) and not isinstance(configured, SecurityPolicy):
        configured = configured()
    if isinstance(configured, SecurityPolicy):
        return configured

    name = getattr(settings, _SETTINGS_PROFILE, "standard")
    policy = SecurityPolicy.from_name(name)
    headers = getattr(settings, _SETTINGS_HEADERS, None)
    if isinstance(headers, SecurityHeadersPolicy):
        return replace(policy, security_headers=headers)
    if isinstance(headers, Mapping):
        return replace(policy, security_headers=_headers_policy_from_mapping(headers))
    return policy


class HedronSecurityHeadersMiddleware:
    """Apply ``SecurityPolicy.response_headers`` using Django auth when present."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        self.policy = security_policy_from_settings()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        authenticated = False
        user = getattr(request, "user", None)
        if user is not None:
            authenticated = bool(getattr(user, "is_authenticated", False))
        for key, value in self.policy.response_headers(authenticated=authenticated).items():
            if (authenticated and key in {"Cache-Control", "Pragma"}) or (key not in response):
                response[key] = value
        return response
