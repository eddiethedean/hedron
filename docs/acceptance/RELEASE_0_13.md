# Hedron `v0.13` advanced async and observability acceptance

Phase 0.13 delivers optional component `prepare()`, adaptive concurrency, optional
distributed tracing, HDJ async I/O budgets, `SecurityAuditSink`, Redis-durable Celery/RQ
job status, live-transport claim honesty, and a complete `HED-*` catalog. Evidence is
indexed by [`release-gate-0.13.toml`](release-gate-0.13.toml).
**Zero Deferred:** every 0.13-owned gate row must be Verified at cut. Prior-phase live ops
Deferred rows (`BROWSER-10-001`, `PERF-10-001`, `LIVE-011-BROWSER`, `EXPLORER-10-001`)
remain owned by `0.10.x` / `0.11.x` and stay experimental.

## Spec packet

- [x] ROADMAP §0.13 scope accepted; sync rendering remains the deterministic final stage.
- [x] Entry gate: 0.12 evidence remains closed; 0.13 gate TOML owns Verified rows only.

## Prepare and async test controls

- [x] Optional component `prepare()` with ownership, deadlines, cancellation, partial
  failure, caching, and deterministic render handoff. *(`PREP-013`)*
- [x] Controllable clock and scripted cancel/disconnect scenario harness.
  *(`ASYNC-TEST-013`)*

## Concurrency and tracing

- [x] Adaptive concurrency from measured capacity with semantic-preserving opt-out.
  *(`CONC-013`)*
- [x] Optional distributed tracing with redaction, sampling, stable spans, exporter
  failure isolation, and opt-out. *(`TRACE-013`)*
- [x] Scenario overload/degradation/shutdown/partial-failure evidence without wall-clock
  sleeps. *(`PERF-013-SCENARIO`)*

## HDJ / audit / jobs / honesty

- [x] HDJ async filter/global I/O budgets, deadlines, cancellation, and trace correlation.
  *(`HDJ-DEF-013`)*
- [x] `SecurityAuditSink` for framework-boundary events without secrets. *(`AUDIT-013`)*
- [x] Celery/RQ Redis-backed durable status and idempotency. *(`JOB-013-CELERY`)*
  *(`JOB-013-RQ`)*
- [x] Live-transport Supported vs experimental labeling reconciled. *(`LIVE-CLAIM-013`)*
- [x] Complete `HED-*` catalog with CI fail-on-unregistered. *(`HED-CAT-013`)*

## Exit

- [x] Full regression suite. *(`REGRESS-013`)*
- [x] Packaging rehearsal. *(`PKG-013`)*
