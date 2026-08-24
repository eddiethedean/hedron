"""Portable job-status HTMX interaction helper."""

from __future__ import annotations

from typing import TYPE_CHECKING

from hedron_core.action_state import ActionPhase, ActionState, ActionTrace, OperationIdentity
from hedron_core.jobs.types import JobStatus

if TYPE_CHECKING:
    from hedron_core.htmx.policy import InteractionResult


def action_state_for_job(status: JobStatus) -> ActionState:
    """Project an authorized job status into the phase 0.61 lifecycle."""
    phase = {
        "queued": ActionPhase.PENDING,
        "running": ActionPhase.PENDING,
        "succeeded": ActionPhase.SUCCESS,
        "failed": ActionPhase.ERROR,
        "cancelled": ActionPhase.CANCELLED,
    }[status.state.value]
    operation = OperationIdentity(status.job_id)
    message = (
        (status.error or "Job failed")
        if phase is ActionPhase.ERROR
        else f"Job {status.job_id}: {status.state.value}"
    )
    return ActionState(phase=phase, operation=operation, message=message[:512])


def job_status_interaction(status: JobStatus) -> InteractionResult:
    """Portable 202 InteractionResult with Retry-After and accessible polling UI."""
    from hedron_core.builtins.async_region import AsyncRegion
    from hedron_core.builtins.utilities import Status
    from hedron_core.htmx.policy import InteractionResult

    label = f"Job {status.job_id}: {status.state.value}"
    action_state = action_state_for_job(status)
    content = AsyncRegion(
        Status(label, tone="info", live=True),
        state=action_state.phase,
        label=f"Job {status.job_id}",
    )
    action_trace = ActionTrace().append(action_state.phase, operation=action_state.operation)
    return InteractionResult(
        content=content,
        status_code=202,
        action_state=action_state,
        action_trace=action_trace,
        cache="no-store",
        headers={"Retry-After": str(status.retry_after)},
        explanation=(
            "Bounded polling job status (SSE observation available via job_status_sse_events)"
        ),
    )
