# Specification and implementation status

**Roadmap position:** phase 0.10 **published** as `v0.10.0` (packages `0.10.0`, 2026-08-04).
**Date:** 2026-08-04
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` / `hedron-sample-kit` /
`hedron-data` / `hedron-charts` / `hedron-flask` / `hedron-django` / `hedron-jinja` `0.10.0`
(MIT licensed, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`; Alpha — `hedron-charts`, `hedron-sample-kit`.

**Phase focus:** live interaction and navigation (RFC-0032 / D-044 / D-045): official HTMX SSE,
focused streaming, page/session WebSocket channels, Chat/Dialog, media chunk transport contracts,
HDJ head/two-phase streaming, and opt-in navigation preload. Polling and ordinary HTTP remain
Supported fallbacks. Native Flask/Django depth remains assigned to 0.11; capture UI to 0.15.

**Honest Deferred (owned, post-release):** full three-engine live browser matrix beyond asset/HTMX
smoke, load/proxy backpressure evidence, Explorer live traces, and a first-party live example app
(`BROWSER-10-001`, `PERF-10-001`, `EXPLORER-10-001`, `EXAMPLES-10-001` → `0.10.x`).

## Phase 0.10 evidence

- Closure index: [release-gate-0.10.toml](acceptance/release-gate-0.10.toml)
  (`Verified` or owned `Deferred`).
- Acceptance: [RELEASE_0_10.md](acceptance/RELEASE_0_10.md) and
  [RFC-0032](rfcs/RFC-0032-LIVE-TRANSPORT.md).
- Stability: [api/STABILITY.md](api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_10.py`.
- Cut procedure: [RELEASE.md](RELEASE.md) (`## Build and cut v0.10.0`).
  Next capability phase packet: **0.11**.
