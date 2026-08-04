# Live interaction

Phase **0.10** adds official live observation and navigation helpers on the FastAPI
flagship: HTMX SSE, focused streaming, page/session WebSocket channels, Chat/Dialog
components, and opt-in navigation preload. **Polling and ordinary HTTP remain
Supported fallbacks** on every host—and they are the right place to start.

Flask and Django adapters do **not** ship these FastAPI helpers; use bounded polling
there until later native depth (0.11).

!!! note "First-party live demo app"

    Start with the polling clock below (Supported on every host). For a clone-and-run
    FastAPI sample (poll + token stream + `/sse/ping`), see
    [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction)
    (`EXAMPLES-10-001` Verified). Advanced WebSocket / preload / job-status SSE helpers
    below are FastAPI-only and assume you already have a working page.

See also: [SSE API](../api/SSE.md) · [Streaming](../api/STREAMING.md) ·
[WebSocket channel](../api/WEBSOCKET_CHANNEL.md) · [Preload](../api/PRELOAD.md) ·
[Upgrade](upgrade.md).

## End-to-end: poll a clock (start here)

Polling works on FastAPI, Flask, and Django. Paste this into `app.py`:

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

app = Hedron(title="Live clock", security="standard", session_secret="replace-me")

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
    stream_tokens,
)
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

## Job status over SSE (FastAPI — API-oriented)

Keep a **polling UI for correctness**. The cloneable sample under
[`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction)
covers poll + token stream + `/sse/ping`. Job-status SSE below is an API sketch — wire it
only after you have a real worker; it is not a full paste-and-run app.

```python
from fastapi import Request

from hedron import Hedron, Page, Text, job_status_sse_response
from hedron.jobs import enqueue_durable

app = Hedron(title="Jobs", security="standard", session_secret="replace-me")


@app.page("/")
def home() -> Page:
    job_id = enqueue_durable("demo", {"n": 1})
    return Page(
        Text(f"Observing job {job_id} — open /jobs/{job_id}/events"),
        title="Jobs",
    )


@app.get("/jobs/{job_id}/events")
def job_events(job_id: str, request: Request):
    return job_status_sse_response(job_id, request=request, poll_interval_seconds=0.5)
```

Include the pinned extension when using `hx-ext="sse"` (PAGE responses already inject
known extensions when configured). Honor `Last-Event-ID` for reconnect. Treat the stream
as observation—polling remains Supported.

## Page/session WebSocket channel (FastAPI — API-oriented)

Server accept-path only — pair with your own page that opens the socket. Not covered
end-to-end by `examples/live-interaction`.

```python
from fastapi import WebSocket

from hedron import accept_page_session_channel
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

## Navigation preload (opt-in, FastAPI — API-oriented)

Preload is off until you enable an explicit policy. Apply headers to a real response
object. Not part of the first-party live sample app.

```python
from fastapi.responses import HTMLResponse

from hedron import NavigationPreloadPolicy, apply_preload_headers, evaluate_preload_request

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
| Want a clone-and-run live demo | Use [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction) (poll + stream + `/sse/ping`) or the poll/stream snippets above |
