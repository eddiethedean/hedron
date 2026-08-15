"""Portable job-status HTMX interaction helper."""

from __future__ import annotations

from typing import TYPE_CHECKING

from hedron_core.jobs.types import JobStatus

if TYPE_CHECKING:
    from hedron_core.interaction import InteractionResult


def job_status_interaction(status: JobStatus) -> InteractionResult:
    """Portable 202 InteractionResult with Retry-After and accessible polling UI."""
    from hedron_core.builtins import Status
    from hedron_core.interaction import InteractionResult

    label = f"Job {status.job_id}: {status.state.value}"
    content = Status(label, tone="info", live=True)
    return InteractionResult(
        content=content,
        status_code=202,
        cache="no-store",
        headers={"Retry-After": str(status.retry_after)},
        explanation=(
            "Bounded polling job status (SSE observation available via job_status_sse_events)"
        ),
    )
