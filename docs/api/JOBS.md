# Job interaction contracts

!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).
    Durable `JobBackend` + **polling** are Supported. Job SSE helpers are **experimental**
    (`hedron.experimental` / `job_status_sse_response`) — see [What’s ready](../guides/whats-ready.md).

**Status:** Shipped (`JobBackend` + polling) · Job SSE **experimental** on FastAPI

`JobBackend` is a protocol over application-operated durable work. Hedron does not ship a
queue, worker fleet, scheduler, result database, or retry service.

## Public helpers

| Symbol | Import | Role |
|---|---|---|
| `JobBackend` / `JobState` / `JobStatus` / `JobHandle` | `hedron_core.jobs` | Protocol + status types |
| `InMemoryJobBackend` / `RedisJobBackend` | `hedron_core.jobs` | In-process (tests) and Redis-durable backends |
| `CeleryJobBackend` | `hedron_core.jobs_celery` | Celery + Redis status bridge |
| `RQJobBackend` | `hedron_core.jobs_rq` | RQ + Redis status bridge |
| `set_job_backend` / `get_job_backend` | `hedron_core.jobs` | Process-local default backend |
| `enqueue_durable` | `hedron.jobs` | Submit via the configured backend; returns `job_id` |
| `job_status_response` | `hedron.jobs` | HTML **202** status fragment + `Retry-After` (Supported) |
| `schedule_post_response` | `hedron.jobs` | FastAPI `BackgroundTasks` only — **not** durable |
| `TaskFlow` / `JobScope` / `PollPolicy` | `hedron` | Progressive durable submit/status/cancel/result UI (0.58; API `beta`) |
| `job_status_sse_response` | `hedron.experimental` | SSE observation until terminal (**experimental**) |

Production recipe: [Celery / RQ + Redis](../guides/jobs-celery-rq.md).

## Parameters

| Helper | Key parameters |
|---|---|
| `enqueue_durable(job_type, payload, *, auth_subject=…, tenant_id=…, idempotency_key=…)` | Job type + JSON-ish payload; scope with subject/tenant for HTTP observation |
| `job_status_response(status, *, auth_subject=…, tenant_id=…)` | `JobStatus` from backend `get`; same scope as enqueue |
| `set_job_backend(backend)` | Process-local `JobBackend` (set on every worker) |
| `JobBackend.submit` / `get` / `request_cancel` | See protocol table below |

## Returns

| Helper | Returns | Errors / notes |
|---|---|---|
| `enqueue_durable(...)` | `str` job id | Backend/auth failures raise or return host errors per backend |
| `job_status_response(...)` | HTML response **202** + `Retry-After` + status fragment | Missing/unauthorized job → fail closed (typically **404** / **403**) |
| `set_job_backend` / `get_job_backend` | `None` / current `JobBackend` | Process-local; set on every worker |
| `schedule_post_response` | `None` | FastAPI `BackgroundTasks` only — not durable |
| `JobBackend.submit` | `JobHandle` | See protocol table |
| `JobBackend.get` | `JobStatus \| None` | `None` when missing or unauthorized |
| `job_status_sse_response` | SSE response (**experimental**) | Prefer polling in production |

## `JobBackend` protocol

Implementations must provide:

| Method | Contract |
|---|---|
| `submit(job_type, payload, *, idempotency_key=None, tenant_id=None, auth_subject=None) -> JobHandle` | Enqueue work; return an opaque `job_id`. Honor idempotency within auth/tenant scope when a key is supplied. |
| `get(job_id, *, auth_subject=None, tenant_id=None) -> JobStatus \| None` | Lookup status; return `None` when missing or unauthorized for the caller scope. |
| `request_cancel(job_id, *, auth_subject=None, tenant_id=None) -> bool` | Request cancellation; return whether the request was accepted. |
| `cleanup_expired(*, older_than_seconds=86400) -> int` | Drop retained records older than the TTL window; return count removed. |
| `mark(job_id, state, *, result=None, error=None) -> JobStatus \| None` | Worker/application transition helper (queued → running → terminal). |

`JobState` values: `queued`, `running`, `succeeded`, `failed`, `cancelled`.
`JobStatus.cancel_requested` records a cancel ask while work may still be finishing.
Retry ownership, maximum attempts, result serialization, and backend-unavailable behavior
remain application/backend policy.

HTTP observers use `job_authorized_http`: unscoped jobs are **not** readable over HTTP
helpers (fail closed). Pass credentials that **exactly** match every scope dimension on
the job (including `None` on unset dimensions). A tenant-only job does **not** authorize
an arbitrary `auth_subject` in that tenant — pass `auth_subject=None` with the matching
`tenant_id`, or scope jobs with both subject and tenant at enqueue time. Prefer
`backend.get(job_id, **scope)` plus `job_status_response(status, **scope)` rather than
unrestricted `get` + hardcoded auth kwargs.

## InferencePolicy cancel (0.18)

`InferencePolicy.request_cancel(request_id, *, auth_subject=..., tenant_id=..., backend=...)`
layers admission/queue cancel on top of this contract: the caller must match the
request's stored auth scope (same fail-closed rules as `job_authorized_http`). Queued
requests are dropped locally; accepted requests map to a backend `job_id` and call
`JobBackend.request_cancel` with the **caller** identity (never the stored owner),
releasing inflight concurrency capacity. See [Inference API](INFERENCE.md).

## HTTP and HTMX behavior (Supported path)

1. Submit with `enqueue_durable(...)` (or `backend.submit(...)`).
2. Return an addressable status URL and a **`Poll`** (or ordinary refresh) against that URL.
3. Serve status with `job_status_response(...)` → HTTP **202** + `Retry-After` + fragment HTML
   until the job is terminal.
4. Stop polling on success/failure/cancel; keep native HTML usable without HTMX.

Optional **SSE** observation (`job_status_sse_response`) is experimental on FastAPI only.
Polling remains the Supported baseline on every host, including Flask/Django.

`schedule_post_response` / host `BackgroundTasks` are for small post-response work only —
they do **not** implement the durable protocol.

## `TaskFlow` (0.58)

Compose submit/status/cancel/result surfaces around an application-operated
`JobBackend`. Does not run workers or become a scheduler.

```python
from fastapi import Depends
from hedron import JobScope, TaskFlow, Text

reports = TaskFlow(
    name="report",
    input_model=ReportRequest,
    job_type="build-report",
    payload=lambda data: {"label": data.label},
    scope=lambda: JobScope(auth_subject="dev", tenant_id="local"),
    authorize_submit=Depends(allow),
    result=lambda result: Text(str(result)),
)
app.include(reports)
```

Recipe: [Jobs poll](../examples/jobs-poll.md). Scaffold: `hedron new NAME --template task`.

## End-to-end example (polling — Supported)

```python
import threading
import time

from fastapi import HTTPException

from hedron import ComponentRef, Hedron, Page, Poll, Status, Text
from hedron.jobs import enqueue_durable, job_status_response
from hedron_core.jobs import InMemoryJobBackend, JobState, set_job_backend

app = Hedron(
    title="Jobs demo",
    security="standard",
    explorer="off",
    session_secret="replace-in-production",
)
backend = InMemoryJobBackend()
set_job_backend(backend)

JOB_STATUS = "/jobs/{job_id}/status"


def worker(job_id: str) -> None:
    time.sleep(0.5)
    backend.mark(job_id, JobState.SUCCEEDED, result={"ok": True})


@app.page("/")
def home():
    job_id = enqueue_durable(
        "demo",
        {"n": 1},
        auth_subject="demo-user",
        tenant_id="demo-tenant",
    )
    threading.Thread(target=worker, args=(job_id,), daemon=True).start()
    ref = ComponentRef(
        logical_id="job-status",
        path=JOB_STATUS.format(job_id=job_id),
        method="GET",
    )
    return Page(
        Text(f"Job {job_id}"),
        Poll(ref=ref, interval_ms=2000, content=Status("Queued…")),
    )


@app.get("/jobs/{job_id}/status")
def job_status(job_id: str):
    status = backend.get(
        job_id,
        auth_subject="demo-user",
        tenant_id="demo-tenant",
    )
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_status_response(
        status,
        auth_subject="demo-user",
        tenant_id="demo-tenant",
    )
```

Use the same `auth_subject` / `tenant_id` on `get` and `job_status_response` as on
`enqueue_durable`. Unscoped `backend.get(job_id)` is for worker/internal paths only —
do not copy that pattern into HTTP poll handlers.

For multi-worker production, replace `InMemoryJobBackend` with
[`RedisJobBackend`](../guides/jobs-celery-rq.md), `CeleryJobBackend`, or `RQJobBackend`.

## Experimental SSE sample

```python
from fastapi import Request
from hedron.experimental import job_status_sse_response

@app.get("/jobs/{job_id}/events")
def events(job_id: str, request: Request):
    return job_status_sse_response(
        job_id,
        backend=backend,
        request=request,
        auth_subject="demo-user",
        tenant_id="demo-tenant",
    )
```

Runnable live sample (includes experimental SSE):
[`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction).

## Errors

| Condition | Behavior |
|---|---|
| Unknown / unauthorized job (HTTP poll) | `job_status_response` → **404** (same shape; no enumeration) |
| Auth/tenant mismatch (SSE) | **403** / fail-closed per helper |
| Backend unavailable | Application/backend-defined; do not cache failures as success |
| Cancel unsupported / revoke failed | Backend returns `False`; UI must degrade |
| Production without durable backend | `production_gate` may refuse in-memory defaults |

## See also

[Celery / RQ + Redis](../guides/jobs-celery-rq.md) · [SSE](SSE.md) ·
[Live interaction](../guides/live-interaction.md) · [STABILITY](STABILITY.md) ·
[Deployment](../guides/deployment.md)
