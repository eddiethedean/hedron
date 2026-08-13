# Jobs poll

Enqueue durable work and **poll** status (Supported path). SSE/WebSocket job helpers are
Experimental — prefer this recipe.

### Try it (simulated)

=== "Demo"

    Bounded job poll — each click advances one status step. Docs simulation.

    <!-- hedron-sim:jobs-poll -->

=== "Code"

    Real recipe listing using `enqueue_durable`, `Poll`, and scoped job status. The Demo tab is a simplified bounded view:

    ```python title="app.py"
    """Polling job status (Supported path). In-memory backend — local demo only."""

    from __future__ import annotations

    import threading
    import time

    from fastapi import HTTPException, Request

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
    ```

## Run without cloning the monorepo

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.34.0,<0.35" "uvicorn[standard]"
curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/jobs-poll/app.py -o app.py
uvicorn app:app --reload
```

## Run (monorepo)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/jobs-poll --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The panel should advance from
Queued → Succeeded within a couple of seconds.

## What it shows

- `enqueue_durable` + `InMemoryJobBackend` (local / single process only)
- `Poll` + `job_status_response` (HTTP **202** + `Retry-After`)
- Scoped `auth_subject` / `tenant_id` (fail-closed over HTTP)

!!! warning "Multi-worker"

    Replace `InMemoryJobBackend` with Redis / Celery / RQ before production. See
    [Celery / RQ + Redis](../guides/jobs-celery-rq.md) and [Jobs API](../api/JOBS.md).

Source: [`examples/jobs-poll`](https://github.com/eddiethedean/hedron/tree/main/examples/jobs-poll).
