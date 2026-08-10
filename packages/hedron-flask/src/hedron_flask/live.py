"""Capability-labeled live helpers for Flask (phase 0.11)."""

from __future__ import annotations

import warnings
from collections.abc import Iterable, Iterator

from flask import Response, stream_with_context

from hedron_core.live import SseEvent, encode_sse

__all__ = [
    "POLLING_FALLBACK_SUPPORTED",
    "poll_status_response",
]

# Polling remains the Supported fallback on WSGI hosts (D-044 / D-046).
POLLING_FALLBACK_SUPPORTED = True


def poll_status_response(body: str, *, status: int = 200) -> Response:
    """Ordinary HTTP polling response — Supported fallback on Flask hosts."""
    return Response(
        body,
        status=status,
        mimetype="text/html; charset=utf-8",
        headers={
            "Cache-Control": "no-store",
            "X-Hedron-Live": "poll",
        },
    )


def sse_response(
    events: Iterable[SseEvent],
    *,
    status: int = 200,
) -> Response:
    """Return a text/event-stream response (experimental).

    Prefer ``hedron_flask.experimental.sse_response``. Polling is the Supported fallback.
    Only ``SseEvent`` values are accepted — raw strings are rejected to prevent
    SSE framing injection.
    """
    warnings.warn(
        "hedron_flask.live.sse_response is experimental; import from "
        "hedron_flask.experimental (prefer polling in production).",
        DeprecationWarning,
        stacklevel=2,
    )

    def generate() -> Iterator[str]:
        for item in events:
            if not isinstance(item, SseEvent):
                raise TypeError(
                    "hedron_flask.live.sse_response accepts only SseEvent values; "
                    f"got {type(item)!r}"
                )
            yield encode_sse(item)

    # Prefer stream_with_context inside a request; fall back for factory use/tests.
    try:
        from flask import has_request_context

        iterator: Iterable[str] = (
            stream_with_context(generate()) if has_request_context() else generate()
        )
    except (ImportError, RuntimeError):
        iterator = generate()

    return Response(
        iterator,
        status=status,
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-store",
            "X-Accel-Buffering": "no",
            "X-Hedron-Live": "sse",
            "X-Hedron-Fallback": "poll",
        },
    )


def stream_text(
    chunks: Iterable[str],
    *,
    status: int = 200,
    mimetype: str = "text/plain",
) -> Response:
    """Focused text streaming helper (experimental; not general HTML streaming)."""
    warnings.warn(
        "hedron_flask.live.stream_text is experimental; import from "
        "hedron_flask.experimental (prefer polling in production).",
        DeprecationWarning,
        stacklevel=2,
    )

    def generate() -> Iterator[str]:
        yield from chunks

    try:
        from flask import has_request_context

        iterator: Iterable[str] = (
            stream_with_context(generate()) if has_request_context() else generate()
        )
    except (ImportError, RuntimeError):
        iterator = generate()

    return Response(
        iterator,
        status=status,
        mimetype=mimetype,
        headers={
            "Cache-Control": "no-store",
            "X-Hedron-Live": "stream",
            "X-Hedron-Fallback": "poll",
        },
    )
