---
status: shipped
---

# Job interaction contracts

!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).
    Durable `JobBackend` shipped in 0.7; official SSE observation is Supported in **0.10**.

**Status:** Shipped (`JobBackend` + polling) · SSE observation Supported on FastAPI (0.10)

`JobBackend` is a protocol over application-operated durable work. Hedron does not ship a
queue, worker fleet, scheduler, result database, or retry service.

## Public helpers

| Symbol | Import | Role |
|---|---|---|
| `InMemoryJobBackend` / `set_job_backend` / `get_job_backend` | `hedron_core.jobs` | Test/demo backend + process-local default |
| `enqueue_durable` | `hedron.jobs` | Submit via the configured backend; returns `job_id` |
| `job_status_response` | `hedron.jobs` | HTML 202 status fragment + `Retry-After` |
| `schedule_post_response` | `hedron.jobs` | FastAPI `BackgroundTasks` only — **not** durable |
| `job_status_sse_response` | `hedron` / `hedron.sse` | SSE observation until terminal |

## Contract

A backend declares capabilities and supports explicit submission, status lookup,
result/error metadata, retention/expiry, and cancellation requests where available.
Submission carries an application-defined task description, authorization/tenant scope, and
optional idempotency key. Job identifiers are opaque, bounded, and safe for addressable
status URLs.

Portable states: queued, running, succeeded, failed, cancellation-requested, cancelled,
expired. Retry ownership, maximum attempts, result serialization, cleanup, and
backend-unavailable behavior are explicit backend/application policies.

## HTTP and HTMX behavior

Accepted work returns HTTP 202 with an addressable authorized status resource and
`Retry-After`. The default component uses **bounded polling**, accessible status
announcements, terminal stop behavior, and an ordinary-HTML fallback.

Optional **SSE** observation uses the same status contract via
`job_status_sse_response` on the FastAPI flagship ([SSE](SSE.md),
[live interaction](../guides/live-interaction.md)). Polling remains the required Supported
baseline on every host, including Flask/Django.

Host-framework background helpers are limited to small post-response work and do not
implement the durable protocol.

## End-to-end example (in-memory backend + SSE)

```python
import threading
import time

from fastapi import Request

from hedron import job_status_sse_response
from hedron.jobs import enqueue_durable
from hedron_core.jobs import InMemoryJobBackend, JobState, set_job_backend

backend = InMemoryJobBackend()
set_job_backend(backend)


def worker(job_id: str) -> None:
    time.sleep(0.5)
    backend.mark(job_id, JobState.SUCCEEDED, result={"ok": True})


@app.page("/")
def home():
    job_id = enqueue_durable("demo", {"n": 1})
    threading.Thread(target=worker, args=(job_id,), daemon=True).start()
    return f"Observe /jobs/{job_id}/events"


@app.get("/jobs/{job_id}/events")
def events(job_id: str, request: Request):
    return job_status_sse_response(job_id, backend=backend, request=request)
```

Runnable sample: [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction).

## Parameters (`job_status_sse_response`)

| Parameter | Type | Description |
|---|---|---|
| `job_id` | `str` | Opaque job identifier from `enqueue_durable` / `JobBackend.submit` |
| `backend` | `JobBackend \| None` | Defaults to `get_job_backend()` |
| `request` | `Request \| None` | Used for `Last-Event-ID` resume |
| `html_message` | callable \| None | Custom HTML body for status events |
| `poll_interval_seconds` | `float \| None` | Backend poll cadence while open |
| `auth_subject` / `tenant_id` | `str \| None` | Required when the stored job scoped those fields |

## Errors

| Condition | Behavior |
|---|---|
| Unknown job id | `404` from `job_status_sse_response` |
| Auth/tenant mismatch | `403` |
| Backend unavailable | Application/backend-defined; do not cache failures as success |
| Cancel unsupported | Backend reports capability; UI must degrade |

## See also

[SSE](SSE.md) · [Live interaction](../guides/live-interaction.md) · [STABILITY](STABILITY.md) · [Cache](CACHE.md)
