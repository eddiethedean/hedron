<!-- Generated from docs/STATUS.md — edit the docs/ copy, then run scripts/sync_status_roadmap.py -->

# Specification and implementation status

**Roadmap position:** phase 0.15 **implemented** as `v0.15.0` (2026-08-05; **pending cut** —
draft until the coordinated tag/publish). Workspace packages: Beta `0.15.0`, Alpha
charts/sample-kit/native `0.1.x`.
**Date:** 2026-08-05
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` / `hedron-conformance` `0.15.0`; Alpha
(independent) — `hedron-charts` / `hedron-sample-kit` / `hedron-native` `0.1.x` (MIT, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`, `hedron-conformance`; Alpha —
`hedron-charts`, `hedron-sample-kit`, `hedron-native`.

**Phase focus:** data-app surface completeness — AppScenario / HTMX testing helpers,
`region`/`@fragment`/`swap` ergonomics, typed controls and surface chrome, media
Range/downloads, Map/GeoJSON, BrowserContext/Storage, Math/IFrame, OIDC/session helpers,
and the named connection registry. Capture UI ships in this phase.

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](docs/guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred**. Live
SSE/WS/streaming/preload remain **experimental** (polling Supported) until earlier ops gates
close. Phase 0.15 closed with **zero Deferred** rows for 0.15-owned work (pending cut
verification via `check_release_gate.py 0.15.0`).

| ID | Topic | Disposition | Notes |
|---|---|---|---|
| — | Typed pages, HTMX fragments, CSRF profiles, CLI | Verified | FastAPI flagship |
| — | Flask/Django native depth | Verified (0.11) | D-046 |
| — | Data/chart scale | Verified (0.12) | D-047 |
| — | Advanced async / observability | Verified (0.13) | |
| — | Portable runtimes / acceleration | Verified (0.14) | |
| `TEST-APP-015` | AppScenario application-flow harness | Verified (0.15) | |
| `HTMX-ASSERT-015` | HTMX InteractionResult / fragment asserts | Verified (0.15) | #22–#26 |
| `ERGONOMICS-015` | region / @fragment / swap | Verified (0.15) | RFC-0039 |
| `CONTROLS-015` | Typed controls + surface chrome | Verified (0.15) | RFC-0035 |
| `MEDIA-015` | Media Range / downloads | Verified (0.15) | RFC-0034 |
| `MAP-015` | Map / GeoJSON | Verified (0.15) | RFC-0033 |
| `BROWSER-015` | BrowserContext / Storage, Math, IFrame | Verified (0.15) | |
| `IDENTITY-015` | OIDC / session helpers | Verified (0.15) | |
| `CONNECTIONS-015` | Connection registry | Verified (0.15) | |
| `LIVE-011-BROWSER` | Full adapter live browser matrix | **Deferred** → `0.11.x` | Prior-phase carryover |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Deferred** → `0.10.x` | Prior-phase carryover |
| `PERF-10-001` | Load/proxy backpressure evidence | **Deferred** → `0.10.x` | SSE/WS ops proof |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | |

## Phase 0.15 evidence

- Closure index: [release-gate-0.15.toml](docs/acceptance/release-gate-0.15.toml)
  (all `Verified`; zero-Deferred for 0.15-owned rows).
- Acceptance: [RELEASE_0_15.md](docs/acceptance/RELEASE_0_15.md).
- Stability: [api/STABILITY.md](docs/api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](docs/COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](docs/guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_15.py`.
- Cut procedure: [RELEASE.md](docs/RELEASE.md) (current cut target: **0.15**; next capability: **0.16**).

## Next capability phase

**0.16** — workbench / extras surface. Track progress in [ROADMAP.md](docs/ROADMAP.md) and
the public [roadmap guide](docs/guides/roadmap.md).
