"""BUDGET-025 / W-025-JOB-POLL — job status poll fanout soft budget."""

from __future__ import annotations

import time

import pytest

from hedron_core.jobs import InMemoryJobBackend, JobState, set_job_backend

pytestmark = pytest.mark.performance

_FANOUT = 50
_POLL_MS = 500


def test_w025_job_poll_fanout() -> None:
    backend = InMemoryJobBackend()
    set_job_backend(backend)
    handles = [
        backend.submit(
            "w025-poll",
            {"i": i},
            auth_subject="budget-user",
            tenant_id="budget-tenant",
        )
        for i in range(_FANOUT)
    ]
    for handle in handles:
        backend.mark(handle.job_id, JobState.SUCCEEDED, result={"ok": True})

    t0 = time.perf_counter()
    statuses = [
        backend.get(h.job_id, auth_subject="budget-user", tenant_id="budget-tenant")
        for h in handles
    ]
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms <= _POLL_MS
    assert len(statuses) == _FANOUT
    assert all(s is not None and s.state == JobState.SUCCEEDED for s in statuses)
