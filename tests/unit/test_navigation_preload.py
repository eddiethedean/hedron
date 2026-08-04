"""Navigation preload policy tests."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import Response

from hedron.preload import apply_preload_headers, evaluate_preload_request
from hedron_core.preload import HX_PRELOADED, NavigationPreloadPolicy, decide_preload


def test_preload_disabled_by_default() -> None:
    decision = decide_preload(
        NavigationPreloadPolicy(),
        method="GET",
        same_origin=True,
        speculative_count=0,
        concurrent=0,
    )
    assert decision.allowed is False
    assert decision.reason == "preload_disabled"


def test_preload_enabled_safe_get() -> None:
    policy = NavigationPreloadPolicy(enabled=True)
    decision = decide_preload(
        policy, method="GET", same_origin=True, speculative_count=0, concurrent=0
    )
    assert decision.allowed is True
    assert decision.header_value == "1"
    assert decision.cancel_on_navigation is True
    assert decision.cache_control == "private, max-age=0"
    response = Response("ok")
    apply_preload_headers(response, decision)
    assert response.headers[HX_PRELOADED] == "1"
    assert response.headers["Cache-Control"] == "private, max-age=0"
    assert response.headers["X-Hedron-Preload-Cancel"] == "navigation"


def test_preload_respects_private_cache_and_cancel() -> None:
    policy = NavigationPreloadPolicy(enabled=True)
    denied = decide_preload(
        policy,
        method="GET",
        same_origin=True,
        speculative_count=0,
        concurrent=0,
        cache_control_request="private, no-store",
    )
    assert denied.allowed is False
    assert denied.reason == "private_cache"

    cancelled = decide_preload(
        policy,
        method="GET",
        same_origin=True,
        speculative_count=0,
        concurrent=0,
        navigation_cancelled=True,
    )
    assert cancelled.allowed is False
    assert cancelled.reason == "navigation_cancelled"


def test_evaluate_preload_request() -> None:
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [(b"origin", b"http://test")],
        "client": ("127.0.0.1", 1),
        "server": ("test", 80),
    }
    request = Request(scope)
    decision = evaluate_preload_request(request, NavigationPreloadPolicy(enabled=True))
    assert decision.allowed is True

    missing_origin = Request({**scope, "headers": []})
    denied = evaluate_preload_request(missing_origin, NavigationPreloadPolicy(enabled=True))
    assert denied.allowed is False
    assert denied.reason == "cross_origin"
