"""Long-running operation workflow helpers over ``JobBackend`` (WORKFLOW-053).

Thin composition of start / status / cancel / retry. Terminal job states
``succeeded``, ``failed``, and ``cancelled`` stop SSE monitoring — see
``hedron.sse._TERMINAL`` and ``job_status_sse_response``.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from hedron_core.jobs.backend import JobBackend
from hedron_core.jobs.types import JobHandle, JobState, JobStatus
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "TERMINAL_JOB_STATES",
    "OperationWorkflow",
    "is_terminal_job_state",
    "retry_operation",
]

TERMINAL_JOB_STATES: frozenset[JobState] = frozenset(
    {
        JobState.SUCCEEDED,
        JobState.FAILED,
        JobState.CANCELLED,
    }
)


def is_terminal_job_state(state: JobState | str | object) -> bool:
    """Return True for succeeded / failed / cancelled (SSE monitoring stops)."""
    if isinstance(state, JobState):
        return state in TERMINAL_JOB_STATES
    if isinstance(state, str):
        try:
            return JobState(state) in TERMINAL_JOB_STATES
        except ValueError:
            return False
    return False


def retry_operation(
    backend: JobBackend,
    *,
    factory: Callable[[], tuple[str, Mapping[str, JsonValue]] | Mapping[str, JsonValue]],
    job_type: str = "operation",
    idempotency_key: str | None = None,
    tenant_id: str | None = None,
    auth_subject: str | None = None,
) -> JobHandle:
    """Explicitly re-submit a new job via ``factory`` (does not mutate prior ids).

    ``factory`` returns either a payload mapping or ``(job_type, payload)``.
    """
    produced = factory()
    if isinstance(produced, tuple) and len(produced) == 2:
        submit_type, payload = produced
        submit_type = str(submit_type)
    else:
        submit_type = job_type
        payload = produced
    return backend.submit(
        submit_type,
        payload,
        idempotency_key=idempotency_key,
        tenant_id=tenant_id,
        auth_subject=auth_subject,
    )


@dataclass(slots=True)
class OperationWorkflow:
    """Thin start / status / cancel / retry helpers over a ``JobBackend``."""

    backend: JobBackend
    job_type: str = "operation"

    def start(
        self,
        factory: Callable[[], Mapping[str, JsonValue]],
        *,
        idempotency_key: str | None = None,
        tenant_id: str | None = None,
        auth_subject: str | None = None,
    ) -> JobHandle:
        """Submit a new operation; ``factory`` returns the job payload (never polled here)."""
        payload = factory()
        return self.backend.submit(
            self.job_type,
            payload,
            idempotency_key=idempotency_key,
            tenant_id=tenant_id,
            auth_subject=auth_subject,
        )

    def status(
        self,
        job_id: str,
        *,
        auth_subject: str | None = None,
        tenant_id: str | None = None,
    ) -> JobStatus | None:
        """Observe job status when authorized."""
        return self.backend.get(job_id, auth_subject=auth_subject, tenant_id=tenant_id)

    def cancel(
        self,
        job_id: str,
        *,
        auth_subject: str | None = None,
        tenant_id: str | None = None,
    ) -> bool:
        """Request cooperative cancellation."""
        return self.backend.request_cancel(job_id, auth_subject=auth_subject, tenant_id=tenant_id)

    def retry(
        self,
        *,
        factory: Callable[[], tuple[str, Mapping[str, JsonValue]] | Mapping[str, JsonValue]],
        idempotency_key: str | None = None,
        tenant_id: str | None = None,
        auth_subject: str | None = None,
    ) -> JobHandle:
        """Explicit re-submit via :func:`retry_operation`."""
        return retry_operation(
            self.backend,
            factory=factory,
            job_type=self.job_type,
            idempotency_key=idempotency_key,
            tenant_id=tenant_id,
            auth_subject=auth_subject,
        )

    def is_terminal(self, state: JobState | str | object) -> bool:
        """Whether ``state`` stops monitoring (matches SSE terminal set)."""
        return is_terminal_job_state(state)

    def is_busy(self, state: JobState | str | object) -> bool:
        """Non-terminal states are treated as busy for control regions."""
        if isinstance(state, JobState):
            resolved = state
        elif isinstance(state, str):
            try:
                resolved = JobState(state)
            except ValueError:
                return False
        else:
            return False
        return resolved not in TERMINAL_JOB_STATES
