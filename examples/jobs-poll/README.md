# Jobs poll (Supported)

Minimal FastAPI + Hedron demo: enqueue work, poll status with `Poll` +
`job_status_response` until the job succeeds.

**Local only:** uses `InMemoryJobBackend` (does not span workers). For multi-worker
production, use Redis / Celery / RQ — see
[Celery / RQ + Redis](https://hedron.readthedocs.io/en/latest/guides/jobs-celery-rq/).

## Run

```bash
uv sync
uv run uvicorn app:app --app-dir examples/jobs-poll --reload
```

Open http://127.0.0.1:8000 — the status panel should move from Queued → Succeeded.

Docs: [Jobs API](https://hedron.readthedocs.io/en/latest/api/JOBS/) ·
[Live interaction](https://hedron.readthedocs.io/en/latest/guides/live-interaction/).
