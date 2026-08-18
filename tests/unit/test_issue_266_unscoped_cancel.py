"""#266: JobBackend.request_cancel must fail closed for unscoped jobs."""

from __future__ import annotations

from hedron_core.jobs import InMemoryJobBackend, job_authorized_http


def test_unscoped_cancel_without_credentials_fails_closed() -> None:
    backend = InMemoryJobBackend()
    handle = backend.submit("t", {})
    status = backend.get(handle.job_id)
    assert status is not None
    assert job_authorized_http(status) is False
    assert backend.request_cancel(handle.job_id) is False
    assert backend.request_cancel(handle.job_id, auth_subject="alice") is False
