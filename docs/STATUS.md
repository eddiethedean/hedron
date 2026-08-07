# Specification and implementation status

**Roadmap position:** phase 0.20 **Ready to cut / Implemented on `main`** as `0.20.0`
(2026-08-07); last published PyPI/git = `v0.18.0`. Workspace packages:
Beta `0.20.0`, Alpha charts/sample-kit/native `0.1.x`, Alpha notebook/mcp/gradio `0.1.0`.
**Date:** 2026-08-07
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` / `hedron-conformance` / `hedron-extras`
`0.20.0` on `main`; Alpha (independent) — `hedron-charts` / `hedron-sample-kit` /
`hedron-native` / `hedron-notebook` / `hedron-mcp` / `hedron-gradio` `0.1.x` (MIT, D-033).
PyPI/git still serve **`v0.18.0`** until `v0.20.0` is tagged and published.
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`, `hedron-conformance`, `hedron-extras`; Alpha —
`hedron-charts`, `hedron-sample-kit`, `hedron-native`, `hedron-notebook`, `hedron-mcp`,
`hedron-gradio`.

**Phase focus:** production security floor and adapter parity — HTMX/eval hardening, mount-path
helpers, production startup gates, Flask/Django regions/CSP/AuthSignal, adapter scaffolds and
wheel smoke (D-051). CSRF composition Deferred → **0.22**. Human AT Deferred → **0.21**
(D-050).

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred**. Live
SSE/WS/streaming/preload remain **experimental** (polling Supported). Notebook preview, MCP, and
Gradio interop are **Experimental** / Alpha. Phase 0.20 closed with **zero Deferred** among
**0.20 gate IDs** (`check_release_gate.py 0.20.0`); human screen-reader / compensated user
evaluation is owned by **0.21** (D-050). CSRF / SecurityPolicy composition is owned by **0.22**.
Prior-phase Deferred rows below remain owned elsewhere.

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
| — | Accessibility engineering / PE | Verified (0.19) | D-050 |
| `HTMX-020` | HTMX browser preset | Verified (0.20) | #1 |
| `EVAL-020` | Python `hx-vals`/`hx-headers` `js:` reject | Verified (0.20) | #18 |
| `MOUNT-020` | Trusted mount path / cookie Path=auto | Verified (0.20) | #3 |
| `PROD-020` | Production security startup gates | Verified (0.20) | #6 |
| `REGION-020` | Flask/Django fragment_regions | Verified (0.20) | #12 |
| `CSP-020` | Portable SecurityPolicy headers on adapters | Verified (0.20) | #14 |
| `AUTH-020` | Flask-Login AuthSignal | Verified (0.20) | #20 |
| `SCAFFOLD-020` | `hedron new --flask` / `--django` | Verified (0.20) | #17 |
| `WHEEL-020` | Adapter clean-wheel CI smoke | Verified (0.20) | #19 |
| `LIVE-011-BROWSER` | Full adapter live browser matrix | **Deferred** → `0.11.x` | Prior-phase carryover |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Deferred** → `0.10.x` | Prior-phase carryover |
| `PERF-10-001` | Load/proxy backpressure evidence | **Deferred** → `0.10.x` | SSE/WS ops proof |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | |

## Phase 0.20 evidence

- Closure index: [release-gate-0.20.toml](acceptance/release-gate-0.20.toml)
  (all `Verified`; zero-Deferred for 0.20-owned rows).
- Acceptance: [RELEASE_0_20.md](acceptance/RELEASE_0_20.md).
- Stability: [api/STABILITY.md](api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_20.py`.
- Cut procedure: [RELEASE.md](RELEASE.md) (last published: **0.18**; current cut target: **0.20**;
  next capability: **0.21** human AT / **0.22** CSRF composition).

## Next capability phases

**0.21** — human assistive-technology / compensated evaluation (D-050).
**0.22** — CSRF and SecurityPolicy composition (#36–#38; D-051 split).
Track progress in [ROADMAP.md](ROADMAP.md) and the public [roadmap guide](guides/roadmap.md).
Open-issue owners: [issue ownership table](ROADMAP.md#open-github-issue-ownership-013).
