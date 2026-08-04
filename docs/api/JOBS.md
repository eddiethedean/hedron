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

## Example (in-memory backend + SSE)

```python
from fastapi import Request

from hedron import job_status_sse_response
from hedron_core.jobs import InMemoryJobBackend, set_job_backend

backend = InMemoryJobBackend()
set_job_backend(backend)


@app.get("/jobs/{job_id}/events")
def events(job_id: str, request: Request):
    return job_status_sse_response(job_id, backend=backend, request=request)
```

## Errors

| Condition | Behavior |
|---|---|
| Unknown job id | SSE/status handlers emit missing/terminal sequence or 404 per app policy |
| Backend unavailable | Application/backend-defined; do not cache failures as success |
| Cancel unsupported | Backend reports capability; UI must degrade |

## See also

[Jobs implementation notes in STABILITY](STABILITY.md) · [Cache](CACHE.md)
