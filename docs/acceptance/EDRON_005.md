# Edron 0.5 acceptance

**Status:** Refined implementation candidate; no availability claim

Phase 0.5 is the proposed state, resource, durable-job, progressive-observation, and deployment
diagnostics slice. The packet freezes entry and exit gates; it does not authorize implementation or
publication until the native contracts and supported backend matrix are accepted.

| Gate | Evidence required | State |
|---|---|---|
| `EDR-05-RES` | deterministic sync/async resource lifetime, cleanup, cancellation, errors, and overrides | Planned |
| `EDR-05-STATE` | typed session/cache ownership, scope partition, expiry, invalidation, restart, and multi-worker behavior | Planned |
| `EDR-05-JOB` | bounded progress, cancel, retry/idempotency, result/download, retention, authorization, and operator diagnostics | Planned |
| `EDR-05-LIVE` | polling/no-JavaScript baseline plus optional SSE/WebSocket reconnect, stale, disconnect, CSP, and rate evidence | Planned |
| `EDR-05-OPS` | redacted deterministic deployment checks and fail-closed production durability findings | Planned |
| `EDR-05-ADAPTER` | lazy optional adapters, direct-install/version-pin diagnostics, and host matrix | Planned |
| `EDR-05-REGRESSION` | Edron 0.4 regression, upgrade fixtures, built artifacts, documentation, and package checks | Planned |

Native Hedron remains the authority for dependency injection, lifespan, sessions, caches, durable
jobs, live transports, production gates, authorization, persistence, queues, workers, and audit.
Edron must not add a global resource registry, worker/scheduler/queue/database/object-store
implementation, implicit rerun model, or client-side state authority.
