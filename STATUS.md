<!-- Generated from docs/STATUS.md — edit the docs/ copy, then run scripts/sync_status_roadmap.py -->

# Specification and implementation status

**Roadmap position:** phase 0.16 **implemented** as `v0.16.0` (2026-08-06; **pending cut** —
draft until the coordinated tag/publish). Workspace packages: Beta `0.16.0`, Alpha
charts/sample-kit/native `0.1.x`.
**Date:** 2026-08-06
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` / `hedron-conformance` / `hedron-extras`
`0.16.0`; Alpha (independent) — `hedron-charts` / `hedron-sample-kit` / `hedron-native` `0.1.x`
(MIT, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`, `hedron-conformance`, `hedron-extras`; Alpha —
`hedron-charts`, `hedron-sample-kit`, `hedron-native`.

**Phase focus:** curated extras and interactive analysis tools — optional `hedron-extras`,
composition UI, DataExplorer/JSONEditor/CodeEditor workbenches, image tools, calendar/signature/
typeahead, display recipes, browser-Python sandbox, and Experimental specialty extras
(TerminalView, joystick/device bridges, native-shell packaging recipe).

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](docs/guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred**. Live
SSE/WS/streaming/preload remain **experimental** (polling Supported) until earlier ops gates
close. Specialty extras (TerminalView / joystick / device bridges) are **Experimental**.
Phase 0.16 closed with **zero Deferred** rows for 0.16-owned work (pending cut
verification via `check_release_gate.py 0.16.0`).

| ID | Topic | Disposition | Notes |
|---|---|---|---|
| — | Typed pages, HTMX fragments, CSRF profiles, CLI | Verified | FastAPI flagship |
| — | Flask/Django native depth | Verified (0.11) | D-046 |
| — | Data/chart scale | Verified (0.12) | D-047 |
| — | Advanced async / observability | Verified (0.13) | |
| — | Portable runtimes / acceleration | Verified (0.14) | |
| — | Data-app surface completeness | Verified (0.15) | |
| `EXTRAS-PKG-016` | hedron-extras + FeatureManifest | Verified (0.16) | |
| `WORKBENCH-TEST-016` | Workbench-flow AppScenario helpers | Verified (0.16) | |
| `COMPOSITION-016` | ChoiceCards / TreeView / Steps / Split / FAB | Verified (0.16) | |
| `WORKBENCH-016` | DataExplorer / editors / ChartWorkbench | Verified (0.16) | RFC-0037 |
| `IMAGE-016` | Compare / crop / region / annotations | Verified (0.16) | |
| `EDITOR-EXTRAS-016` | Calendar / signature / typeahead | Verified (0.16) | RFC-0037 |
| `DISPLAY-016` | Log console + presentation recipes | Verified (0.16) | |
| `SANDBOX-016` | Browser-Python sandbox | Verified (0.16) | |
| `SPECIALTY-016` | TerminalView / joystick / device (Experimental) | Verified (0.16) | RFC-0038 |
| `LIVE-011-BROWSER` | Full adapter live browser matrix | **Deferred** → `0.11.x` | Prior-phase carryover |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Deferred** → `0.10.x` | Prior-phase carryover |
| `PERF-10-001` | Load/proxy backpressure evidence | **Deferred** → `0.10.x` | SSE/WS ops proof |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | |

## Phase 0.16 evidence

- Closure index: [release-gate-0.16.toml](docs/acceptance/release-gate-0.16.toml)
  (all `Verified`; zero-Deferred for 0.16-owned rows).
- Acceptance: [RELEASE_0_16.md](docs/acceptance/RELEASE_0_16.md).
- Stability: [api/STABILITY.md](docs/api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](docs/COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](docs/guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_16.py`.
- Cut procedure: [RELEASE.md](docs/RELEASE.md) (current cut target: **0.16**; next capability: **0.17**).

## Next capability phase

**0.17** — reactive dashboards and agent interfaces. Track progress in [ROADMAP.md](docs/ROADMAP.md) and
the public [roadmap guide](docs/guides/roadmap.md).
