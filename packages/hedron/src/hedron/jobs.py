"""FastAPI job helpers — BackgroundTasks vs durable JobBackend."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from fastapi import BackgroundTasks, HTTPException
from starlette.responses import HTMLResponse

from hedron_core.jobs import JobStatus, get_job_backend, job_authorized_http, job_status_interaction
from hedron_core.rendering import RenderMode, render
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "enqueue_durable",
    "schedule_post_response",
    "job_status_response",
]


def schedule_post_response(tasks: BackgroundTasks, fn: Callable[..., Any], *args: Any) -> None:
    """Schedule small non-durable post-response work (NOT a JobBackend)."""
    tasks.add_task(fn, *args)


def enqueue_durable(
    job_type: str,
    payload: Mapping[str, JsonValue],
    *,
    idempotency_key: str | None = None,
    tenant_id: str | None = None,
    auth_subject: str | None = None,
) -> str:
    handle = get_job_backend().submit(
        job_type,
        payload,
        idempotency_key=idempotency_key,
        tenant_id=tenant_id,
        auth_subject=auth_subject,
    )
    return handle.job_id


def job_status_response(
    job_status: JobStatus,
    *,
    auth_subject: str | None = None,
    tenant_id: str | None = None,
) -> HTMLResponse:
    if not job_authorized_http(job_status, auth_subject=auth_subject, tenant_id=tenant_id):
        raise HTTPException(status_code=403, detail="Job access forbidden")
    result = job_status_interaction(job_status)
    assert result.content is not None
    rendered = render(result.content, mode=RenderMode.FRAGMENT)
    headers = {
        "Retry-After": str(job_status.retry_after),
        "Cache-Control": "private, no-store",
    }
    return HTMLResponse(rendered.html, status_code=202, headers=headers)
