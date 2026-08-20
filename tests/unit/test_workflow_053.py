"""WORKFLOW-053 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron.sse import _TERMINAL
from hedron_core import (
    TERMINAL_JOB_STATES,
    OperationWorkflow,
    is_terminal_job_state,
    retry_operation,
)
from hedron_core.jobs import InMemoryJobBackend, JobState, reset_jobs_for_tests, set_job_backend


def test_workflow_053_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.53.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["WORKFLOW-053"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md").is_file()


def test_is_terminal_job_state_matches_sse_stop_set() -> None:
    assert TERMINAL_JOB_STATES == _TERMINAL
    assert {s.value for s in TERMINAL_JOB_STATES} == {"succeeded", "failed", "cancelled"}
    for state in _TERMINAL:
        assert is_terminal_job_state(state)
        assert is_terminal_job_state(state.value)
    assert not is_terminal_job_state(JobState.QUEUED)
    assert not is_terminal_job_state(JobState.RUNNING)
    assert not is_terminal_job_state("queued")
    assert not is_terminal_job_state("nope")


def test_operation_workflow_start_status_cancel_retry() -> None:
    reset_jobs_for_tests()
    backend = InMemoryJobBackend()
    set_job_backend(backend)
    try:
        wf = OperationWorkflow(backend=backend, job_type="pipeline")
        handle = wf.start(lambda: {"step": 1}, tenant_id="t1", auth_subject="alice")
        status = wf.status(handle.job_id, tenant_id="t1", auth_subject="alice")
        assert status is not None
        assert status.state is JobState.QUEUED
        assert wf.is_busy(status.state)
        assert not wf.is_terminal(status.state)

        assert wf.cancel(handle.job_id, tenant_id="t1", auth_subject="alice") is True
        cancelled = wf.status(handle.job_id, tenant_id="t1", auth_subject="alice")
        assert cancelled is not None
        assert is_terminal_job_state(cancelled.state)

        retried = wf.retry(
            factory=lambda: {"step": 2},
            tenant_id="t1",
            auth_subject="alice",
        )
        assert retried.job_id != handle.job_id
        again = retry_operation(
            backend,
            factory=lambda: ("pipeline", {"step": 3}),
            tenant_id="t1",
            auth_subject="alice",
        )
        assert again.job_id != retried.job_id
    finally:
        reset_jobs_for_tests()
