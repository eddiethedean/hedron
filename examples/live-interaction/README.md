# Live interaction sample

First-party FastAPI demo for **polling** (Supported) plus **experimental** token
streaming, SSE, Job SSE, WebSocket page channel, and navigation preload. Companion to
the [live interaction guide](https://hedron.readthedocs.io/en/latest/guides/live-interaction/)
and [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).

Import experimental helpers from `hedron.experimental` (as this sample does).

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

| Surface | In this sample | Maturity |
|---|---|---|
| `Poll` + fragment refresh | Yes | **Supported** on all hosts |
| `stream_tokens` / `TokenStream` | Yes | **Experimental** (FastAPI) |
| `sse_response` / `SseEvent` | Yes (`/sse/ping`) | **Experimental** (FastAPI) |
| Job SSE (`job_status_sse_response`) | Yes (`/jobs/{id}/events`) | **Experimental** (FastAPI) |
| WebSocket page/session channel | Yes (`/ws/page`) | **Experimental** (FastAPI) |
| Navigation preload | Yes (`/next`) | **Experimental** (FastAPI) |

Prefer polling behind load balancers. Phase **0.24** Accepted **`polling_only`**:
live SSE/WS helpers remain **experimental**; polling is the Supported production story
([LIVE_DISPOSITION](https://hedron.readthedocs.io/en/latest/api/LIVE_DISPOSITION/)).
