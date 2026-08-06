<!-- Generated from docs/STATUS.md — edit the docs/ copy, then run scripts/sync_status_roadmap.py -->

# Specification and implementation status

**Roadmap position:** phase 0.18 **Published** as `v0.18.0` (2026-08-06). Workspace packages:
Beta `0.18.0`, Alpha charts/sample-kit/native `0.1.x`, Alpha notebook/mcp/gradio `0.1.0`.
**Date:** 2026-08-06
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` / `hedron-conformance` / `hedron-extras`
`0.18.0`; Alpha (independent) — `hedron-charts` / `hedron-sample-kit` / `hedron-native` /
`hedron-notebook` / `hedron-mcp` / `hedron-gradio` `0.1.x` (MIT, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`, `hedron-conformance`, `hedron-extras`; Alpha —
`hedron-charts`, `hedron-sample-kit`, `hedron-native`, `hedron-notebook`, `hedron-mcp`,
`hedron-gradio`.

**Phase focus:** model demos and inference workflows — `InferenceInterface` / `ModelDemo`,
`ExampleSet` / presentation / `PredictionFeedback`, `InferencePolicy`, `InteractionRecorder`,
`InferenceWorkflow`, optional `hedron-gradio` (Experimental).

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](docs/guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred**. Live
SSE/WS/streaming/preload remain **experimental** (polling Supported). Notebook preview, MCP, and
Gradio interop are **Experimental** / Alpha. Phase 0.18 closed with **zero Deferred** among
**0.18 gate IDs** (`check_release_gate.py 0.18.0`); prior-phase Deferred rows below remain owned
elsewhere.

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
| `SCENARIO-018` | ModelDemoScenario | Verified (0.18) | RFC-0047 |
| `DEMO-018` | InferenceInterface / ModelDemo | Verified (0.18) | RFC-0045 |
| `EXAMPLE-018` | ExampleSet | Verified (0.18) | RFC-0046 |
| `PRESENT-018` | PredictionLabel / ParameterViewer / Dialogue | Verified (0.18) | |
| `FEEDBACK-018` | PredictionFeedback | Verified (0.18) | |
| `INFER-018` | InferencePolicy | Verified (0.18) | RFC-0047 |
| `RECORD-018` | InteractionRecorder | Verified (0.18) | RFC-0048 |
| `WORKFLOW-018` | InferenceWorkflow | Verified (0.18) | RFC-0050 |
| `GRADIO-018` | hedron-gradio adapter | Verified (0.18) | Experimental |
| `MIGRATE-018` | Gradio migration inventory | Verified (0.18) | |
| `LIVE-011-BROWSER` | Full adapter live browser matrix | **Deferred** → `0.11.x` | Prior-phase carryover |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Deferred** → `0.10.x` | Prior-phase carryover |
| `PERF-10-001` | Load/proxy backpressure evidence | **Deferred** → `0.10.x` | SSE/WS ops proof |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | |

## Phase 0.18 evidence

- Closure index: [release-gate-0.18.toml](docs/acceptance/release-gate-0.18.toml)
  (all `Verified`; zero-Deferred for 0.18-owned rows).
- Acceptance: [RELEASE_0_18.md](docs/acceptance/RELEASE_0_18.md).
- Stability: [api/STABILITY.md](docs/api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](docs/COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](docs/guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_18.py`.
- Cut procedure: [RELEASE.md](docs/RELEASE.md) (last published: **0.18**; next capability: **0.19**).

## Next capability phase

**0.19** — accessibility engineering and inclusive authoring. Track progress in
[ROADMAP.md](docs/ROADMAP.md) and the public [roadmap guide](docs/guides/roadmap.md).
Open-issue owners: [issue ownership table](ROADMAP.md#open-github-issue-ownership-013).
