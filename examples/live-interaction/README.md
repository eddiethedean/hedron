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

| Surface | In this sample |
|---|---|
| `Poll` + fragment refresh | Yes (Supported on all hosts) |
| `stream_tokens` / `TokenStream` | Yes (FastAPI flagship) |
| `sse_response` / `SseEvent` | Yes (minimal `/sse/ping`) |
| Job SSE / WebSocket / preload | Documented in the guide |

Use Flask/Django polling patterns from the guide when you are not on FastAPI.
