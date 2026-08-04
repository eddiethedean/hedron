# Observability

Operator-facing guidance for logging, health, and diagnosing Hedron apps in production.
Hedron uses the standard library logging module and bounded diagnostic records — it does
not require a telemetry SDK.

## Logging

- Logger names are typically `hedron` and subsystem loggers under packages.
- Prefer structured messages that include route name, component logical id, and request
  correlation ids you already use in FastAPI middleware.
- Never log session secrets, CSRF tokens, or raw credentials. Diagnostics redact secrets
  before formatting.

## Health and readiness

Expose ordinary FastAPI (or host) health endpoints yourself. Suggested split:

| Endpoint | Meaning |
|---|---|
| `/healthz` | Process is up (liveness) |
| `/readyz` | Build manifest present (production), dependent stores reachable if you require them |

Hedron refuses to start in production without a valid build manifest (`HED-BUILD-0003`).
That gate is stronger than a custom readiness probe for CSS/asset correctness.

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

[Deployment](deployment.md) · [Production readiness](production-readiness.md) ·
[Support](support.md)
