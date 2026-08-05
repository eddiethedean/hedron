"""Experimental live-transport surfaces (SSE, streaming, WebSocket, preload).

Prefer polling for production until ops gates close. Import from this module
explicitly, or use root ``hedron`` attribute access (compat shim).
"""

from __future__ import annotations

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
