<!-- Generated from docs/STATUS.md — edit the docs/ copy, then run scripts/sync_status_roadmap.py -->

# Specification and implementation status

**Roadmap position:** phase 0.25 **Published** as `v0.25.0` (2026-08-09); last published
PyPI/git = `v0.25.1`. Workspace release candidate (not tagged): Beta `0.25.2`, charts /
sample-kit `0.1.6`, native `0.1.0`, notebook/mcp/gradio `0.1.0`.
**Date:** 2026-08-10
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` / `hedron-conformance` / `hedron-extras`
`0.25.2` candidate; Alpha (independent) — `hedron-charts` / `hedron-sample-kit` `0.1.6`,
`hedron-native` / `hedron-notebook` / `hedron-mcp` / `hedron-gradio` `0.1.0` (MIT, D-033).
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`, `hedron-conformance`, `hedron-extras`; Alpha —
`hedron-charts`, `hedron-sample-kit`, `hedron-native`, `hedron-notebook`, `hedron-mcp`,
`hedron-gradio`.

**Phase focus:** Living published train is **0.25** (D-053 production archetype + landmine
quarantine). Live-transport disposition remains **`polling_only`** from 0.24 — polling is the
Supported production story; live SSE/WS/streaming/preload remain **experimental**
(`hedron.experimental`). Human AT protocol remains **Verified** (`PROTOCOL-021`);
**`SR-021` / `PARTICIPANT-021` / `ARTIFACT-021` / `REMEDIATE-021` remain Planned** until real
sessions — **do not market human AT as Supported**. Automated AT (`AT-019`, phase 0.19)
remains Supported and is not a substitute for human AT. Production-quality maturity program
(**D-053** / RFC-0056) packet **0.25** is **Verified** — see
[production-quality](docs/guides/production-quality.md) ·
[PRODUCTION_ARCHETYPE](docs/api/PRODUCTION_ARCHETYPE.md).

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](docs/guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred** or still
**Planned**. Live SSE/WS/streaming/preload remain **experimental** (polling Supported —
`polling_only` Accepted in 0.24). Notebook preview, MCP, and Gradio interop are
**Experimental** / Alpha. Phase 0.20 closed with **zero Deferred** among **0.20 gate IDs**.
Phase 0.21 ships the engineering train with an honest human-AT gap: protocol Verified;
sessions Planned / not Supported. Phase **0.22** ships CSRF / SecurityPolicy composition with
**zero Deferred** among 0.22-owned rows. Phase **0.23** ships stable-tier expansion with
**zero Deferred** among 0.23-owned rows. Phase **0.24** ships live-transport disposition
`polling_only` with **zero Deferred** among 0.24-owned rows.

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
| `STABLE-023` | Expanded stable tier allowlist | **Verified** (0.23) | D-053 / RFC-0056 |
| `FACADE-023` | Beginner facade inventory | **Verified** (0.23) | [STABLE_FACADE](docs/api/STABLE_FACADE.md) |
| `INVENTORY-023` | Stability inventory checker | **Verified** (0.23) | |
| `REGRESS-023` | Full suite at 0.23 cut | **Verified** (0.23) | |
| `PKG-023` | `verify_pkg_23.py` packet evidence | **Verified** (0.23) | |
| `DECIDE-024` | Live disposition XOR (`polling_only`) | **Verified** (0.24) | D-053 / RFC-0056 |
| `BROWSER-024` | Browser waive ledger for prior live IDs | **Verified** (0.24) | [waive-browser-024.toml](docs/acceptance/waive-browser-024.toml) |
| `PERF-024` | Perf waive ledger for `PERF-10-001` | **Verified** (0.24) | [waive-perf-024.toml](docs/acceptance/waive-perf-024.toml) |
| `DOCS-024` | Docs train SSOT + live-claim honesty | **Verified** (0.24) | |
| `REGRESS-024` | Full suite at 0.24 cut | **Verified** (0.24) | |
| `PKG-024` | `verify_pkg_24.py` packet evidence | **Verified** (0.24) | |
| `ARCHETYPE-025` | Reference-app production archetype | **Verified** (0.25) | `examples/reference-app` |
| `BUDGET-025` | Critical-path load budgets | **Verified** (0.25) | `W-025-*` |
| `EXTRAS-025` | Extras landmine quarantine XOR | **Verified** (0.25) | `quarantine` → `hedron[experimental-ui]` |
| `CHARTS-025` | Matplotlib-default / Plotly–Altair path | **Verified** (0.25) | |
| `SUPPLY-025` | SBOM/evidence attach on train tags | **Verified** (0.25) | process |
| `REGRESS-025` | Full suite at 0.25 cut | **Verified** (0.25) | |
| `PKG-025` | `verify_pkg_25.py` packet evidence | **Verified** (0.25) | |
| `LIVE-011-BROWSER` | Full adapter live browser matrix | **Superseded** (0.24) | By `DECIDE-024` `polling_only` / `BROWSER-024` |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Superseded** (0.24) | By `DECIDE-024` `polling_only` / `BROWSER-024` |
| `PERF-10-001` | Load/proxy backpressure evidence | **Superseded** (0.24) | By `DECIDE-024` `polling_only` / `PERF-024` |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | **Not** re-homed to 0.24; stays on `0.10.x` |

## Phase 0.24 evidence

- Gate index: [release-gate-0.24.toml](docs/acceptance/release-gate-0.24.toml)
  (all `Verified`; zero-Deferred for 0.24-owned rows).
- Acceptance: [RELEASE_0_24.md](docs/acceptance/RELEASE_0_24.md).
- Disposition: [api/LIVE_DISPOSITION.md](docs/api/LIVE_DISPOSITION.md) ·
  [live-disposition-024.toml](docs/acceptance/live-disposition-024.toml) (`polling_only`).
- Waive ledgers: [waive-browser-024.toml](docs/acceptance/waive-browser-024.toml) ·
  [waive-perf-024.toml](docs/acceptance/waive-perf-024.toml).
- What’s new: [guides/whats-new-0.24.md](docs/guides/whats-new-0.24.md).
- Checker: `python scripts/check_release_gate.py 0.24.0`,
  `python scripts/verify_pkg_24.py`.

## Phase 0.23 evidence (prior)

- Gate index: [release-gate-0.23.toml](docs/acceptance/release-gate-0.23.toml)
  (all `Verified`; zero-Deferred for 0.23-owned rows).
- Acceptance: [RELEASE_0_23.md](docs/acceptance/RELEASE_0_23.md).
- Contracts: [api/STABILITY.md](docs/api/STABILITY.md) · [api/STABLE_FACADE.md](docs/api/STABLE_FACADE.md).
- What’s new: [guides/whats-new-0.23.md](docs/guides/whats-new-0.23.md).
- Checker: `python scripts/check_release_gate.py 0.23.0`,
  `python scripts/verify_pkg_23.py`.

## Phase 0.22 evidence (prior)

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

## Phase 0.25 evidence

All `*-025` capability gates are **Verified** on the Published `v0.25.0` train:

| Gate | Disposition |
|---|---|
| `ARCHETYPE-025` | Verified — `examples/reference-app` production archetype |
| `BUDGET-025` | Verified — `W-025-*` soft CI budgets |
| `EXTRAS-025` | Verified — quarantine via `hedron[experimental-ui]` + discovery gates |
| `CHARTS-025` | Verified — Matplotlib Supported default; Plotly/Altair path documented |
| `SUPPLY-025` | Verified — atomic SBOM/evidence attach on train tags |
| `REGRESS-025` / `PKG-025` | Verified — suite + `verify_pkg_25.py` |

SSOT: [PRODUCTION_ARCHETYPE](docs/api/PRODUCTION_ARCHETYPE.md) ·
[RELEASE_0_25](docs/acceptance/RELEASE_0_25.md) ·
[release-gate-0.25.toml](docs/acceptance/release-gate-0.25.toml).
Cut verify: `python scripts/verify_pkg_25.py`.
Program summary: [production-quality guide](docs/guides/production-quality.md).

## Next capability phases

Human AT sessions (`SR-021` / `PARTICIPANT-021` / `ARTIFACT-021` / `REMEDIATE-021`) remain
**Planned** until compensated screen-reader evidence lands. The roadmap now assigns the remaining
package-production work to planned phases **0.26–0.32**: core/FastAPI/Explorer; supported Python
satellites; charts/native; developer and portable conformance tooling; MCP; Gradio; then a
whole-fleet closure audit. These phases require owning RFCs/decisions and Verified evidence before
any package maturity label changes. They do not schedule `1.0`, promote every experimental
subfeature, or change the current 0.25 readiness claims.
