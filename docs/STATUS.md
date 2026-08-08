# Specification and implementation status

**Roadmap position:** phase 0.20 **Published** as `v0.20.0` (2026-08-07); last published
PyPI/git = `v0.20.0`. Workspace packages: Beta `0.20.0`, Alpha charts/sample-kit/native
`0.1.x`, Alpha notebook/mcp/gradio `0.1.0`.
**Date:** 2026-08-07
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` / `hedron-conformance` / `hedron-extras`
`0.20.0`; Alpha (independent) — `hedron-charts` / `hedron-sample-kit` /
`hedron-native` / `hedron-notebook` / `hedron-mcp` / `hedron-gradio` `0.1.x` (MIT, D-033).
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`, `hedron-conformance`, `hedron-extras`; Alpha —
`hedron-charts`, `hedron-sample-kit`, `hedron-native`, `hedron-notebook`, `hedron-mcp`,
`hedron-gradio`.

**Phase focus:** Living published train remains **0.20** (D-051). Next capability packet
**0.21** human AT is **engineering-complete / sessions outstanding** (D-052): protocol
Verified (`PROTOCOL-021`); reference-app task corpus + `verify_pkg_21` + CI packet checks
landed; **`SR-021` / `PARTICIPANT-021` remain Planned** until real sessions. CSRF composition
remains Deferred → **0.22**. Production-quality maturity program (**D-053** / RFC-0056)
assigns post-0.22 packets **0.23** (stable-tier), **0.24** (live disposition), **0.25**
(archetype / landmines) — see [production-quality](guides/production-quality.md).

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred** or still
**Planned**. Live SSE/WS/streaming/preload remain **experimental** (polling Supported).
Notebook preview, MCP, and Gradio interop are **Experimental** / Alpha. Phase 0.20 closed with
**zero Deferred** among **0.20 gate IDs** (`check_release_gate.py 0.20.0`). Human screen-reader /
compensated user evaluation is owned by **0.21** (D-052; engineering-complete — PROTOCOL Verified;
sessions outstanding — not Supported). CSRF / SecurityPolicy composition is owned by **0.22**.
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
| `PROTOCOL-021` | Human AT protocol packet | **Verified** (0.21) | D-052 engineering |
| `SR-021` | VoiceOver / NVDA / TalkBack matrix | **Planned** (0.21) | sessions outstanding |
| `PARTICIPANT-021` | Compensated participant floor | **Planned** (0.21) | sessions outstanding |
| `ARTIFACT-021` | Redacted ledger + statement update | **Planned** (0.21) | after sessions |
| `REMEDIATE-021` | Blocker fix / waiver | **Planned** (0.21) | after sessions |
| `REGRESS-021` | Full suite at cut | **Planned** (0.21) | cut |
| `PKG-021` | `verify_pkg_21.py` packet evidence | **Planned** (0.21) | command ready; Verified at cut |
| `LIVE-011-BROWSER` | Full adapter live browser matrix | **Deferred** → `0.11.x` | Prior-phase carryover; disposition → **0.24** (D-053) |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Deferred** → `0.10.x` | Prior-phase carryover; disposition → **0.24** (D-053) |
| `PERF-10-001` | Load/proxy backpressure evidence | **Deferred** → `0.10.x` | SSE/WS ops proof; disposition → **0.24** (D-053) |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | |

## Phase 0.20 evidence

- Closure index: [release-gate-0.20.toml](acceptance/release-gate-0.20.toml)
  (all `Verified`; zero-Deferred for 0.20-owned rows).
- Acceptance: [RELEASE_0_20.md](acceptance/RELEASE_0_20.md).
- Stability: [api/STABILITY.md](api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_20.py`.
- Cut procedure: [RELEASE.md](RELEASE.md) (last published: **0.20**; next capability: **0.21**
  human AT / **0.22** CSRF composition).

## Phase 0.21 packet (engineering-complete / sessions outstanding)

- Decision: D-052; RFC baseline [RFC-0055](rfcs/RFC-0055-A11Y-GOVERNANCE.md) (amended).
- Gate index: [release-gate-0.21.toml](acceptance/release-gate-0.21.toml)
  (`PROTOCOL-021` Verified; SR/PARTICIPANT/ARTIFACT/REMEDIATE/REGRESS/PKG Planned).
- Acceptance: [RELEASE_0_21.md](acceptance/RELEASE_0_21.md).
- Protocol: [acceptance/human-at/](acceptance/human-at/).
- Checker: `python scripts/check_release_gate.py 0.21.0 --allow-planned`,
  `python scripts/check_human_at_packet.py`, `python scripts/verify_pkg_21.py`.
- Human AT is **not** Supported for adopter marketing until remaining gates are Verified and
  `v0.21.0` is Published. `--require-sessions` must still fail on placeholder-only ledger.

## Next capability phases

**0.21** — human assistive-technology / compensated evaluation (engineering prep complete;
sessions outstanding; D-052).
**0.22** — CSRF and SecurityPolicy composition (#36–#38; D-051 split).
**0.23** — Stable-tier expansion for Supported CRUD/admin (D-053 / RFC-0056).
**0.24** — Live-transport production disposition (prove ops **or** polling-only; D-053).
**0.25** — Production archetype, load budgets, extras quarantine (D-053).
Program summary: [production-quality guide](guides/production-quality.md).
Track progress in [ROADMAP.md](ROADMAP.md) and the public [roadmap guide](guides/roadmap.md).
Open-issue owners: [issue ownership table](ROADMAP.md#open-github-issue-ownership-013).
