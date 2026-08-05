# Specification and implementation status

**Roadmap position:** phase 0.13 **published** as `v0.13.0` (2026-08-05). Workspace
packages: Beta `0.13.0`, Alpha charts/sample-kit `0.1.x`.
**Date:** 2026-08-05
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` `0.13.0`; Alpha (independent) —
`hedron-charts` / `hedron-sample-kit` `0.1.x` (MIT licensed, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`; Alpha — `hedron-charts`, `hedron-sample-kit`.

**Phase focus:** advanced async and observability: optional component `prepare()`, adaptive
concurrency, optional distributed tracing, HDJ async I/O contracts (`HDJ-DEF-013`),
`SecurityAuditSink`, Redis-durable Celery/RQ status, live-transport claim honesty, and a
complete `HED-*` catalog (zero Deferred for 0.13-owned rows). Capture UI remains **0.15**.

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred**. Live
SSE/WS/streaming/preload remain **experimental** (polling Supported) until earlier ops gates
close. Phase 0.13 closed with **zero Deferred** rows for 0.13-owned work.

| ID | Topic | Disposition | Notes |
|---|---|---|---|
| — | Typed pages, HTMX fragments, CSRF profiles, CLI | Verified | FastAPI flagship |
| — | Flask/Django native depth | Verified (0.11) | D-046 |
| — | Data/chart scale | Verified (0.12) | D-047 |
| — | Component `prepare()` + async scenario harness | Verified (0.13) | `PREP-013` / `ASYNC-TEST-013` |
| — | Adaptive concurrency + scenario load | Verified (0.13) | `CONC-013` / `PERF-013-SCENARIO` |
| — | Optional distributed tracing | Verified (0.13) | `TRACE-013` |
| — | HDJ async I/O budgets | Verified (0.13) | `HDJ-DEF-013` |
| — | Security audit sink | Verified (0.13) | `AUDIT-013` |
| — | Celery/RQ Redis durable status | Verified (0.13) | `JOB-013-*` |
| — | Live-claim honesty + HED catalog | Verified (0.13) | `LIVE-CLAIM-013` / `HED-CAT-013` |
| `LIVE-011-BROWSER` | Full adapter live browser matrix | **Deferred** → `0.11.x` | Prior-phase carryover |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Deferred** → `0.10.x` | Prior-phase carryover |
| `PERF-10-001` | Load/proxy backpressure evidence | **Deferred** → `0.10.x` | SSE/WS ops proof |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | |

## Phase 0.13 evidence

- Closure index: [release-gate-0.13.toml](acceptance/release-gate-0.13.toml)
  (all `Verified`; zero-Deferred for 0.13-owned rows).
- Acceptance: [RELEASE_0_13.md](acceptance/RELEASE_0_13.md).
- Stability: [api/STABILITY.md](api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_13.py`.
- Cut procedure: [RELEASE.md](RELEASE.md) (next capability cut: **0.14**).

## Next capability phase

**0.14** — portable runtimes and acceleration. Track progress in [ROADMAP.md](ROADMAP.md) and
the public [roadmap guide](guides/roadmap.md).
