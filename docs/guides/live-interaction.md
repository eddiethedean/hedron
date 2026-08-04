# Live interaction

Phase **0.10** adds official live observation and navigation helpers on the FastAPI
flagship: HTMX SSE, focused streaming, page/session WebSocket channels, Chat/Dialog
components, and opt-in navigation preload. Polling and ordinary HTTP remain Supported
fallbacks on every host.

Flask and Django adapters do **not** ship these FastAPI helpers; use bounded polling
there until later native depth (0.11).

See also: [SSE API](../api/SSE.md) · [Streaming](../api/STREAMING.md) ·
[WebSocket channel](../api/WEBSOCKET_CHANNEL.md) · [Preload](../api/PRELOAD.md) ·
[Upgrade](upgrade.md).

## Job status over SSE

Keep a polling UI for correctness. Optionally observe the same job with SSE:

```python
from fastapi import Request

from hedron import Hedron, Page, Text, job_status_sse_response

app = Hedron(title="Jobs", security="standard", session_secret="replace-me")


@app.page("/")
def home() -> Page:
    return Page(Text("Submit work, then open /jobs/{id}/events"), title="Jobs")


@app.get("/jobs/{job_id}/events")
def job_events(job_id: str, request: Request):
    return job_status_sse_response(job_id, request=request, poll_interval_seconds=0.5)
```

Include the pinned extension when using `hx-ext="sse"` (PAGE responses already inject
known extensions when configured). Honor `Last-Event-ID` for reconnect. Stop treating the
stream as the only correctness path—polling remains Supported.

## Focused streaming

Stream HTML into an addressable region without a full page rerun:

```python
from hedron import stream_tokens
from hedron_core.streaming import TokenStream

tokens = TokenStream(region_id="answer", tokens=["Hello", " ", "world"])


@app.get("/stream/answer")
def stream_answer():
    return stream_tokens(tokens)
```

`StreamingComponentResponse` sets `X-Hedron-Stream-Region` and may prefix a fallback HTML
chunk when `fallback_html=` is provided.

## Page/session WebSocket channel

Use WebSockets for bounded region updates after origin checks:

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

## Navigation preload (opt-in)

Preload is off until you enable an explicit policy:

```python
from hedron import NavigationPreloadPolicy, apply_preload_headers, evaluate_preload_request

policy = NavigationPreloadPolicy(enabled=True, max_concurrent=2)


@app.page("/next")
def next_page(request):
    decision = evaluate_preload_request(request, policy)
    response = ...  # your PageResponse / HTML response
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
