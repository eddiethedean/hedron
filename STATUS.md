# Specification and implementation status

**Roadmap position:** phase 0.10 cut-ready on repository `main`.
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

## Phase 0.10 evidence

- Closure index: [release-gate-0.10.toml](docs/acceptance/release-gate-0.10.toml)
  (`Verified` or owned `Deferred`).
- Acceptance: [RELEASE_0_10.md](docs/acceptance/RELEASE_0_10.md) and
  [RFC-0032](docs/rfcs/RFC-0032-LIVE-TRANSPORT.md).
- Stability: [docs/api/STABILITY.md](docs/api/STABILITY.md).
- Compatibility / deprecation: [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).
- Upgrade: [docs/guides/upgrade.md](docs/guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_10.py`.
- Cut procedure: [docs/RELEASE.md](docs/RELEASE.md) (`## Build and cut v0.10.0`).
  Tag/publish remains an explicit release step after public-index verification.
