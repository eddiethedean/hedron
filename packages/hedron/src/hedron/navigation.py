"""FastAPI/Starlette helpers for the phase 0.62 navigation contract."""

from __future__ import annotations

from collections.abc import Mapping
from uuid import uuid4

from starlette.requests import Request
from starlette.responses import Response

from hedron_core.navigation import (
    NavigationIdentity,
    NavigationPhase,
    NavigationPolicy,
    PrefetchDecision,
    decide_prefetch,
)

__all__ = [
    "HEDRON_NAVIGATION_HEADER",
    "HEDRON_NAVIGATION_PHASE_HEADER",
    "HEDRON_NAVIGATION_TARGET_HEADER",
    "HEDRON_NAVIGATION_TITLE_HEADER",
    "HEDRON_PREFETCH_HEADER",
    "apply_navigation_headers",
    "evaluate_prefetch_request",
    "navigation_identity_from_request",
]

HEDRON_NAVIGATION_HEADER = "X-Hedron-Navigation"
HEDRON_NAVIGATION_PHASE_HEADER = "X-Hedron-Navigation-Phase"
HEDRON_NAVIGATION_TARGET_HEADER = "X-Hedron-Navigation-Target"
HEDRON_NAVIGATION_TITLE_HEADER = "X-Hedron-Title"
HEDRON_PREFETCH_HEADER = "X-Hedron-Prefetch"


def _request_origin(request: Request) -> str:
    scheme = request.url.scheme or "http"
    host = request.headers.get("host") or request.url.netloc
    return f"{scheme}://{host}"


def navigation_identity_from_request(
    request: Request,
    *,
    generation: int,
    target: str = "document",
) -> NavigationIdentity:
    navigation_id = request.headers.get(HEDRON_NAVIGATION_HEADER) or str(uuid4())
    return NavigationIdentity(
        navigation_id=navigation_id,
        generation=generation,
        url=str(request.url),
        target=target,
    )


def apply_navigation_headers(
    response: Response,
    *,
    identity: NavigationIdentity,
    phase: NavigationPhase = NavigationPhase.COMMITTED,
    title: str | None = None,
    extra: Mapping[str, str] | None = None,
) -> Response:
    """Annotate a response without making browser headers authoritative."""
    response.headers[HEDRON_NAVIGATION_PHASE_HEADER] = phase.value
    response.headers[HEDRON_NAVIGATION_TARGET_HEADER] = identity.target
    response.headers["X-Hedron-Navigation-Generation"] = str(identity.generation)
    if title is not None:
        response.headers[HEDRON_NAVIGATION_TITLE_HEADER] = title
    if extra:
        for key, value in extra.items():
            if any(ord(char) < 32 for char in key + value):
                raise ValueError("navigation response headers must not contain controls")
            response.headers[key] = value
    return response


def evaluate_prefetch_request(
    request: Request,
    policy: NavigationPolicy,
    *,
    concurrent: int = 0,
    response_bytes: int = 0,
    private: bool = False,
) -> PrefetchDecision:
    return decide_prefetch(
        policy,
        method=request.method,
        url=str(request.url),
        origin=_request_origin(request),
        concurrent=concurrent,
        response_bytes=response_bytes,
        private=private,
    )
