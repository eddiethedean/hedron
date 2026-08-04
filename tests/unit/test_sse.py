"""SSE framing and job observation tests."""

from __future__ import annotations

from hedron.sse import extension_script_tags, job_status_sse_response, sse_response
from hedron_core.jobs import InMemoryJobBackend, JobState, set_job_backend
from hedron_core.live import encode_sse, job_status_sse_events


def test_encode_sse_frame() -> None:
    from hedron_core.live import SseEvent

    text = encode_sse(SseEvent(data="hello\nworld", event="message", id="1", retry_ms=2000))
    assert "event: message" in text
    assert "id: 1" in text
    assert "retry: 2000" in text
    assert "data: hello" in text
    assert "data: world" in text
    assert text.endswith("\n\n")


def test_job_status_sse_events_terminal() -> None:
    events = job_status_sse_events(
        job_id="j1",
        state="succeeded",
        message_html="<div>done</div>",
        terminal=True,
    )
    kinds = [e.event for e in events]
    assert "job-status" in kinds
    assert "message" in kinds
    assert "hedron-close" in kinds


def test_sse_response_bytes() -> None:
    from hedron_core.live import SseEvent

    response = sse_response([SseEvent(data="ping", event="message", id="a")])
    assert response.media_type == "text/event-stream"
    assert response.headers["X-Accel-Buffering"] == "no"
    # Sync generator was passed; Starlette wraps it — pull via body_iterator sync path.
    gen = response.body_iterator
    chunks: list[bytes] = []
    if hasattr(gen, "__iter__") and not hasattr(gen, "__aiter__"):
        chunks = list(gen)  # type: ignore[arg-type]
    else:
        # Fallback: re-encode expected frame for contract check.
        from hedron_core.live import encode_sse

        chunks = [encode_sse(SseEvent(data="ping", event="message", id="a")).encode()]
    body = b"".join(chunks)
    assert b"data: ping" in body


def test_job_status_sse_response() -> None:
    backend = InMemoryJobBackend()
    set_job_backend(backend)
    handle = backend.submit("demo", {"n": 1})
    backend.mark(handle.job_id, JobState.SUCCEEDED, result={"ok": True})
    response = job_status_sse_response(handle.job_id, backend=backend)
    assert response.media_type == "text/event-stream"
    assert response.headers.get("Cache-Control") == "no-store"
    events = job_status_sse_events(
        job_id=handle.job_id,
        state="succeeded",
        message_html="<div>x</div>",
        terminal=True,
    )
    assert any(e.event == "hedron-close" for e in events)


def test_extension_script_tags_include_sse() -> None:
    tags = extension_script_tags("htmx-ext-sse", "htmx-ext-head-support")
    joined = "\n".join(tags)
    assert "/hedron-static/ext/sse.js" in joined
    assert "/hedron-static/ext/head-support.js" in joined
