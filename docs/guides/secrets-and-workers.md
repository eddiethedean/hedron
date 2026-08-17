# Secrets, sessions, and workers

One page for the three facts that cause production tickets.

## Session secret

`HEDRON_SESSION_SECRET` is an **adopter convention**, not a framework env loader.
Hedron does **not** read it automatically. Pass the value into the constructor:

```python
import os
from hedron import Hedron

app = Hedron(
    title="Ops",
    security="standard",
    session_secret=os.environ["HEDRON_SESSION_SECRET"],
)
```

Flask uses `app.secret_key`. Django uses `SECRET_KEY`. Do not reuse a development
placeholder in production. Full env table: [Deployment](deployment.md).

## Sticky sessions are not a job store

Starlette/Flask/Django **signed cookie sessions** (the Hello default) live on the
browser or on one process’s memory. They are not Redis, and they do not share
in-process job status.

| Need | What to configure |
|---|---|
| Multiple HTTP workers, cookie sessions | Sticky sessions at the proxy **or** a shared server-side session store |
| Job status visible to every worker | Shared `JobBackend` (Redis / Celery / RQ) — [Celery / RQ](jobs-celery-rq.md) |
| CSRF cookies behind a subpath | `HEDRON_ROOT_PATH` before app import — [Mount](../api/MOUNT.md) |

In-memory `JobBackend` is fine for Hello and a single `uvicorn` worker. It is **not**
correct for `uvicorn --workers 4` or a replica set.

## FastAPI vs `Hedron()`

`Hedron` **is** a FastAPI app. Unrecognized constructor kwargs go to `FastAPI`.
Hedron owns security profiles, HTMX routes, CSRF, static mount, and optional Explorer.
Your lifespan is **composed** with Hedron’s, not replaced. OpenAPI inclusion follows
route decorator defaults (`include_in_schema`). Details: [Application](../api/HEDRON.md).

## See also

[Deployment](deployment.md) · [Ship](ship.md) · [Jobs](../api/JOBS.md) ·
[FAQ](faq.md)
