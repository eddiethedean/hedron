# Jobs poll (Supported)

Minimal FastAPI + Hedron demo: enqueue work, poll status with `Poll` +
`job_status_response` until the job succeeds.

**Local only:** uses `InMemoryJobBackend` (does not span workers). For multi-worker
production, use Redis / Celery / RQ — see
[Celery / RQ + Redis](https://hedron.readthedocs.io/en/latest/guides/jobs-celery-rq/).

## Run without cloning

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.61.0,<0.62" "uvicorn[standard]"
curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/jobs-poll/app.py -o app.py
uvicorn app:app --reload
```

## Run (monorepo)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/jobs-poll --reload
```

Open http://127.0.0.1:8000 — the status panel should move from Queued → Succeeded.

Docs: [Jobs API](https://hedron.readthedocs.io/en/latest/api/JOBS/) ·
[Live interaction](https://hedron.readthedocs.io/en/latest/guides/live-interaction/).
