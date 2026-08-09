"""Capability-labeled live helpers for Django (phase 0.11)."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from django.http import HttpResponse, StreamingHttpResponse

from hedron_core.live import SseEvent, encode_sse

__all__ = [
    "POLLING_FALLBACK_SUPPORTED",
    "poll_status_response",
    "sse_response",
    "stream_text",
]

POLLING_FALLBACK_SUPPORTED = True


def sse_response(
    events: Iterable[SseEvent | str],
    *,
    status: int = 200,
) -> StreamingHttpResponse:
    """Return a text/event-stream StreamingHttpResponse (ASGI preferred).

    **Experimental** — prefer :func:`poll_status_response` in production. Import
    from ``hedron_django.experimental`` rather than the package root.
    """

    def generate() -> Iterator[bytes]:
        for item in events:
            if isinstance(item, SseEvent):
                yield encode_sse(item).encode("utf-8")
            else:
                yield str(item).encode("utf-8")

    response = StreamingHttpResponse(generate(), status=status, content_type="text/event-stream")
    response["Cache-Control"] = "no-store"
    response["X-Accel-Buffering"] = "no"
    response["X-Hedron-Live"] = "sse"
    response["X-Hedron-Fallback"] = "poll"
    return response


def stream_text(
    chunks: Iterable[str],
    *,
    status: int = 200,
    content_type: str = "text/plain",
) -> StreamingHttpResponse:
    """Stream plain text chunks (experimental).

    Prefer polling in production. Import from ``hedron_django.experimental``.
    """

    def generate() -> Iterator[bytes]:
        for chunk in chunks:
            yield chunk.encode("utf-8")

    response = StreamingHttpResponse(generate(), status=status, content_type=content_type)
    response["Cache-Control"] = "no-store"
    response["X-Hedron-Live"] = "stream"
    response["X-Hedron-Fallback"] = "poll"
    return response


def poll_status_response(body: str, *, status: int = 200) -> HttpResponse:
    """Ordinary HTTP polling response — Supported fallback on all Django modes."""
    response = HttpResponse(
        content=body.encode("utf-8"),
        status=status,
        content_type="text/html; charset=utf-8",
    )
    response["Cache-Control"] = "no-store"
    response["X-Hedron-Live"] = "poll"
    return response
