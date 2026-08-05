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
# Keep adopter-facing pages here; historical DECISIONS / ROADMAP are excluded.
LIVE_CLAIM_DOC_GLOBS: tuple[str, ...] = (
    "docs/api/STABILITY.md",
    "docs/api/JOBS.md",
    "docs/api/SSE.md",
    "docs/api/STREAMING.md",
    "docs/api/WEBSOCKET_CHANNEL.md",
    "docs/api/PRELOAD.md",
    "docs/api/ADAPTERS.md",
    "docs/guides/whats-ready.md",
    "docs/guides/faq.md",
    "docs/guides/troubleshooting.md",
    "docs/guides/upgrade.md",
    "docs/guides/cookbook.md",
    "docs/getting-started/flask.md",
    "docs/getting-started/django.md",
    "docs/COMPATIBILITY.md",
    "docs/ARCHITECTURE.md",
    "README.md",
)

# Phrases that imply live SSE/WS are unqualified Supported (current-train claim).
FORBIDDEN_LIVE_SUPPORTED_PHRASES: tuple[str, ...] = (
    "Official HTMX SSE observation is\n    **Supported**",
    "SSE observation is **Supported**",
    "SSE observation Supported on FastAPI",
    "official SSE observation is Supported",
    "Official HTMX SSE is Supported",
    "Official HTMX SSE live observation is **Supported",
    "FastAPI SSE helpers are Supported",
    "are FastAPI-flagship Supported surfaces",
    "Official SSE and focused streaming are Supported",
    "Supported live-transport surfaces",
)

SUPPORTED_PRODUCTION_FALLBACK = "polling"
