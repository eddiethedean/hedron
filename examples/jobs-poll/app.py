"""Polling job status (Supported path). In-memory backend — local demo only."""

from __future__ import annotations

import threading
import time

from fastapi import HTTPException

from hedron import ComponentRef, Hedron, Page, Poll, Status, Text
from hedron.jobs import enqueue_durable, job_status_response
from hedron_core.jobs import InMemoryJobBackend, JobState, set_job_backend

app = Hedron(
    title="Jobs poll demo",
    security="standard",
    explorer="off",
    session_secret="replace-in-production",
)

backend = InMemoryJobBackend()
set_job_backend(backend)

JOB_STATUS = "/jobs/{job_id}/status"
AUTH = {"auth_subject": "demo-user", "tenant_id": "demo-tenant"}


def worker(job_id: str) -> None:
    time.sleep(1.0)
    backend.mark(job_id, JobState.SUCCEEDED, result={"ok": True})


@app.page("/")
def home() -> Page:
    job_id = enqueue_durable("demo", {"n": 1}, **AUTH)
    threading.Thread(target=worker, args=(job_id,), daemon=True).start()
    ref = ComponentRef(
        logical_id="job-status",
        path=JOB_STATUS.format(job_id=job_id),
        method="GET",
    )
    return Page(
        Text(f"Job {job_id} (poll every 2s — Supported path)"),
        Poll(ref=ref, interval_ms=2000, content=Status("Queued…")),
        title="Jobs poll",
    )


@app.get("/jobs/{job_id}/status")
def job_status(job_id: str):
    status = backend.get(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_status_response(status, **AUTH)
