# Jobs poll

Enqueue durable work and **poll** status (Supported path). SSE/WebSocket job helpers are
Experimental — prefer this recipe.

### Try it (simulated)

=== "Demo"

    Bounded job poll — each click advances one status step. Docs simulation.

    <!-- hedron-sim:jobs-poll -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import Hedron, Page, Stack, html, swap

    app = Hedron(
        title="Job poll",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    job = app.region("job-panel", description="Job status")

    _STEPS = [
        ("Queued", "Waiting for worker"),
        ("Running", "Step 1 of 2"),
        ("Running", "Step 2 of 2"),
        ("Complete", "84 records imported; polling stopped"),
    ]
    _tick = 0


    def panel(state: str, detail: str):
        return html.div(
            html.strong(state),
            html.span(detail),
            id=job.id,
            role="status",
            aria={"live": "polite"},
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                panel("Idle", "Click to start a bounded poll cycle."),
                html.button(
                    "Start job poll",
                    type="button",
                    **{
                        "hx-get": "/jobs/42",
                        "hx-target": job.selector,
                        "hx-swap": "outerHTML",
                    },
                ),
            ),
            title="Poll",
        )


    @app.fragment("/jobs/42", region=job)
    def job_tick():
        global _tick
        state, detail = _STEPS[min(_tick, len(_STEPS) - 1)]
        _tick = min(_tick + 1, len(_STEPS) - 1)
        return swap(panel(state, detail))
    ```

## Run without cloning the monorepo

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.21.0,<0.22" "uvicorn[standard]"
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
