# Celery / RQ + Redis jobs

Supported production recipe for durable [`JobBackend`](../api/JOBS.md) work. Hedron does
**not** run your workers — you supply Celery or RQ, a shared Redis client for status, and
authorization scope on submit + poll.

Prefer **polling** (`job_status_response` + `Poll`) as the Supported status UX. SSE remains
experimental.

## Prerequisites

- Shared Redis reachable from web workers and job workers
- Application-owned Celery app **or** RQ `Queue` + task registry
- `set_job_backend(...)` before enqueueing in each web process
- Matching `auth_subject` / `tenant_id` on submit and on HTTP status reads

Optional: `HEDRON_REDIS_URL` as your ops convention for the Redis URL (see
[Deployment](deployment.md) / [CONFIGURATION](../CONFIGURATION.md)).

## Celery

```python
import redis
from celery import Celery

from hedron_core.jobs import set_job_backend
from hedron_core.jobs_celery import CeleryJobBackend

celery_app = Celery("demo", broker="redis://localhost:6379/0")
redis_client = redis.Redis.from_url("redis://localhost:6379/1")

backend = CeleryJobBackend(
    celery_app,
    redis_client=redis_client,
    key_prefix="h1:job:",
    ttl_seconds=86400,
)
set_job_backend(backend)


@celery_app.task(name="demo.heavy")
def heavy(payload: dict) -> dict:
    # Application workers own progress. Look up the job id Celery assigned
    # (task_id == Hedron job_id) and mark terminal state for pollers:
    #   from hedron_core.jobs import JobState
    #   backend.mark(current_task.request.id, JobState.SUCCEEDED, result={...})
    return {"ok": True, "n": payload.get("n")}
```

Submit from a route with the **Celery task name** as `job_type`:

```python
from hedron.jobs import enqueue_durable

job_id = enqueue_durable(
    "demo.heavy",
    {"n": 1},
    auth_subject=user.id,
    tenant_id=tenant.id,
    idempotency_key=request.headers.get("Idempotency-Key"),
)
```

`CeleryJobBackend.submit` stores durable status in Redis, then
`celery_app.send_task(job_type, args=[payload], task_id=job_id)`. Cancel calls
`control.revoke` and updates status; revoke failures restore the prior snapshot.

## RQ

```python
import redis
from rq import Queue

from hedron_core.jobs import set_job_backend
from hedron_core.jobs_rq import RQJobBackend

conn = redis.Redis.from_url("redis://localhost:6379/0")
queue = Queue("hedron", connection=conn)


def heavy(payload: dict) -> dict:
    return {"ok": True, "n": payload.get("n")}


backend = RQJobBackend(
    queue,
    redis_client=conn,
    task_registry={"demo.heavy": heavy},
)
set_job_backend(backend)
```

Unknown `job_type` values raise `KeyError` at submit time. Status/idempotency use the same
Redis status store pattern as Celery.

## Redis-only backend

When you own the worker loop yourself (no Celery/RQ), use `RedisJobBackend` from
`hedron_core.jobs` with the same shared client. Workers call `backend.mark(...)` as they
progress.

## Multi-worker checklist

1. Every web process calls `set_job_backend` with the **same** Redis prefix/TTL.
2. Never use `InMemoryJobBackend` behind more than one process or in production gates.
3. Scope jobs with `auth_subject` / `tenant_id`; poll with the same credentials.
4. Run periodic `backend.cleanup_expired()` from a scheduled task.
5. Keep status UX on **polling** until your proxy/load story covers experimental SSE.

## See also

[Jobs API](../api/JOBS.md) · [Deployment](deployment.md) · [What’s ready](whats-ready.md) ·
[Live interaction](live-interaction.md)
