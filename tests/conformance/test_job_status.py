"""202 job status conformance."""

from __future__ import annotations

from hedron_core.jobs import InMemoryJobBackend, JobState, job_status_interaction
from hedron_core.rendering import RenderMode, render


def test_job_status_renders_accessible_live_region() -> None:
    backend = InMemoryJobBackend()
    handle = backend.submit("work", {})
    backend.mark(handle.job_id, JobState.RUNNING)
    status = backend.get(handle.job_id)
    assert status is not None
    result = job_status_interaction(status)
    assert result.content is not None
    html = render(result.content, mode=RenderMode.FRAGMENT).html
    assert "aria-live" in html
    assert status.job_id in html
    assert result.headers.get("Retry-After")
    from hedron_core.interaction import interaction_headers

    headers = interaction_headers(result)
    assert headers["Retry-After"] == "2"
