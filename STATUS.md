# Specification and implementation status

**Roadmap position:** phase 0.7 **cut-ready** as `0.7.0` (tag `v0.7.0` when cut)
**Date:** 2026-08-03
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` / `hedron-sample-kit` /
`hedron-data` / `hedron-charts` / `hedron-flask` / `hedron-django` `0.7.0` (MIT licensed, D-033)

Phase 0.7 delivers the portable adapter foundation in `hedron-core`, Supported FastAPI
operations (gather/run_sync, Redis cache/jobs conformance, health/readiness, deploy topology),
Supported `hedron-flask` and `hedron-django` native adapters, durable `JobBackend` with 202
polling, and an HTMX extension asset contract. SSE live transport and Django QuerySet DataSource
remain Deferred (D-036, D-037).

## Phase 0.7 evidence

- Acceptance: [ADAPTERS](acceptance/ADAPTERS.md), [OPERATIONS](acceptance/OPERATIONS.md),
  [JOBS](acceptance/JOBS.md), [OBSERVABILITY](acceptance/OBSERVABILITY.md),
  [ASYNC](acceptance/ASYNC.md), [PACKAGING_DEPLOYMENT](acceptance/PACKAGING_DEPLOYMENT.md).
- Closure index: [release-gate-0.7.toml](acceptance/release-gate-0.7.toml)
  (`Verified` or owned `Deferred`).
- Compatibility: [COMPATIBILITY.md](COMPATIBILITY.md) Phase 0.7 entry gate (concrete ranges).
- Reference: FastAPI `examples/reference-app` compose topology; `examples/flask-reference`;
  `examples/django-reference`.
- Cut procedure: [RELEASE.md](RELEASE.md) (`## Cut v0.7.0`).

See the [roadmap](ROADMAP.md) for phase 0.8 API freeze entry.
