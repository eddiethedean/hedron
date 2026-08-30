# Observability

Operator-facing guidance for logging, health, and diagnosing Hedron apps in production.
Hedron uses the standard library logging module and bounded diagnostic records — it does
not require a telemetry SDK.

## Logging

- Logger names are typically `hedron` and subsystem loggers under packages.
- Prefer structured messages that include route name, component logical id, and a
  request correlation id you inject in FastAPI middleware (for example
  `X-Request-ID` → `logging.LoggerAdapter` / contextvars).
- Suggested fields for app logs: `request_id`, `route`, `logical_id`, `render_mode`
  (`PAGE`/`FRAGMENT`), `status_code`, `duration_ms`.
- Never log session secrets, CSRF tokens, or raw credentials. Diagnostics redact secrets
  before formatting.

### Request IDs, timing, and tracing

Use ordinary FastAPI middleware for application-owned request logs. Optional Hedron spans can
share the same service name without changing behavior when an exporter is unavailable:

```python
import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request

from hedron import Hedron
from hedron.tracing import configure_tracing

logger = logging.getLogger("app.http")
configure_tracing(enabled=True, sample_rate=0.1, service_name="operations-ui")

app = Hedron(title="Operations", security="standard")


@app.middleware("http")
async def log_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid4().hex
    started = perf_counter()
    response = await call_next(request)
    duration_ms = (perf_counter() - started) * 1_000

    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request.complete",
        extra={
            "request_id": request_id,
            "route": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )
    return response


@app.get("/healthz", include_in_schema=False)
def healthz() -> dict[str, str]:
    return {"status": "ok"}
```

If `hedron[otel]` is not installed, tracing is a no-op; the middleware and health endpoint
continue to work through FastAPI and standard-library logging.

## Health and readiness

Expose ordinary FastAPI (or host) health endpoints yourself. Suggested split:

| Endpoint | Meaning |
|---|---|
| `/healthz` | Process is up (liveness) |
| `/readyz` | Build manifest present (production), dependent stores reachable if you require them |

Hedron refuses to start in production without a valid build manifest (`HED-BUILD-0003`).
That gate is stronger than a custom readiness probe for CSS/asset correctness.

Map `HED-*` failures into alerts by code family (`HED-SEC-*`, `HED-BUILD-*`) rather than
substring-matching HTML bodies.

## Optional OpenTelemetry

Install `hedron[otel]` and call `hedron.tracing.configure_tracing(enabled=True)` to emit
optional first-party spans across HTTP, prepare, cache, jobs, and render. Sampling and
exporter failure never change component semantics; disable anytime to return to stdlib-only
logging. If your platform already instruments FastAPI / Starlette, propagate the same
`traceparent` / request id into application logs. App-owned metrics remain application
middleware (`hedron_fragment_latency_ms`, `hedron_sse_open_connections`, …).

## Jobs, SSE, and proxies

- Job status SSE must be authorized the same way as polling status endpoints
  ([threat model](threat-model.md)).
- Disable response buffering for `text/event-stream` at the reverse proxy
  ([deployment](deployment.md)).
- Multi-worker deployments: do not assume in-process job/session memory is shared.

## Diagnostics

Stable `HED-*` codes from `hedron check`, CLI, and runtime failures — see
[Error codes](error-codes.md) and [API diagnostics](../api/DIAGNOSTICS.md).

## See also

[Deployment](deployment.md) · [Ship a Hedron app](ship.md) ·
[Support](support.md)
