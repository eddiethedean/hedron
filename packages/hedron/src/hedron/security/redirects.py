"""Safe redirect helpers."""

from __future__ import annotations

from urllib.parse import urlparse

from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse
from starlette.responses import Response

from hedron.security.policy import SecurityPolicy

__all__ = ["redirect_external", "redirect_local"]


def _is_local(url: str) -> bool:
    parsed = urlparse(url)
    if not parsed.scheme and not parsed.netloc:
        return url.startswith("/") and not url.startswith("//")
    return False


def redirect_local(
    url: str,
    *,
    status_code: int = 303,
    policy: SecurityPolicy | None = None,
) -> Response:
    del policy  # reserved for future host allowlists
    if not _is_local(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="External redirect rejected; use redirect_external explicitly",
        )
    return RedirectResponse(url=url, status_code=status_code)


def redirect_external(
    url: str,
    *,
    status_code: int = 303,
    policy: SecurityPolicy | None = None,
) -> Response:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid external redirect URL",
        )
    if policy is not None and not policy.allow_external_redirects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="External redirects are disabled by security policy",
        )
    return RedirectResponse(url=url, status_code=status_code)
