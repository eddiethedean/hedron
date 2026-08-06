# Specification and implementation status

**Roadmap position:** phase 0.16 **Published** as `v0.16.0` (2026-08-06). Workspace packages:
Beta `0.16.0`, Alpha charts/sample-kit/native `0.1.x`.
**Date:** 2026-08-06
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` / `hedron-conformance` / `hedron-extras`
`0.16.0`; Alpha (independent) — `hedron-charts` / `hedron-sample-kit` / `hedron-native` `0.1.x`
(MIT, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`, `hedron-conformance`, `hedron-extras`; Alpha —
`hedron-charts`, `hedron-sample-kit`, `hedron-native`.

**Phase focus (published):** curated extras and interactive analysis tools — optional
`hedron-extras`, composition UI, DataExplorer/JSONEditor/CodeEditor workbenches, image tools,
calendar/signature/typeahead, display recipes, browser-Python sandbox, and Experimental specialty
extras (TerminalView, joystick/device bridges, native-shell packaging recipe).

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred**. Live
SSE/WS/streaming/preload remain **experimental** (polling Supported) until earlier ops gates
close. Specialty extras (TerminalView / joystick / device bridges) are **Experimental**.
Phase 0.16 closed with **zero Deferred** among **0.16 gate IDs**
(`check_release_gate.py 0.16.0`); prior-phase Deferred rows below remain owned elsewhere.

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

- Closure index: [release-gate-0.16.toml](acceptance/release-gate-0.16.toml)
  (all `Verified`; zero-Deferred for 0.16-owned rows).
- Acceptance: [RELEASE_0_16.md](acceptance/RELEASE_0_16.md).
- Stability: [api/STABILITY.md](api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_16.py`.
- Cut procedure: [RELEASE.md](RELEASE.md) (last published: **0.16**; next capability: **0.17**).

## Next capability phase

**0.17** — reactive dashboards and agent interfaces (**Planned**; phase packet refined
2026-08-06). Entry cross-checks refreshed; RFCs 0040–0044 Accepted; evidence scaffold
[release-gate-0.17.toml](acceptance/release-gate-0.17.toml) /
[RELEASE_0_17.md](acceptance/RELEASE_0_17.md).

Workstreams / gate IDs (all **Planned** until implementation):

| ID | Topic | Owner |
|---|---|---|
| `GRAPH-017` | InteractionGraph / TriggerContext | RFC-0040 / [#41](https://github.com/eddiethedean/hedron/issues/41) |
| `PATCH-017` | PropertyPatch / CollectionPatch | RFC-0041 / [#42](https://github.com/eddiethedean/hedron/issues/42) |
| `XFILTER-017` | Cross-filter composition | RFC-0040/0041 |
| `REPLAY-017` | Graph recorder / replay | RFC-0040 |
| `NOTEBOOK-017` | `hedron-notebook` (experimental) | RFC-0042 / [#43](https://github.com/eddiethedean/hedron/issues/43) |
| `MCP-017` | `hedron-mcp` (experimental) | RFC-0043 / [#44](https://github.com/eddiethedean/hedron/issues/44) |
| `SHELL-017` | NavLink / OobHost / AppShell / render_interaction | RFC-0044 / `#28`–`#30`, `#35`, `#40` |
| `HEDDOC-017` | `error-codes.md` ↔ `HED-*` catalog | `#15` |
| `ASSERT-017` | Dialog / Tabs / Pagination / Lazy asserts | `#24` |
| `MIGRATE-017` | Dash / NiceGUI migration inventory | [#45](https://github.com/eddiethedean/hedron/issues/45) |
| `REGRESS-017` / `PKG-017` | Full regression / package verify | cut |

Also: shell NavLink/OobHost/`class_` primitives; landmark a11y attrs/types land in **0.19**.
Track progress in [ROADMAP.md](ROADMAP.md) and the public [roadmap guide](guides/roadmap.md).
Open-issue owners: [issue ownership table](ROADMAP.md#open-github-issue-ownership-013).
Next step: implement against Verified promotion (`check_release_gate.py 0.17.0 --allow-planned`
during development).
