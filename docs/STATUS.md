# Specification and implementation status

**Roadmap position:** phase 0.12 **implementation complete / ready to cut** (not published
until `v0.12.0` tag). Workspace packages: Beta `0.12.0`, Alpha charts/sample-kit `0.1.x`
(2026-08-05). Last published train remains `v0.11.0` until cut.
**Date:** 2026-08-05
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` `0.12.0`; Alpha (independent) —
`hedron-charts` / `hedron-sample-kit` `0.1.x` (MIT licensed, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`; Alpha — `hedron-charts`, `hedron-sample-kit`.

**Phase focus:** data and visualization scale (D-047): shared column catalog, typed
grid/chart events, saved views, `TransformPlan`, advanced DataEditor (formulas, pivots,
trees, collab, spreadsheet I/O), AG Grid Community client/infinite, Dask/Snowflake sources,
beginner Area/Bar/Scatter charts, Plotly typed events, annotation overlays, optional chart
adapters, offline runtime pins, HDJ `hedron.data`/`hedron.charts` provider parity, and
three-engine browser/a11y matrices (zero Deferred). Capture UI remains **0.15**.

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred**. Live
SSE/WS/streaming/preload remain **experimental** (polling Supported) until earlier ops gates
close. Phase 0.12 closed with **zero Deferred** rows.

| ID | Topic | Disposition | Notes |
|---|---|---|---|
| — | Typed pages, HTMX fragments, CSRF profiles, CLI | Verified | FastAPI flagship |
| — | Flask/Django native depth | Verified (0.11) | D-046 |
| — | Data/chart contract fixtures | Verified (0.12) | `TEST-012` |
| — | Column catalog / events / views / plans | Verified (0.12) | `COL-012` / `EVT-012` / `VIEW-012` / `PLAN-012` |
| — | Distributed/lazy sources | Verified (0.12) | `SRC-012*` |
| — | Advanced DataEditor / AG Grid infinite | Verified (0.12) | `EDIT-012*` / `GRID-012-AG` |
| — | Visualization scale + offline pins | Verified (0.12) | `CHART-012-*` |
| — | HDJ data/charts provider parity | Verified (0.12) | `HDJ-DEF-012` |
| — | Grid/chart spatial a11y + browser matrix | Verified (0.12) | `A11Y-012` / `BROWSER-012` |
| `LIVE-011-BROWSER` | Full adapter live browser matrix | **Deferred** → `0.11.x` | Prior-phase carryover |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Deferred** → `0.10.x` | Prior-phase carryover |
| `PERF-10-001` | Load/proxy backpressure evidence | **Deferred** → `0.10.x` | SSE/WS ops proof |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | |

## Phase 0.12 evidence

- Closure index: [release-gate-0.12.toml](acceptance/release-gate-0.12.toml)
  (all `Verified`; D-047 zero-Deferred policy).
- Acceptance: [RELEASE_0_12.md](acceptance/RELEASE_0_12.md).
- Stability: [api/STABILITY.md](api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_12.py`.
- Cut procedure: [RELEASE.md](RELEASE.md) (next cut: **0.13**).

## Next capability phase

**0.13** — advanced async and observability. Track progress in [ROADMAP.md](ROADMAP.md) and
the public [roadmap guide](guides/roadmap.md).
