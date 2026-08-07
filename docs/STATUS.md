# Specification and implementation status

**Roadmap position:** phase 0.19 **Ready to cut / Implemented on `main`** as `0.19.0`
(2026-08-07); last published PyPI/git = `v0.18.0`. Workspace packages:
Beta `0.19.0`, Alpha charts/sample-kit/native `0.1.x`, Alpha notebook/mcp/gradio `0.1.0`.
**Date:** 2026-08-07
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` / `hedron-conformance` / `hedron-extras`
`0.19.0` on `main`; Alpha (independent) — `hedron-charts` / `hedron-sample-kit` /
`hedron-native` / `hedron-notebook` / `hedron-mcp` / `hedron-gradio` `0.1.x` (MIT, D-033).
PyPI/git still serve **`v0.18.0`** until `v0.19.0` is tagged and published.
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`, `hedron-conformance`, `hedron-extras`; Alpha —
`hedron-charts`, `hedron-sample-kit`, `hedron-native`, `hedron-notebook`, `hedron-mcp`,
`hedron-gradio`.

**Phase focus:** accessibility engineering and inclusive authoring — `AccessibilityContract`,
Explorer a11y workspace, ATAG assistance, progressive enhancement / landmarks / Page scripts,
automated AT matrix (human AT Deferred → 0.21 per D-050).

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred**. Live
SSE/WS/streaming/preload remain **experimental** (polling Supported). Notebook preview, MCP, and
Gradio interop are **Experimental** / Alpha. Phase 0.19 closed with **zero Deferred** among
**0.19 gate IDs** (`check_release_gate.py 0.19.0`); human screen-reader / compensated user
evaluation is owned by **0.21** (D-050), not a 0.19-owned Deferred row. Prior-phase Deferred rows
below remain owned elsewhere.

| ID | Topic | Disposition | Notes |
|---|---|---|---|
| — | Typed pages, HTMX fragments, CSRF profiles, CLI | Verified | FastAPI flagship |
| — | Flask/Django native depth | Verified (0.11) | D-046 |
| — | Data/chart scale | Verified (0.12) | D-047 |
| — | Advanced async / observability | Verified (0.13) | |
| — | Portable runtimes / acceleration | Verified (0.14) | |
| — | Data-app surface completeness | Verified (0.15) | |
| — | Curated extras / workbenches | Verified (0.16) | |
| — | Reactive dashboards / agent interfaces | Verified (0.17) | |
| — | Model demos / inference workflows | Verified (0.18) | D-049 |
| `PROFILE-019` | Standards profile / claim boundaries | Verified (0.19) | RFC-0023 |
| `CONTRACT-019` | AccessibilityContract catalog | Verified (0.19) | RFC-0051 |
| `INTERACT-019` | WCAG 2.2 interaction cases | Verified (0.19) | |
| `ATAG-019` | ATAG authoring assistance | Verified (0.19) | RFC-0054 |
| `EXPLORER-019` | Explorer a11y workspace | Verified (0.19) | RFC-0052 |
| `TEST-019` | AccessibilityScenario / axe SARIF | Verified (0.19) | RFC-0052 |
| `AT-019` | Automated Playwright/axe matrix | Verified (0.19) | D-050; human AT → 0.21 |
| `MEDIA-019` | Media / complex-content alternatives | Verified (0.19) | |
| `COG-019` | Cognitive / personalization helpers | Verified (0.19) | |
| `I18N-019` | Language / structure validation | Verified (0.19) | |
| `GOVERN-019` | Evidence inventory / statement / waivers | Verified (0.19) | RFC-0055 |
| `PE-019` | Progressive-enhancement forms | Verified (0.19) | #8 |
| `LANDMARK-019` | Landmark attrs / real types | Verified (0.19) | #27 #31 |
| `SCRIPT-019` | Allowlisted Page PE scripts | Verified (0.19) | #39 |
| `LIVE-011-BROWSER` | Full adapter live browser matrix | **Deferred** → `0.11.x` | Prior-phase carryover |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Deferred** → `0.10.x` | Prior-phase carryover |
| `PERF-10-001` | Load/proxy backpressure evidence | **Deferred** → `0.10.x` | SSE/WS ops proof |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | |

## Phase 0.19 evidence

- Closure index: [release-gate-0.19.toml](acceptance/release-gate-0.19.toml)
  (all `Verified`; zero-Deferred for 0.19-owned rows).
- Acceptance: [RELEASE_0_19.md](acceptance/RELEASE_0_19.md).
- Stability: [api/STABILITY.md](api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_19.py`.
- Cut procedure: [RELEASE.md](RELEASE.md) (last published: **0.18**; current cut target: **0.19**;
  next capability: **0.20**).

## Next capability phase

**0.20** — production security floor and adapter parity. Track progress in
[ROADMAP.md](ROADMAP.md) and the public [roadmap guide](guides/roadmap.md).
Open-issue owners: [issue ownership table](ROADMAP.md#open-github-issue-ownership-013).
Human AT / compensated evaluation follow-up remains owned by **0.21** (D-050).
