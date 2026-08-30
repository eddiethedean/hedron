"""Polling job status (Supported path). In-memory backend — local demo only."""

from __future__ import annotations

import threading
import time

from fastapi import HTTPException, Request

from hedron import ComponentRef, Hedron, Page, Poll, Status, Text
from hedron.jobs import enqueue_durable, job_status_response
from hedron_core.jobs import InMemoryJobBackend, JobState

backend = InMemoryJobBackend()

app = Hedron(
    title="Jobs poll demo",
    security="standard",
    explorer="off",
    session_secret="replace-in-production",
    job_backend=backend,
)

JOB_STATUS = "/jobs/{job_id}/status"
DEMO_SUBJECT = "demo-user"
DEMO_TENANT = "demo-tenant"


def _demo_scope(request: Request) -> dict[str, str]:
    """Session-backed demo identity (replace with real auth in production)."""
    session = request.session
    subject = session.get("auth_subject")
    tenant = session.get("tenant_id")
    if not isinstance(subject, str) or not subject:
        subject = DEMO_SUBJECT
        session["auth_subject"] = subject
    if not isinstance(tenant, str) or not tenant:
        tenant = DEMO_TENANT
        session["tenant_id"] = tenant
    return {"auth_subject": subject, "tenant_id": tenant}


def worker(job_id: str) -> None:
    time.sleep(1.0)
    backend.mark(job_id, JobState.SUCCEEDED, result={"ok": True})


@app.page("/")
def home(request: Request) -> Page:
    scope = _demo_scope(request)
    job_id = enqueue_durable("demo", {"n": 1}, **scope)
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
def job_status(job_id: str, request: Request):
    scope = _demo_scope(request)
    status = backend.get(job_id, **scope)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_status_response(status, **scope)
