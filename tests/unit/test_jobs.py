"""JobBackend tests."""

from __future__ import annotations

import pytest

from hedron_core.jobs import (
    InMemoryJobBackend,
    JobState,
    _idempotency_scope_key,
    job_status_interaction,
    reset_jobs_for_tests,
)


def test_submit_idempotent_and_cancel() -> None:
    reset_jobs_for_tests()
    backend = InMemoryJobBackend()
    h1 = backend.submit("demo", {"x": 1}, idempotency_key="k1", tenant_id="t1")
    h2 = backend.submit("demo", {"x": 2}, idempotency_key="k1", tenant_id="t1")
    assert h1.job_id == h2.job_id
    assert backend.request_cancel(h1.job_id, tenant_id="t1") is True
    st = backend.get(h1.job_id)
    assert st is not None
    assert st.cancel_requested is True


def test_cleanup_drops_idempotency() -> None:
    backend = InMemoryJobBackend()
    handle = backend.submit("demo", {}, idempotency_key="gone")
    backend.mark(handle.job_id, JobState.SUCCEEDED)
    # Force expiry by rewriting updated_at via mark then cleanup with tiny window.
    rec = backend._jobs[handle.job_id]
    from hedron_core.jobs import JobStatus

    rec.status = JobStatus(
        job_id=rec.status.job_id,
        state=JobState.SUCCEEDED,
        job_type=rec.status.job_type,
        updated_at=0.0,
        created_at=0.0,
    )
    assert backend.cleanup_expired(older_than_seconds=1) == 1
    again = backend.submit("demo", {}, idempotency_key="gone")
    assert again.job_id != handle.job_id


def test_idempotency_distinguishes_missing_and_empty_scopes() -> None:
    backend = InMemoryJobBackend()
    unscoped = backend.submit("demo", {}, idempotency_key="same")
    empty_scoped = backend.submit(
        "demo", {}, idempotency_key="same", tenant_id="", auth_subject=""
    )

    assert unscoped.job_id != empty_scoped.job_id
    assert backend.submit("demo", {}, idempotency_key="same").job_id == unscoped.job_id
    assert (
        backend.submit("demo", {}, idempotency_key="same", tenant_id="", auth_subject="").job_id
        == empty_scoped.job_id
    )
    assert len(backend._jobs) == 2


def test_idempotency_scope_key_does_not_delete_cross_scope_pointer() -> None:
    backend = InMemoryJobBackend()
    other = backend.submit("demo", {}, idempotency_key="same", tenant_id="other")
    scoped = _idempotency_scope_key("same", tenant_id="expected", auth_subject=None)
    backend._idempotency[scoped] = other.job_id

    with pytest.raises(PermissionError, match="another scope"):
        backend.submit("demo", {}, idempotency_key="same", tenant_id="expected")
    assert backend._idempotency[scoped] == other.job_id


def test_mark_and_status_interaction() -> None:
    backend = InMemoryJobBackend()
    handle = backend.submit("demo", {})
    backend.mark(handle.job_id, JobState.SUCCEEDED, result={"ok": True})
    st = backend.get(handle.job_id)
    assert st is not None
    result = job_status_interaction(st)
    assert result.status_code == 202
    assert result.headers["Retry-After"] == "2"
