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
    "validate_csrf",
]

_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})

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
    except Exception:
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


class DjangoCsrfError(PermissionError):
    """Raised when Hedron Django CSRF validation fails closed."""


def validate_csrf(request: HttpRequest) -> None:
    """Fail closed on unsafe methods using Django's CSRF machinery.

    Bridges portable ``csrf_token`` form fields into ``csrfmiddlewaretoken`` before
    ``CsrfViewMiddleware.process_view``. Also accepts both ``X-CSRFToken`` and
    ``X-CSRF-Token`` request headers. Safe methods are no-ops. When Django CSRF
    middleware is disabled in settings this still rejects missing/invalid tokens so
    ``hedron_view`` / ``HedronDjango.respond`` do not silently skip protection.
    """
    method = (request.method or "GET").upper()
    if method in _SAFE_METHODS:
        return

    # Accept Hedron portable header alongside Django's default header name.
    django_hdr = "HTTP_X_CSRFTOKEN"
    portable_hdr = "HTTP_X_CSRF_TOKEN"
    if django_hdr not in request.META and request.META.get(portable_hdr):
        request.META = {**request.META, django_hdr: request.META[portable_hdr]}
    if portable_hdr not in request.META and request.META.get(django_hdr):
        request.META = {**request.META, portable_hdr: request.META[django_hdr]}

    # Bridge Hedron portable form field into Django's expected name.
    if not request.POST.get("csrfmiddlewaretoken"):
        portable = extract_csrf_from_post(request, field_name="csrf_token")
        if portable:
            try:
                mutable = request.POST.copy()
            except Exception:
                mutable = None
            if mutable is not None:
                mutable["csrfmiddlewaretoken"] = portable
                request.POST = mutable
            elif not (request.META.get(django_hdr) or request.META.get(portable_hdr)):
                raise DjangoCsrfError(
                    "CSRF validation failed: could not read csrf_token from the POST "
                    "body; send X-CSRFToken or X-CSRF-Token instead"
                )

    from django.http import HttpRequest as DjangoHttpRequest
    from django.http import HttpResponse, HttpResponseForbidden
    from django.middleware.csrf import CsrfViewMiddleware

    def _forbidden(_req: DjangoHttpRequest) -> HttpResponse:
        return HttpResponseForbidden(b"CSRF")

    def _noop_view(
        _req: DjangoHttpRequest, *_args: object, **_kwargs: object
    ) -> HttpResponse | None:
        return None

    middleware = CsrfViewMiddleware(_forbidden)
    rejected = middleware.process_view(request, _noop_view, (), {})
    if rejected is not None:
        from hedron_core.audit import SecurityAuditEventType, emit_security_audit

        emit_security_audit(
            SecurityAuditEventType.CSRF_REJECTED,
            "Django CSRF validation failed",
            attributes={"path": getattr(request, "path", "")},
        )
        raise DjangoCsrfError(
            "CSRF validation failed; send csrfmiddlewaretoken / csrf_token form field "
            "or X-CSRFToken / X-CSRF-Token header"
        )
