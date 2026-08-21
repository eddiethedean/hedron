"""Experimental live-transport surfaces (SSE, streaming, WebSocket, preload).

Prefer polling for production until ops gates close. Import from this module
explicitly. Root ``hedron`` attribute access remains a temporary compat shim that
emits ``DeprecationWarning`` — remove those aliases before an honest 1.0 freeze
(see ``docs/guides/one-point-zero-readiness.md`` and ``docs/api/SYMBOL_TIERS.md``).

Under ``HEDRON_ENV=production``, calling these helpers fails closed unless
``HEDRON_SECURITY_RISK_ACCEPTANCE`` includes ``experimental-live``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar, cast

from hedron.preload import (
    HX_PRELOADED,
    NavigationPreloadPolicy,
    apply_preload_headers,
    evaluate_preload_request,
)
from hedron.sse import SseResponse, extension_script_tags, job_status_sse_response, sse_response
from hedron.streaming import (
    StreamingComponentResponse,
    stream_chunked_list,
    stream_document,
    stream_tokens,
)
from hedron.websocket_channel import (
    ALLOW_MISSING_ORIGIN,
    accept_page_session_channel,
    origin_allowed,
    send_region_update,
)
from hedron_core.production_gate import assert_experimental_live_allowed

_F = TypeVar("_F", bound=Callable[..., Any])


def _guard_live(fn: _F) -> _F:
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        assert_experimental_live_allowed()
        return fn(*args, **kwargs)

    wrapped.__name__ = getattr(fn, "__name__", "wrapped")
    wrapped.__doc__ = getattr(fn, "__doc__", None)
    return cast(_F, wrapped)


sse_response = _guard_live(sse_response)
job_status_sse_response = _guard_live(job_status_sse_response)
stream_chunked_list = _guard_live(stream_chunked_list)
stream_document = _guard_live(stream_document)
stream_tokens = _guard_live(stream_tokens)
accept_page_session_channel = _guard_live(accept_page_session_channel)
send_region_update = _guard_live(send_region_update)
apply_preload_headers = _guard_live(apply_preload_headers)
evaluate_preload_request = _guard_live(evaluate_preload_request)

__all__ = [
    "ALLOW_MISSING_ORIGIN",
    "HX_PRELOADED",
    "NavigationPreloadPolicy",
    "SseResponse",
    "StreamingComponentResponse",
    "accept_page_session_channel",
    "apply_preload_headers",
    "evaluate_preload_request",
    "extension_script_tags",
    "job_status_sse_response",
    "origin_allowed",
    "send_region_update",
    "sse_response",
    "stream_chunked_list",
    "stream_document",
    "stream_tokens",
]
