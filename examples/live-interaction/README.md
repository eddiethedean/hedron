# Live interaction sample

First-party FastAPI demo for **polling**, **token streaming**, and a minimal **SSE**
endpoint (phase 0.10). Companion to the
[live interaction guide](https://hedron.readthedocs.io/en/latest/guides/live-interaction/).

## Run

From the repository root:

```bash
uv sync
uv run uvicorn app:app --app-dir examples/live-interaction --reload
```

Open <http://127.0.0.1:8000/>. The clock panel polls every two seconds; the answer
region streams tokens on load. Open <http://127.0.0.1:8000/sse/ping> (or an
`EventSource`) to see a short SSE sequence.

## Scope

| Surface | In this sample | Elsewhere |
|---|---|---|
| `Poll` + fragment refresh | Yes (Supported on all hosts) | — |
| `stream_tokens` / `TokenStream` | Yes (FastAPI flagship) | Guide |
| `sse_response` / `SseEvent` | Yes (minimal `/sse/ping`) | Guide |
| Job SSE (`job_status_sse_response`) | No | [Live interaction guide](https://hedron.readthedocs.io/en/latest/guides/live-interaction/) (API Supported) |
| WebSocket page/session channel | No | Same guide (API Supported) |
| Navigation preload | No | Same guide (API Supported) |

This sample is the **learning-path** proof for poll + stream. Treat Job SSE / WebSocket /
preload as guide-and-API surfaces until you extend the sample or wait for a fuller demo.

Use Flask/Django polling patterns from the guide when you are not on FastAPI.
