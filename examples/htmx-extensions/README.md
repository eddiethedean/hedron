# HTMX extension integration sample

First-party FastAPI demo for **declared HTMX extensions** (phase 0.48).
Polling remains the Supported production fallback. SSE and preload APIs stay
experimental.

## Run

From the repository root:

```bash
uv sync
uv run uvicorn app:app --app-dir examples/htmx-extensions --reload
```

Open <http://127.0.0.1:8000/>.

| Route | What it shows |
|---|---|
| `/` | Declared `sse`, `head-support`, and `preload` |
| `/opt-out` | `htmx_extensions=()` — zero extension bytes |
| `/events` | Experimental `sse_response` |
| `/next` | Cacheable GET preload destination |

Idiomorph / morph swap is **Deferred** and is not shipped.
