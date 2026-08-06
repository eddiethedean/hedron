"""Flask live helper tests (phase 0.11)."""

from __future__ import annotations

from flask import Flask

from hedron_core.live import SseEvent
from hedron_flask import poll_status_response
from hedron_flask.experimental import sse_response, stream_text
from hedron_flask.live import sse_response as live_sse_response


def test_sse_response_headers() -> None:
    app = Flask(__name__)
    with app.app_context():
        response = sse_response([SseEvent(data="hello", event="message", id="1")])
        assert response.mimetype == "text/event-stream"
        # Polling remains the Supported live fallback for Flask hosts.
        assert response.headers.get("X-Hedron-Fallback") == "poll"
        assert b"data: hello" in response.get_data()


def test_stream_text() -> None:
    app = Flask(__name__)
    with app.app_context():
        response = stream_text(["a", "b"])
        assert response.headers.get("X-Hedron-Live") == "stream"
        assert response.get_data() == b"ab"


def test_poll_status_response_supported_fallback() -> None:
    response = poll_status_response("<div>ok</div>")
    assert response.headers.get("X-Hedron-Live") == "poll"
    assert response.headers.get("Cache-Control") == "no-store"
    assert b"<div>ok</div>" in response.get_data()


def test_experimental_reexports_live_sse() -> None:
    assert live_sse_response is sse_response
