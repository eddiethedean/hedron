from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from hedron import PollPolicy, TaskFlow
from hedron.jobs.scope import JobScope
from hedron_core.jobs import JobBackend, JobStatus
from hedron_core.live import SseEvent, job_status_sse_events

__all__ = ["JobBackend", "JobFlow", "JobScope", "job_status_events"]


class JobFlow:
    """Thin Edron constructor for native Hedron task flows."""

    def __init__(
        self,
        *,
        name: str,
        input_model: type[Any],
        job_type: str,
        payload: Callable[[Any], Mapping[str, Any]],
        idempotency_key: Callable[[Any], str | None] | None = None,
        backend: Any = None,
        scope: Any,
        result: Callable[..., Any],
        authorize_submit: Any = None,
        authorize_cancel: Any = None,
        poll_interval_ms: int = 2000,
        retry_attempts: int = 0,
        result_ttl_seconds: int = 86400,
    ) -> None:
        self.name = name
        self.input_model = input_model
        self.job_type = job_type
        self.payload = payload
        self.idempotency_key = idempotency_key
        self.backend = backend
        self.scope = scope
        self.result = result
        self.authorize_submit = authorize_submit
        self.authorize_cancel = authorize_cancel
        self.poll_interval_ms = poll_interval_ms
        if retry_attempts < 0 or retry_attempts > 10:
            raise ValueError("retry_attempts must be between 0 and 10")
        if result_ttl_seconds < 60 or result_ttl_seconds > 2_592_000:
            raise ValueError("result_ttl_seconds must be between 60 and 2592000")
        self.retry_attempts = retry_attempts
        self.result_ttl_seconds = result_ttl_seconds

    def to_bundle(self) -> Any:
        native = TaskFlow(
            name=self.name,
            input_model=self.input_model,
            job_type=self.job_type,
            payload=self.payload,
            idempotency_key=self.idempotency_key,
            scope=self.scope,
            authorize_submit=self.authorize_submit,
            authorize_cancel=self.authorize_cancel,
            result=self.result,
            poll=PollPolicy(interval_ms=self.poll_interval_ms),
            backend=self.backend,
            retry_attempts=self.retry_attempts,
            result_ttl_seconds=self.result_ttl_seconds,
        )
        return native.to_bundle()


def job_status_events(
    status: JobStatus,
    *,
    message_html: str,
    event_id: str | None = None,
) -> list[SseEvent]:
    """Project an authorized native job status into bounded SSE events.

    Authorization remains the responsibility of the native status route; this
    helper only formats an already-authorized status and never looks up a job.
    """
    terminal = status.state.value in {"succeeded", "failed", "cancelled"}
    return job_status_sse_events(
        job_id=status.job_id,
        state=status.state.value,
        message_html=message_html,
        event_id=event_id,
        retry_ms=max(1000, min(60_000, int(status.retry_after * 1000))),
        terminal=terminal,
    )
