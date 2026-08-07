"""Safe redirect helpers."""

from __future__ import annotations

from urllib.parse import urlparse

from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse
from starlette.responses import Response

from hedron.security.policy import SecurityPolicy
from hedron_core.htmx_contract import is_local_path

__all__ = ["redirect_external", "redirect_local"]


def redirect_local(
    url: str,
    *,
    status_code: int = 303,
    policy: SecurityPolicy | None = None,
    mount: str | None = None,
) -> Response:
    del policy  # reserved for future host allowlists
    if not is_local_path(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="External redirect rejected; use redirect_external explicitly",
        )
    target = url
    if mount is not None:
        from hedron.mount import prefix_local_path

        target = prefix_local_path(url, mount)
    return RedirectResponse(url=target, status_code=status_code)


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
    if parsed.username is not None or parsed.password is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="External redirect URL must not contain credentials",
        )
    # Fail closed: missing policy means external redirects are disabled.
    allow = bool(policy is not None and policy.allow_external_redirects)
    if not allow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="External redirects are disabled by security policy",
        )
    return RedirectResponse(url=url, status_code=status_code)
