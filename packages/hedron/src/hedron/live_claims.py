"""Live-transport claim inventory for Supported vs experimental honesty (#13)."""

from __future__ import annotations

# Surfaces that must remain experimental until Deferred ops gates close.
EXPERIMENTAL_LIVE_SURFACES: frozenset[str] = frozenset(
    {
        "SseResponse",
        "sse_response",
        "job_status_sse_response",
        "StreamingComponentResponse",
        "stream_tokens",
        "stream_chunked_list",
        "stream_document",
        "accept_page_session_channel",
        "send_region_update",
        "evaluate_preload_request",
        "apply_preload_headers",
    }
)

# Docs that must not call experimental live transports unqualified "Supported".
LIVE_CLAIM_DOC_GLOBS: tuple[str, ...] = (
    "docs/api/STABILITY.md",
    "docs/guides/whats-ready.md",
    "docs/api/SSE.md",
    "docs/api/STREAMING.md",
    "docs/api/WEBSOCKET_CHANNEL.md",
    "docs/api/PRELOAD.md",
)

SUPPORTED_PRODUCTION_FALLBACK = "polling"
