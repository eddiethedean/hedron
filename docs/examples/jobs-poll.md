# Jobs poll

Enqueue durable work and **poll** status (Supported path). SSE/WebSocket job helpers are
Experimental — prefer this recipe.

## Run without cloning the monorepo

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.19.0,<0.20" "uvicorn[standard]"
# Copy https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/jobs-poll/app.py → app.py
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
