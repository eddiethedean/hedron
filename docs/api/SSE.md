---
status: shipped
---

# SSE responses


!!! note "Stability"

    Classifications live in [STABILITY.md](STABILITY.md). Official HTMX SSE observation is
    **experimental** (`hedron.experimental`) until Deferred ops gates
    (`BROWSER-10-001`, `PERF-10-001`, `LIVE-011-BROWSER`) close. Polling remains the
    Supported production fallback.

**Status:** Shipped in `0.10.0`

Helpers in `hedron`: `SseResponse`, `sse_response`, `job_status_sse_response`,
`extension_script_tags`. Framing primitives (`SseEvent`, `encode_sse`) live in `hedron_core.live`.

## `SseResponse`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `content` | sync/async byte iterator | required | SSE body |
| `status_code` | `int` | `200` | HTTP status |
| `headers` | mapping | `None` | Merged with `Cache-Control: no-store`, `Connection: keep-alive`, `X-Accel-Buffering: no` |

`media_type` is always `text/event-stream`.

## `sse_response(events)`

Wraps an iterator/list of `SseEvent` values and returns `SseResponse`.

```python
from hedron import sse_response
from hedron_core.live import SseEvent

return sse_response([SseEvent(data="ping", event="message", id="1")])
```

## `job_status_sse_response(job_id, …)`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `job_id` | `str` | required | Opaque job id |
| `backend` | `JobBackend \| None` | process default | Job store |
| `request` | Starlette `Request \| None` | `None` | Reads `Last-Event-ID` when set |
| `html_message` | callable \| `None` | Status component | HTML payload for message events |
| `poll_interval_seconds` | `float \| None` | backend default | Server-side poll between emissions |

Streams until the job is terminal or missing. Emits only when `state` / `updated_at` change.

## Errors

- Missing/unknown jobs end the stream after a terminal/missing event sequence.
- Backend failures surface as ordinary Python exceptions from the generator (map to HTTP errors in your route if needed).

## See also

[Live interaction guide](../guides/live-interaction.md) · [Jobs](JOBS.md)
