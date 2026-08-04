"""CSRF and session helpers for Django.

Django's built-in ``CsrfViewMiddleware`` and session middleware remain authoritative.
These helpers expose token/header names aligned with Hedron's portable CSRF contract
while remaining compatible with stock Django defaults.

Stock Django accepts ``X-CSRFToken`` (``CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"``).
For portable Hedron HTMX clients that send ``X-CSRF-Token``, set::

    CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"

in Django settings (as the reference app does). Form posts may use either
``csrfmiddlewaretoken`` (Django) or ``csrf_token`` (Hedron portable).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest

__all__ = [
    "DJANGO_CSRF_HEADER",
    "PORTABLE_CSRF_HEADER",
    "csrf_header_name",
    "csrf_token_for_request",
    "extract_csrf_from_post",
    "seed_csrf_cookie",
]

# Stock Django header / WSGI mapping.
DJANGO_CSRF_HEADER = "X-CSRFToken"
# Hedron portable header used by FastAPI/Flask adapters and HTMX helpers.
PORTABLE_CSRF_HEADER = "X-CSRF-Token"
DEFAULT_CSRF_HEADER = PORTABLE_CSRF_HEADER


def csrf_header_name() -> str:
    """Return the HTTP header clients should send (not the WSGI environ key)."""
    try:
        from django.conf import settings

        raw = getattr(settings, "CSRF_HEADER_NAME", None)
    except Exception:  # noqa: BLE001 — settings may be unconfigured in unit tests
        raw = None
    if raw == "HTTP_X_CSRF_TOKEN":
        return PORTABLE_CSRF_HEADER
    if raw == "HTTP_X_CSRFTOKEN":
        return DJANGO_CSRF_HEADER
    return DEFAULT_CSRF_HEADER


def csrf_token_for_request(request: HttpRequest) -> str:
    from django.middleware.csrf import get_token

    return get_token(request)


def seed_csrf_cookie(request: HttpRequest) -> str:
    """Ensure Django will set the CSRF cookie on the response (via get_token)."""
    return csrf_token_for_request(request)


def extract_csrf_from_post(
    request: HttpRequest,
    *,
    field_name: str | None = None,
) -> str | None:
    """Accept Django ``csrfmiddlewaretoken`` and Hedron portable ``csrf_token``."""
    names = (field_name,) if field_name else ("csrfmiddlewaretoken", "csrf_token")
    for name in names:
        if not name:
            continue
        value = request.POST.get(name)
        if isinstance(value, str) and value:
            return value
    return None
