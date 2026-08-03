"""Safe redirect helpers."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse
from starlette.responses import Response

from hedron.security.policy import SecurityPolicy

__all__ = ["redirect_external", "redirect_local"]

# Reject backslashes and control characters that browsers may normalize into open redirects.
_LOCAL_PATH = re.compile(r"^/[A-Za-z0-9._~!$&'()*+,;=:@%/\-]*$")


def _is_local(url: str) -> bool:
    if "\\" in url or any(ord(ch) < 32 for ch in url):
        return False
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc:
        return False
    if not url.startswith("/") or url.startswith("//"):
        return False
    path = parsed.path or "/"
    return _LOCAL_PATH.fullmatch(path) is not None


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
    # Fail closed: missing policy means external redirects are disabled.
    allow = bool(policy is not None and policy.allow_external_redirects)
    if not allow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="External redirects are disabled by security policy",
        )
    return RedirectResponse(url=url, status_code=status_code)
