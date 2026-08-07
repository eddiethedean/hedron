"""Django middleware applying portable Hedron security-profile headers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from django.http import HttpRequest, HttpResponse

from hedron_core.security_policy import SecurityPolicy

__all__ = ["HedronSecurityHeadersMiddleware", "security_policy_from_settings"]

_SETTINGS_PROFILE = "HEDRON_SECURITY_PROFILE"


def security_policy_from_settings(settings: Any | None = None) -> SecurityPolicy:
    """Resolve ``SecurityPolicy`` from Django settings (default ``standard``)."""
    if settings is None:
        from django.conf import settings as django_settings

        settings = django_settings
    name = getattr(settings, _SETTINGS_PROFILE, "standard")
    return SecurityPolicy.from_name(name)


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
