"""CSRF and session helpers for Django.

Django's built-in ``CsrfViewMiddleware`` and session middleware remain authoritative.
These helpers only expose Hedron-aligned token/header names for forms and HTMX headers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest

__all__ = [
    "csrf_header_name",
    "csrf_token_for_request",
    "extract_csrf_from_post",
]

DEFAULT_CSRF_HEADER = "X-CSRF-Token"


def csrf_header_name() -> str:
    return DEFAULT_CSRF_HEADER


def csrf_token_for_request(request: HttpRequest) -> str:
    from django.middleware.csrf import get_token

    return get_token(request)


def extract_csrf_from_post(
    request: HttpRequest,
    *,
    field_name: str = "csrfmiddlewaretoken",
) -> str | None:
    value = request.POST.get(field_name)
    return value if isinstance(value, str) and value else None
