<!-- Generated from docs/STATUS.md — edit the docs/ copy, then run scripts/sync_status_roadmap.py -->

# Specification and implementation status

**Roadmap position:** phase 0.22 **Published** as `v0.22.0` (2026-08-08); last published
PyPI/git = `v0.22.0`. Workspace packages: Beta `0.22.0`, Alpha charts/sample-kit/native
`0.1.x`, Alpha notebook/mcp/gradio `0.1.0`.
**Date:** 2026-08-08
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` / `hedron-conformance` / `hedron-extras`
`0.22.0`; Alpha (independent) — `hedron-charts` / `hedron-sample-kit` /
`hedron-native` / `hedron-notebook` / `hedron-mcp` / `hedron-gradio` `0.1.x` (MIT, D-033).
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`, `hedron-conformance`, `hedron-extras`; Alpha —
`hedron-charts`, `hedron-sample-kit`, `hedron-native`, `hedron-notebook`, `hedron-mcp`,
`hedron-gradio`.

**Phase focus:** Living published train is **0.22** (D-051 CSRF / SecurityPolicy composition).
Human AT protocol remains **Verified** (`PROTOCOL-021`); **`SR-021` / `PARTICIPANT-021` /
`ARTIFACT-021` / `REMEDIATE-021` remain Planned** until real sessions — **do not market human
AT as Supported**. Automated AT (`AT-019`, phase 0.19) remains Supported and is not a
substitute for human AT. Production-quality maturity program (**D-053** / RFC-0056) assigns
post-0.22 packets **0.23** (stable-tier), **0.24** (live disposition), **0.25**
(archetype / landmines) — see [production-quality](docs/guides/production-quality.md).

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](docs/guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred** or still
**Planned**. Live SSE/WS/streaming/preload remain **experimental** (polling Supported).
Notebook preview, MCP, and Gradio interop are **Experimental** / Alpha. Phase 0.20 closed with
**zero Deferred** among **0.20 gate IDs**. Phase 0.21 ships the engineering train with an
honest human-AT gap: protocol Verified; sessions Planned / not Supported. Phase **0.22**
ships CSRF / SecurityPolicy composition with **zero Deferred** among 0.22-owned rows.
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
| — | Production security / adapter parity | Verified (0.20) | D-051 |
| `PROTOCOL-021` | Human AT protocol packet | **Verified** (0.21) | D-052 engineering |
| `SR-021` | VoiceOver / NVDA / TalkBack matrix | **Planned** (0.21) | sessions outstanding |
| `PARTICIPANT-021` | Compensated participant floor | **Planned** (0.21) | sessions outstanding |
| `ARTIFACT-021` | Redacted ledger + statement update | **Planned** (0.21) | after sessions |
| `REMEDIATE-021` | Blocker fix / waiver | **Planned** (0.21) | after sessions |
| `REGRESS-021` | Full suite at cut | **Verified** (0.21) | engineering publish |
| `PKG-021` | `verify_pkg_21.py` packet evidence | **Verified** (0.21) | engineering publish |
| `CSRF-022` | Pluggable CSRF strategies | **Verified** (0.22) | D-051; [#36](https://github.com/eddiethedean/hedron/issues/36) |
| `HEADERS-022` | Composable SecurityPolicy headers | **Verified** (0.22) | D-051; [#37](https://github.com/eddiethedean/hedron/issues/37) |
| `FORM-022` | `CsrfField` + Form HTMX kwargs | **Verified** (0.22) | D-051; [#38](https://github.com/eddiethedean/hedron/issues/38) |
| `REGRESS-022` | Full suite at 0.22 cut | **Verified** (0.22) | |
| `PKG-022` | `verify_pkg_22.py` packet evidence | **Verified** (0.22) | |
| `LIVE-011-BROWSER` | Full adapter live browser matrix | **Deferred** → `0.11.x` | Prior-phase carryover; disposition → **0.24** (D-053) |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Deferred** → `0.10.x` | Prior-phase carryover; disposition → **0.24** (D-053) |
| `PERF-10-001` | Load/proxy backpressure evidence | **Deferred** → `0.10.x` | SSE/WS ops proof; disposition → **0.24** (D-053) |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | |

## Phase 0.22 evidence

- Gate index: [release-gate-0.22.toml](docs/acceptance/release-gate-0.22.toml)
  (all `Verified`; zero-Deferred for 0.22-owned rows).
- Acceptance: [RELEASE_0_22.md](docs/acceptance/RELEASE_0_22.md).
- Contract: [api/CSRF_COMPOSITION.md](docs/api/CSRF_COMPOSITION.md).
- What’s new: [guides/whats-new-0.22.md](docs/guides/whats-new-0.22.md).
- Checker: `python scripts/check_release_gate.py 0.22.0`,
  `python scripts/verify_pkg_22.py`.

## Phase 0.21 evidence (prior)

- Gate index: [release-gate-0.21.toml](docs/acceptance/release-gate-0.21.toml)
  (`PROTOCOL-021` / `REGRESS-021` / `PKG-021` Verified; SR/PARTICIPANT/ARTIFACT/REMEDIATE Planned).
- Acceptance: [RELEASE_0_21.md](docs/acceptance/RELEASE_0_21.md).
- Protocol: [acceptance/human-at/](docs/acceptance/human-at/).
- What’s new: [guides/whats-new-0.21.md](docs/guides/whats-new-0.21.md).
- Checker: `python scripts/check_release_gate.py 0.21.0 --allow-planned`,
  `python scripts/check_human_at_packet.py`, `python scripts/verify_pkg_21.py`.
- Human AT is **not** Supported for adopter marketing until remaining gates are Verified after
  real sessions. `--require-sessions` must still fail on placeholder-only ledger.

## Phase 0.20 evidence (prior)

- Closure index: [release-gate-0.20.toml](docs/acceptance/release-gate-0.20.toml)
  (all `Verified`; zero-Deferred for 0.20-owned rows).
- Acceptance: [RELEASE_0_20.md](docs/acceptance/RELEASE_0_20.md).
- Stability: [api/STABILITY.md](docs/api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](docs/COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](docs/guides/upgrade.md).

## Next capability phases

**0.23** — Stable-tier expansion for Supported CRUD/admin (D-053 / RFC-0056).
**Packet refine complete:** locked narrow promotion allowlist + distinct gate commands
([ROADMAP §0.23](docs/ROADMAP.md), [STABLE_FACADE](docs/api/STABLE_FACADE.md)); gates remain
**Planned** until cut (`STABLE-023` … `PKG-023`).
**0.24** — Live-transport production disposition (prove ops **or** polling-only; D-053).
**0.25** — Production archetype, load budgets, extras quarantine (D-053).
Program summary: [production-quality guide](docs/guides/production-quality.md).

Cut procedure: [RELEASE.md](docs/RELEASE.md).
