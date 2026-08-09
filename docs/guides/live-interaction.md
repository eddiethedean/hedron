# Live interaction

The FastAPI flagship ships **experimental** live observation and navigation helpers
(`hedron.experimental`): HTMX SSE, focused streaming, page/session WebSocket channels,
and opt-in navigation preload. Chat/Dialog are beta. **Polling and ordinary HTTP remain
the Supported path** on every host — phase **0.24** Accepted **`polling_only`**.

Flask and Django adapters expose capability-labeled live helpers; **bounded polling is
the Supported fallback** behind buffering proxies. Prefer polling
([LIVE_DISPOSITION](../api/LIVE_DISPOSITION.md)). Live helpers remain experimental
(`hedron.experimental`).

!!! note "First-party live demo app"

    Start with the polling clock below (Supported on every host). For a clone-and-run
    FastAPI sample, see
    [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction)
    (**poll + token stream + SSE + Job SSE + WebSocket accept + preload**). Follow the
    sections below after you have a working page; the sample is the paste-and-run proof.

See also: [SSE API](../api/SSE.md) · [Streaming](../api/STREAMING.md) ·
[WebSocket channel](../api/WEBSOCKET_CHANNEL.md) · [Preload](../api/PRELOAD.md) ·
[Upgrade](upgrade.md).

## End-to-end: poll a clock (start here)

Polling works on FastAPI, Flask, and Django. Paste this into a FastAPI `app.py` first;
for Flask/Django use the same `Poll` component with `hedron_route` /
`hedron_view` + `interaction_response` (see [Flask](../getting-started/flask.md) /
[Django](../getting-started/django.md)).

### Try it (simulated)

=== "Demo"

    Bounded poll — each click advances one step (four steps, then wraps). Docs simulation.

    <!-- hedron-sim:live-poll -->

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

```python title="app.py"
from datetime import UTC, datetime

from hedron import (
    ComponentRef,
    FragmentRegion,
    Hedron,
    InteractionResult,
    Page,
    Poll,
    Stack,
    Text,
)

app = Hedron(title="Live clock", security="standard", session_secret="replace-in-production")

CLOCK = FragmentRegion(
    id="clock",
    selector="#clock",
    description="UTC clock panel",
)
CLOCK_REF = ComponentRef(
    logical_id="clock",
    path="/clock",
    target="#clock",
    swap="innerHTML",
)


def clock_text():
    now = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return Text(now)


@app.component("/clock", fragment_regions=(CLOCK,))
def clock_fragment() -> InteractionResult:
    return InteractionResult(
        content=clock_text(),
        region_id=CLOCK.id,
        explanation="Refresh the UTC clock region",
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Server time (polls every 2s)"),
            Poll(
                ref=CLOCK_REF,
                interval_ms=2000,
                target_id=CLOCK.id,
                content=clock_text(),
            ),
        ),
        title="Live clock",
    )
```

```bash
uv run uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The panel updates without a full
page reload. Stop polling by returning markup without `Poll` once a terminal state is
reached (job finished, error, etc.).

## End-to-end: stream tokens into a region

```python title="app.py"
from hedron import (
    FragmentRegion,
    Hedron,
    Page,
    Stack,
    Text,
    html,
)
from hedron.experimental import stream_tokens
from hedron_core.streaming import TokenStream

app = Hedron(title="Stream", security="standard", session_secret="replace-me")

ANSWER = FragmentRegion(id="answer", selector="#answer", description="Streamed answer")


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Streamed answer"),
            html.div(
                Text("Waiting…"),
                id=ANSWER.id,
                **{"hx-get": "/stream/answer", "hx-trigger": "load", "hx-swap": "innerHTML"},
            ),
        ),
        title="Stream",
    )


@app.get("/stream/answer")
def stream_answer():
    tokens = TokenStream(
        region_id=ANSWER.id,
        tokens=["Hello", ", ", "world", "!"],
    )
    return stream_tokens(tokens)
```

`StreamingComponentResponse` sets `X-Hedron-Stream-Region` and may prefix a fallback HTML
chunk when `fallback_html=` is provided.

## Job status over SSE (FastAPI)

Keep a **polling UI for correctness**. The cloneable sample under
[`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction)
enqueues a demo job, completes it in-process, and streams status via
`job_status_sse_response`. Minimal pattern:

```python
import threading
import time

from fastapi import Request

from hedron import Hedron, Page, Text
from hedron.experimental import job_status_sse_response
from hedron.jobs import enqueue_durable
from hedron_core.jobs import InMemoryJobBackend, JobState, set_job_backend

app = Hedron(title="Jobs", security="standard", session_secret="replace-me")
backend = InMemoryJobBackend()
set_job_backend(backend)


def _finish(job_id: str) -> None:
    time.sleep(0.5)
    backend.mark(job_id, JobState.SUCCEEDED, result={"ok": True})


@app.page("/")
def home() -> Page:
    job_id = enqueue_durable("demo", {"n": 1})
    threading.Thread(target=_finish, args=(job_id,), daemon=True).start()
    return Page(Text(f"Open /jobs/{job_id}/events"), title="Jobs")


@app.get("/jobs/{job_id}/events")
def events(job_id: str, request: Request):
    return job_status_sse_response(job_id, backend=backend, request=request)
```

Include the pinned extension when using `hx-ext="sse"` (PAGE responses already inject
known extensions when configured). Honor `Last-Event-ID` for reconnect. Treat the stream
as observation—polling remains Supported.

## Page/session WebSocket channel (FastAPI)

Server accept-path — the
[`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction)
sample mounts `/ws/page`. Pair with your own page that opens the socket.

```python
from fastapi import WebSocket

from hedron.experimental import accept_page_session_channel
from hedron_core.channel import PageSessionChannel

channel = PageSessionChannel(
    channel_id="demo",
    declared_regions=frozenset({"panel"}),
)


@app.websocket("/ws/page")
async def page_socket(websocket: WebSocket):
    await accept_page_session_channel(
        websocket,
        channel,
        allowed_origins=frozenset({"http://127.0.0.1:8000"}),
    )
```

Missing `Origin` is denied by default. Include `ALLOW_MISSING_ORIGIN` only for trusted
non-browser clients. Push updates with `send_region_update(websocket, update)`.

## Chat and Dialog

`Dialog`, `ChatMessage`, and `ChatInput` are ordinary components for accessible overlays
and message UIs. They do not require SSE or WebSockets; wire them to HTMX routes or live
transports only when you need push updates.

## Navigation preload (opt-in, FastAPI)

Preload is off until you enable an explicit policy. The live sample applies headers on
`/next`. Apply headers to a real response object:

```python
from fastapi.responses import HTMLResponse

from hedron.experimental import NavigationPreloadPolicy, apply_preload_headers, evaluate_preload_request

policy = NavigationPreloadPolicy(enabled=True, max_concurrent=2)


@app.page("/next")
def next_page(request):
    decision = evaluate_preload_request(request, policy)
    response = HTMLResponse("<!doctype html><title>Next</title><p>Next</p>")
    return apply_preload_headers(response, decision)
```

Do not enable speculative preload for authenticated mutation endpoints.

## Security notes

- Live transports inherit CSRF, session, and auth from the host app.
- Prefer private, authenticated channels; never put secrets in SSE event payloads.
- WebSocket origin allowlists fail closed.
- Treat live delivery as best-effort observation; keep HTTP fallbacks.

## Troubleshooting

| Symptom | Fix |
|---|---|
| SSE never connects | Confirm FastAPI route returns `SseResponse` / `job_status_sse_response`; check proxies buffer SSE (`X-Accel-Buffering: no` is set) |
| Explorer missing live traces | Explorer live traces remain owned Deferred for 0.10.x — use curl/TestClient |
| Flask/Django looking for SSE helpers | Use polling; helpers are FastAPI-flagship only |
| Preload rejected | Check `NavigationPreloadPolicy(enabled=True)` and same-origin rules |
| Want a clone-and-run live demo | Use [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction) (poll + stream + SSE + Job SSE + WS + preload) or the poll/stream snippets above |
