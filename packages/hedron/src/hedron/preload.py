"""Navigation preload helpers (phase 0.10)."""

from __future__ import annotations

from collections.abc import Mapping

from starlette.requests import Request
from starlette.responses import Response

from hedron_core.preload import (
    HX_PRELOADED,
    NavigationPreloadPolicy,
    PreloadDecision,
    decide_preload,
)

__all__ = [
    "HX_PRELOADED",
    "NavigationPreloadPolicy",
    "apply_preload_headers",
    "evaluate_preload_request",
]


def evaluate_preload_request(
    request: Request,
    policy: NavigationPreloadPolicy,
    *,
    speculative_count: int = 0,
    concurrent: int = 0,
    navigation_cancelled: bool = False,
) -> PreloadDecision:
    same_origin = True
    origin = request.headers.get("origin")
    if origin and request.url.hostname:
        from urllib.parse import urlparse

        same_origin = urlparse(origin).hostname == request.url.hostname
    return decide_preload(
        policy,
        method=request.method,
        same_origin=same_origin,
        speculative_count=speculative_count,
        concurrent=concurrent,
        cache_control_request=request.headers.get("cache-control"),
        navigation_cancelled=navigation_cancelled,
    )


def apply_preload_headers(
    response: Response,
    decision: PreloadDecision,
    *,
    extra: Mapping[str, str] | None = None,
) -> Response:
    if decision.allowed and decision.header_value is not None:
        response.headers[HX_PRELOADED] = decision.header_value
    if decision.cache_control:
        response.headers["Cache-Control"] = decision.cache_control
    if decision.cancel_on_navigation:
        response.headers["X-Hedron-Preload-Cancel"] = "navigation"
    if extra:
        for key, value in extra.items():
            response.headers[key] = value
    return response
