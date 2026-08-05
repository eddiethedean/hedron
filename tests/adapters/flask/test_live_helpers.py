"""Flask live helper tests (phase 0.11)."""

from __future__ import annotations

from flask import Flask

from hedron_core.live import SseEvent
from hedron_flask.live import POLLING_FALLBACK_SUPPORTED, sse_response, stream_text


def test_polling_fallback_flag() -> None:
    assert POLLING_FALLBACK_SUPPORTED is True


def test_sse_response_headers() -> None:
    app = Flask(__name__)
    with app.app_context():
        response = sse_response([SseEvent(data="hello", event="message", id="1")])
        assert response.mimetype == "text/event-stream"
        assert response.headers.get("X-Hedron-Fallback") == "poll"
        assert b"data: hello" in response.get_data()


def test_stream_text() -> None:
    app = Flask(__name__)
    with app.app_context():
        response = stream_text(["a", "b"])
        assert response.headers.get("X-Hedron-Live") == "stream"
        assert response.get_data() == b"ab"
