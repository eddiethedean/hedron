# Edron 0.5 acceptance

**Status:** Implemented and verified in-tree; publication pending

Phase 0.5 is the implemented state, resource, durable-job, progressive-observation, and deployment
diagnostics slice. The packet records the verified gates; publication remains a separate maintainer
step after artifact and registry checks.

Public API draft: [Edron 0.5 resource and operational API](../api/EDRON_05.md).

| Gate | Evidence required | State |
|---|---|---|
| `EDR-05-RES` | deterministic sync/async resource lifetime, cleanup, cancellation, errors, and overrides | Verified by `tests/unit/test_edron_phase05.py` |
| `EDR-05-STATE` | typed session/cache ownership, scope partition, expiry, invalidation, restart, and multi-worker behavior | Verified by native cache/session contracts and `tests/unit/test_edron_phase05.py` |
| `EDR-05-JOB` | bounded progress, cancel, retry/idempotency, result/download, retention, authorization, and operator diagnostics | Verified by `tests/unit/test_edron_phase05.py` and native JobBackend contracts |
| `EDR-05-LIVE` | polling/no-JavaScript baseline plus optional SSE/WebSocket reconnect, stale, disconnect, CSP, and rate evidence | Verified by `tests/unit/test_edron_phase05.py` and native live contracts |
| `EDR-05-OPS` | redacted deterministic deployment checks and fail-closed production durability findings | Verified by `tests/unit/test_edron_phase05.py` and native production gates |
| `EDR-05-ADAPTER` | lazy optional adapters, direct-install/version-pin diagnostics, and host matrix | Verified by docs, package, and adapter CI suites |
| `EDR-05-REGRESSION` | Edron 0.4 regression, upgrade fixtures, built artifacts, documentation, and package checks | Verified by focused Edron regression and CI |

Native Hedron remains the authority for dependency injection, lifespan, sessions, caches, durable
jobs, live transports, production gates, authorization, persistence, queues, workers, and audit.
Edron must not add a global resource registry, worker/scheduler/queue/database/object-store
implementation, implicit rerun model, or client-side state authority.
