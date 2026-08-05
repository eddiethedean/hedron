"""Django live helper tests (phase 0.11)."""

from __future__ import annotations

from hedron_core.live import SseEvent
from hedron_django.live import (
    POLLING_FALLBACK_SUPPORTED,
    poll_status_response,
    sse_response,
    stream_text,
)


def test_polling_fallback_flag() -> None:
    assert POLLING_FALLBACK_SUPPORTED is True


def test_sse_and_poll() -> None:
    response = sse_response([SseEvent(data="ping", id="1")])
    assert response["X-Hedron-Fallback"] == "poll"
    assert response["Content-Type"].startswith("text/event-stream")
    chunks = b"".join(response.streaming_content)
    assert b"data: ping" in chunks

    poll = poll_status_response("<div>ok</div>")
    assert poll["X-Hedron-Live"] == "poll"
    assert b"ok" in poll.content


def test_stream_text() -> None:
    response = stream_text(["x", "y"])
    assert b"xy" == b"".join(response.streaming_content)
