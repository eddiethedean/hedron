<!-- Generated from docs/STATUS.md — edit the docs/ copy, then run scripts/sync_status_roadmap.py -->

# Specification and implementation status

**Roadmap position:** phase 0.11 **published**; current train `v0.11.0` (Beta packages
`0.11.0`, Alpha charts/sample-kit `0.1.x`, 2026-08-04).
**Date:** 2026-08-04
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` `0.11.0`; Alpha (independent) —
`hedron-charts` / `hedron-sample-kit` `0.1.x` (MIT licensed, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`; Alpha — `hedron-charts`, `hedron-sample-kit`.

**Phase focus:** native Flask/Django depth (D-046 / D-044): Blueprint/`init_app`, Django
`AppConfig`, forms bridge, bounded QuerySet DataSource, portable adapter test harness, HDJ
dynamic manifests / foreign namespaces / SecurityPolicy–CSP reconciliation, Celery/RQ
`JobBackend` bridges, and capability-labeled Flask/Django live helpers (polling Supported
fallback). Capture UI remains **0.15**.

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](docs/guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred**. Live
SSE/WS/streaming/preload are **experimental** (polling Supported) until ops gates close.

| ID | Topic | Disposition | Notes |
|---|---|---|---|
| — | Typed pages, HTMX fragments, CSRF profiles, CLI | Verified | FastAPI flagship |
| — | Flask Blueprint / `init_app` | Verified (0.11) | `ADP-FLK-011` |
| — | Django AppConfig / forms / QuerySet DataSource | Verified (0.11) | D-046 |
| — | Portable adapter test harness | Verified (0.11) | `TEST-011` |
| — | HDJ manifests / CSP inventory | Verified (0.11) | `HDJ-DEF-011` |
| — | Celery/RQ JobBackend bridges | Verified (0.11) | optional extras |
| — | Flask/Django live helpers | Experimental API | Polling Supported fallback |
| `LIVE-011-BROWSER` | Full adapter live browser matrix | **Deferred** → `0.11.x` | |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Deferred** → `0.10.x` | Beyond asset/HTMX smoke |
| `PERF-10-001` | Load/proxy backpressure evidence | **Deferred** → `0.10.x` | SSE/WS ops proof |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | |

## Phase 0.11 evidence

- Closure index: [release-gate-0.11.toml](docs/acceptance/release-gate-0.11.toml)
  (`Verified` or owned `Deferred`).
- Acceptance: [RELEASE_0_11.md](docs/acceptance/RELEASE_0_11.md).
- Stability: [api/STABILITY.md](docs/api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](docs/COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](docs/guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_11.py`.
- Cut procedure: [RELEASE.md](docs/RELEASE.md) (next cut: **0.12**).

## Next capability phase

**0.12** — data and visualization scale (advanced editor, distributed sources, more chart
adapters). Track progress in [ROADMAP.md](docs/ROADMAP.md) and the public
[roadmap guide](docs/guides/roadmap.md).
