"""Capability-labeled live helpers for Flask (phase 0.11)."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any

from flask import Response, stream_with_context

from hedron_core.live import SseEvent, encode_sse

__all__ = ["POLLING_FALLBACK_SUPPORTED", "sse_response", "stream_text"]

# Polling remains the Supported fallback on WSGI hosts (D-044 / D-046).
POLLING_FALLBACK_SUPPORTED = True


def sse_response(
    events: Iterable[SseEvent | str],
    *,
    status: int = 200,
) -> Response:
    """Return a text/event-stream response.

    WSGI reverse proxies may buffer; applications must keep polling as a fallback.
    """

    def generate() -> Iterator[str]:
        for item in events:
            if isinstance(item, SseEvent):
                yield encode_sse(item)
            else:
                yield str(item)

    # Prefer stream_with_context inside a request; fall back for factory use/tests.
    try:
        from flask import has_request_context

        iterator: Any = stream_with_context(generate()) if has_request_context() else generate()
    except Exception:  # noqa: BLE001
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


def stream_text(chunks: Iterable[str], *, status: int = 200, mimetype: str = "text/plain") -> Response:
    """Focused text streaming helper (not general HTML streaming)."""

    def generate() -> Iterator[str]:
        for chunk in chunks:
            yield chunk

    try:
        from flask import has_request_context

        iterator: Any = stream_with_context(generate()) if has_request_context() else generate()
    except Exception:  # noqa: BLE001
        iterator = generate()

    return Response(
        iterator,
        status=status,
        mimetype=mimetype,
        headers={"Cache-Control": "no-store", "X-Hedron-Live": "stream", "X-Hedron-Fallback": "poll"},
    )
