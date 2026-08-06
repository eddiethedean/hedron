"""FastAPI adapters for portable ``BrowserContext`` (phase 0.15)."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, Request

from hedron_core.browser import BrowserContext, ViewportHint

__all__ = [
    "browser_context",
    "browser_context_from_request",
]


def browser_context_from_request(
    request: Request,
    *,
    locale: str | None = None,
    timezone: str | None = None,
    color_mode: str | None = None,
    viewport: ViewportHint | None = None,
) -> BrowserContext:
    """Build a :class:`~hedron_core.browser.BrowserContext` from a Starlette request.

    Client-reported overrides (``locale``, ``timezone``, ``color_mode``,
    ``viewport``) remain **spoofable** even when taken from cookies or query
    parameters — never use them for authorization.
    """
    headers = {str(k): str(v) for k, v in request.headers.items()}
    cookies = {str(k): str(v) for k, v in request.cookies.items()}
    client = request.client
    client_address = None if client is None else f"{client.host}:{client.port}"
    url = str(request.url)
    return BrowserContext.from_mapping(
        headers,
        url=url,
        client_address=client_address,
        cookies=cookies,
        locale=locale,
        timezone=timezone,
        color_mode=color_mode,
        viewport=viewport,
    )


def browser_context(
    *,
    locale: str | None = None,
    timezone: str | None = None,
    color_mode: str | None = None,
) -> Any:
    """FastAPI dependency that injects :class:`~hedron_core.browser.BrowserContext`."""

    async def dependency(request: Request) -> BrowserContext:
        return browser_context_from_request(
            request,
            locale=locale,
            timezone=timezone,
            color_mode=color_mode,
        )

    return Depends(dependency)
