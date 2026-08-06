"""Capability-labeled live helpers for Flask (phase 0.11)."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from flask import Response, stream_with_context

from hedron_core.live import SseEvent, encode_sse

__all__ = [
    "POLLING_FALLBACK_SUPPORTED",
    "poll_status_response",
    "sse_response",
    "stream_text",
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
    events: Iterable[SseEvent | str],
    *,
    status: int = 200,
) -> Response:
    """Return a text/event-stream response (experimental).

    WSGI reverse proxies may buffer; applications must keep polling as a fallback.
    Prefer importing from ``hedron_flask.experimental``.
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

        iterator: Iterable[str] = (
            stream_with_context(generate()) if has_request_context() else generate()
        )
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


def stream_text(
    chunks: Iterable[str],
    *,
    status: int = 200,
    mimetype: str = "text/plain",
) -> Response:
    """Focused text streaming helper (experimental; not general HTML streaming)."""

    def generate() -> Iterator[str]:
        yield from chunks

    try:
        from flask import has_request_context

        iterator: Iterable[str] = (
            stream_with_context(generate()) if has_request_context() else generate()
        )
    except Exception:  # noqa: BLE001
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
