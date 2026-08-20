"""SSE framing and job observation tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI, Request
from starlette.testclient import TestClient

from hedron.sse import extension_script_tags, job_status_sse_response, sse_response
from hedron_core.jobs import InMemoryJobBackend, JobState, set_job_backend
from hedron_core.live import SseEvent, encode_sse, job_status_sse_events


def _read_sse_body(response_factory) -> bytes:
    """Materialize an SSE StreamingResponse body via TestClient."""
    app = FastAPI()

    @app.get("/sse")
    def _endpoint():
        return response_factory()

    with TestClient(app) as client:
        return client.get("/sse").content


def test_encode_sse_frame() -> None:
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
    body = _read_sse_body(lambda: sse_response([SseEvent(data="ping", event="message", id="a")]))
    assert b"data: ping" in body
    assert b"event: message" in body
    assert b"id: a" in body


def test_job_status_sse_response_streams_until_terminal() -> None:
    backend = InMemoryJobBackend()
    set_job_backend(backend)
    handle = backend.submit("demo", {"n": 1}, auth_subject="alice")

    # Mark succeeded before the client connects so the generator exits promptly.
    backend.mark(handle.job_id, JobState.SUCCEEDED, result={"ok": True})
    body = _read_sse_body(
        lambda: job_status_sse_response(
            handle.job_id,
            backend=backend,
            auth_subject="alice",
            poll_interval_seconds=0.01,
        )
    )
    assert b"event: job-status" in body
    assert b"succeeded" in body
    assert b"event: hedron-close" in body
    assert b'"terminal":true' in body


def test_job_status_sse_response_polls_state_changes() -> None:
    backend = InMemoryJobBackend()
    set_job_backend(backend)
    handle = backend.submit("demo", {"n": 1}, auth_subject="alice")
    gets = {"n": 0}
    real_get = backend.get

    def _get(job_id: str, **kwargs):
        status = real_get(job_id)
        gets["n"] += 1
        if gets["n"] == 2 and status is not None and status.state is JobState.QUEUED:
            backend.mark(job_id, JobState.RUNNING)
            return real_get(job_id)
        if gets["n"] >= 4 and status is not None and status.state is JobState.RUNNING:
            backend.mark(job_id, JobState.SUCCEEDED, result={"ok": True})
            return real_get(job_id)
        return status

    backend.get = _get  # type: ignore[method-assign]
    body = _read_sse_body(
        lambda: job_status_sse_response(
            handle.job_id,
            backend=backend,
            auth_subject="alice",
            poll_interval_seconds=0.01,
        )
    )
    text = body.decode()
    assert "queued" in text or "running" in text
    assert "succeeded" in text
    assert "hedron-close" in text


def test_job_status_sse_skips_last_event_id() -> None:
    backend = InMemoryJobBackend()
    set_job_backend(backend)
    handle = backend.submit("demo", {}, auth_subject="alice")
    status = backend.get(handle.job_id)
    assert status is not None
    event_id = f"{status.job_id}:{status.updated_at}"
    backend.mark(handle.job_id, JobState.SUCCEEDED, result={"ok": True})

    app = FastAPI()

    @app.get("/sse")
    def _endpoint(request: Request):
        return job_status_sse_response(
            handle.job_id,
            backend=backend,
            request=request,
            auth_subject="alice",
            poll_interval_seconds=0.01,
        )

    with TestClient(app) as client:
        # Resume from the pre-terminal id: should still emit the succeeded terminal frame.
        resumed = client.get("/sse", headers={"Last-Event-ID": event_id})
    assert b"succeeded" in resumed.content
    assert b"hedron-close" in resumed.content


def test_job_status_sse_rejects_unscoped_jobs() -> None:
    from fastapi import HTTPException

    backend = InMemoryJobBackend()
    handle = backend.submit("demo", {})
    try:
        job_status_sse_response(handle.job_id, backend=backend, auth_subject="alice")
        raise AssertionError("expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 404


def test_job_status_sse_not_found() -> None:
    from fastapi import HTTPException

    backend = InMemoryJobBackend()
    try:
        job_status_sse_response("missing", backend=backend)
        raise AssertionError("expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 404


def test_extension_script_tags_include_sse() -> None:
    tags = extension_script_tags("htmx-ext-sse", "htmx-ext-head-support")
    joined = "\n".join(tags)
    assert "/hedron-static/ext/sse.js" in joined
    assert "/hedron-static/ext/head-support.js" in joined


def test_poll_interval_clamps_non_positive_values() -> None:
    from hedron.sse import _poll_interval

    assert _poll_interval(None, retry_after=2.0) == 2.0
    assert _poll_interval(None, retry_after=0.01) == 0.05
    assert _poll_interval(0.0, retry_after=2.0) == 2.0
    assert _poll_interval(-1.0, retry_after=0.01) == 0.05
    assert _poll_interval(0.2, retry_after=2.0) == 0.2


def test_issue_207() -> None:
    backend = InMemoryJobBackend()
    set_job_backend(backend)
    handle = backend.submit("demo", {}, auth_subject="alice")
    status = backend.get(handle.job_id)
    assert status is not None
    assert status.state is JobState.QUEUED
    event_id = f"{status.job_id}:{status.updated_at}"

    gets = {"n": 0}
    real_get = backend.get

    def _get(job_id: str, **kwargs):
        gets["n"] += 1
        if gets["n"] >= 3:
            backend.mark(job_id, JobState.SUCCEEDED, result={"ok": True})
        return real_get(job_id)

    backend.get = _get  # type: ignore[method-assign]

    app = FastAPI()

    @app.get("/sse")
    def _endpoint(request: Request):
        return job_status_sse_response(
            handle.job_id,
            backend=backend,
            request=request,
            auth_subject="alice",
            poll_interval_seconds=0.01,
        )

    with TestClient(app) as client:
        body = client.get("/sse", headers={"Last-Event-ID": event_id}).content.decode()

    assert '"state":"queued"' not in body
    assert "succeeded" in body
    assert "hedron-close" in body


def test_job_status_sse_zero_poll_interval_no_busy_loop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression for #143: poll_interval_seconds=0 must not sleep(0) forever."""
    import asyncio

    backend = InMemoryJobBackend()
    set_job_backend(backend)
    handle = backend.submit("demo", {"n": 1}, auth_subject="alice")
    backend.mark(handle.job_id, JobState.RUNNING)

    sleeps: list[float] = []
    real_sleep = asyncio.sleep

    async def capture_sleep(delay: float, result: object = None) -> object:
        sleeps.append(float(delay))
        if len(sleeps) >= 2:
            backend.mark(handle.job_id, JobState.SUCCEEDED, result={"ok": True})
        return await real_sleep(0)

    monkeypatch.setattr(asyncio, "sleep", capture_sleep)

    body = _read_sse_body(
        lambda: job_status_sse_response(
            handle.job_id,
            backend=backend,
            auth_subject="alice",
            poll_interval_seconds=0,
        )
    )
    assert sleeps
    assert all(delay >= 0.05 for delay in sleeps)
    assert b"succeeded" in body
    assert b"hedron-close" in body
