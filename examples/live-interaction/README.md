# Live interaction sample

First-party FastAPI demo for **polling**, **token streaming**, **SSE**, **Job SSE**,
**WebSocket page channel**, and **navigation preload** (phase 0.10). Companion to the
[live interaction guide](https://hedron.readthedocs.io/en/latest/guides/live-interaction/).

## Run

From the repository root:

```bash
uv sync
uv run uvicorn app:app --app-dir examples/live-interaction --reload
```

Open <http://127.0.0.1:8000/>. The clock panel polls every two seconds; the answer
region streams tokens on load. Follow the on-page links for `/sse/ping`, Job SSE events,
`/ws/page`, and `/next` (preload headers).

## Scope

| Surface | In this sample |
|---|---|
| `Poll` + fragment refresh | Yes (Supported on all hosts) |
| `stream_tokens` / `TokenStream` | Yes (FastAPI flagship) |
| `sse_response` / `SseEvent` | Yes (`/sse/ping`) |
| Job SSE (`job_status_sse_response` + `InMemoryJobBackend`) | Yes (`/jobs/{id}/events`) |
| WebSocket page/session channel | Yes (`/ws/page` accept path) |
| Navigation preload | Yes (`/next`) |

Use Flask/Django polling patterns from the guide when you are not on FastAPI. Prefer
polling behind load balancers until your own ops evidence covers SSE/WS backpressure.
