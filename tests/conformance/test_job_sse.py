"""Job SSE conformance (JOB-006)."""

from __future__ import annotations

from hedron_core.jobs import InMemoryJobBackend, JobState, job_status_interaction, set_job_backend
from hedron_core.live import job_status_sse_events
from hedron_core.rendering import render


def test_job_sse_preserves_status_contract() -> None:
    backend = InMemoryJobBackend()
    set_job_backend(backend)
    handle = backend.submit("demo", {})
    status = backend.get(handle.job_id)
    assert status is not None
    polling = job_status_interaction(status)
    assert polling.status_code == 202
    assert "Retry-After" in polling.headers

    events = job_status_sse_events(
        job_id=status.job_id,
        state=status.state.value,
        message_html=render(polling.content).html,
        terminal=False,
    )
    assert events[0].event == "job-status"
    assert status.state is JobState.QUEUED

    backend.mark(handle.job_id, JobState.FAILED, error="boom")
    failed = backend.get(handle.job_id)
    assert failed is not None
    terminal = job_status_sse_events(
        job_id=failed.job_id,
        state=failed.state.value,
        message_html="<div>failed</div>",
        terminal=True,
    )
    assert any(e.event == "hedron-close" for e in terminal)
