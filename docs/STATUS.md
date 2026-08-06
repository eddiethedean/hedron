# Specification and implementation status

**Roadmap position:** phase 0.17 **Published** as `v0.17.0` (2026-08-06). Workspace packages:
Beta `0.17.0`, Alpha charts/sample-kit/native `0.1.x`, Alpha notebook/mcp `0.1.0`.
**Date:** 2026-08-06
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` / `hedron-conformance` / `hedron-extras`
`0.17.0`; Alpha (independent) — `hedron-charts` / `hedron-sample-kit` / `hedron-native` /
`hedron-notebook` / `hedron-mcp` `0.1.x` (MIT, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`, `hedron-conformance`, `hedron-extras`; Alpha —
`hedron-charts`, `hedron-sample-kit`, `hedron-native`, `hedron-notebook`, `hedron-mcp`.

**Phase focus:** reactive dashboards and agent interfaces — `DashboardBinding` /
`InteractionGraph`, bounded patches, cross-filter/replay, HTMX shell primitives, optional
`hedron-notebook` / `hedron-mcp` (Experimental), Dash/NiceGUI migration inventories.

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred**. Live
SSE/WS/streaming/preload remain **experimental** (polling Supported). Notebook preview and MCP
are **Experimental** / Alpha. Phase 0.17 closed with **zero Deferred** among **0.17 gate IDs**
(`check_release_gate.py 0.17.0`); prior-phase Deferred rows below remain owned elsewhere.

| ID | Topic | Disposition | Notes |
|---|---|---|---|
| — | Typed pages, HTMX fragments, CSRF profiles, CLI | Verified | FastAPI flagship |
| — | Flask/Django native depth | Verified (0.11) | D-046 |
| — | Data/chart scale | Verified (0.12) | D-047 |
| — | Advanced async / observability | Verified (0.13) | |
| — | Portable runtimes / acceleration | Verified (0.14) | |
| — | Data-app surface completeness | Verified (0.15) | |
| — | Curated extras / workbenches | Verified (0.16) | |
| `GRAPH-017` | InteractionGraph / TriggerContext | Verified (0.17) | RFC-0040 |
| `PATCH-017` | PropertyPatch / CollectionPatch | Verified (0.17) | RFC-0041 |
| `XFILTER-017` | Cross-filter composition | Verified (0.17) | |
| `REPLAY-017` | Graph recorder / replay | Verified (0.17) | |
| `NOTEBOOK-017` | hedron-notebook preview | Verified (0.17) | Experimental |
| `MCP-017` | hedron-mcp projection | Verified (0.17) | Experimental; deny-by-default |
| `SHELL-017` | NavLink / AppShell / render_interaction | Verified (0.17) | RFC-0044 |
| `HEDDOC-017` | error-codes.md ↔ HED-* catalog | Verified (0.17) | #15 |
| `ASSERT-017` | Dialog/Tabs/Pagination/Lazy asserts | Verified (0.17) | #24 |
| `MIGRATE-017` | Dash / NiceGUI migration inventory | Verified (0.17) | |
| `LIVE-011-BROWSER` | Full adapter live browser matrix | **Deferred** → `0.11.x` | Prior-phase carryover |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Deferred** → `0.10.x` | Prior-phase carryover |
| `PERF-10-001` | Load/proxy backpressure evidence | **Deferred** → `0.10.x` | SSE/WS ops proof |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | |

## Phase 0.17 evidence

- Closure index: [release-gate-0.17.toml](acceptance/release-gate-0.17.toml)
  (all `Verified`; zero-Deferred for 0.17-owned rows).
- Acceptance: [RELEASE_0_17.md](acceptance/RELEASE_0_17.md).
- Stability: [api/STABILITY.md](api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_17.py`.
- Cut procedure: [RELEASE.md](RELEASE.md) (last published: **0.17**; next capability: **0.18**).

## Next capability phase

**0.18** — model demos and inference workflows. Track progress in [ROADMAP.md](ROADMAP.md)
and the public [roadmap guide](guides/roadmap.md).
Open-issue owners: [issue ownership table](ROADMAP.md#open-github-issue-ownership-013).
