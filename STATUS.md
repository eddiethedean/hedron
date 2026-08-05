<!-- Generated from docs/STATUS.md — edit the docs/ copy, then run scripts/sync_status_roadmap.py -->

# Specification and implementation status

**Roadmap position:** phase 0.14 **implemented** as `v0.14.0` (2026-08-05). Workspace
packages: Beta `0.14.0`, Alpha charts/sample-kit/native `0.1.x`.
**Date:** 2026-08-05
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` / `hedron-conformance` `0.14.0`; Alpha
(independent) — `hedron-charts` / `hedron-sample-kit` / `hedron-native` `0.1.x` (MIT, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`, `hedron-conformance`; Alpha —
`hedron-charts`, `hedron-sample-kit`, `hedron-native`.

**Phase focus:** portable runtimes and acceleration: language-neutral conformance kit,
experimental Java/Node runtimes, optional Rust HTML-escaping acceleration with pure-Python
fallback (D-048), and HDJ instrumentation (`HDJ-DEF-014`). Capture UI remains **0.15**.

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](docs/guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred**. Live
SSE/WS/streaming/preload remain **experimental** (polling Supported) until earlier ops gates
close. Phase 0.14 closed with **zero Deferred** rows for 0.14-owned work.

| ID | Topic | Disposition | Notes |
|---|---|---|---|
| — | Typed pages, HTMX fragments, CSRF profiles, CLI | Verified | FastAPI flagship |
| — | Flask/Django native depth | Verified (0.11) | D-046 |
| — | Data/chart scale | Verified (0.12) | D-047 |
| — | Advanced async / observability | Verified (0.13) | |
| `CONFORM-014` | Language-neutral conformance kit | Verified (0.14) | `hedron-conformance` |
| `SPEC-014` | Portable fixture schema | Verified (0.14) | |
| `RUNTIME-NODE-014` / `RUNTIME-JAVA-014` | Experimental runtimes | Verified (0.14) | Alpha |
| `ACCEL-RUST-014` / `PARITY-014` | Optional Rust accel + fallback | Verified (0.14) | `hedron-native` |
| `HDJ-DEF-014` | HDJ loop/macro / extension / a11y fixtures | Verified (0.14) | |
| `LIVE-011-BROWSER` | Full adapter live browser matrix | **Deferred** → `0.11.x` | Prior-phase carryover |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Deferred** → `0.10.x` | Prior-phase carryover |
| `PERF-10-001` | Load/proxy backpressure evidence | **Deferred** → `0.10.x` | SSE/WS ops proof |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | |

## Phase 0.14 evidence

- Closure index: [release-gate-0.14.toml](docs/acceptance/release-gate-0.14.toml)
  (all `Verified`; zero-Deferred for 0.14-owned rows).
- Acceptance: [RELEASE_0_14.md](docs/acceptance/RELEASE_0_14.md).
- Stability: [api/STABILITY.md](docs/api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](docs/COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](docs/guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_14.py`.
- Cut procedure: [RELEASE.md](docs/RELEASE.md) (next capability cut: **0.15**).

## Next capability phase

**0.15** — data-app surface completeness. Track progress in [ROADMAP.md](docs/ROADMAP.md) and
the public [roadmap guide](docs/guides/roadmap.md).
