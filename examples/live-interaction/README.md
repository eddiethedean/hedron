# Live interaction sample

First-party FastAPI demo for **polling** and **token streaming** (phase 0.10).
This is the clone-and-run companion to the
[live interaction guide](https://hedron.readthedocs.io/en/latest/guides/live-interaction/).

## Run

From the repository root:

```bash
uv sync
uv run uvicorn app:app --app-dir examples/live-interaction --reload
```

Open <http://127.0.0.1:8000/>. The clock panel polls every two seconds; the answer
region streams tokens on load.

## Scope

| Surface | In this sample |
|---|---|
| `Poll` + fragment refresh | Yes (Supported on all hosts) |
| `stream_tokens` / `TokenStream` | Yes (FastAPI flagship) |
| Job SSE / WebSocket / preload | Documented in the guide; not required here |

Use Flask/Django polling patterns from the guide when you are not on FastAPI.
