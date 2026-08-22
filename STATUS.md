<!-- Generated from docs/STATUS.md — edit the docs/ copy, then run scripts/sync_status_roadmap.py -->

# Specification and implementation status

> **Adopters:** this file is a **maintainer ledger** (gate IDs, phase evidence). For
> product readiness use [What’s ready](docs/guides/whats-ready.md); for the public roadmap use
> [What’s next](docs/guides/whats-next.md). Do not treat gate tables as the getting-started guide.

**Roadmap position:** phase 0.58 **Published** as `v0.58.0`; PyPI serves `0.58.0`.
Living tip = published `v0.58.0` (`registry_status = "uploaded"`).
**Date:** 2026-08-21
**Implementation:** Beta — `hedron` / `hedron-core` / `hedron-explorer` / `hedron-data` /
`hedron-flask` / `hedron-django` / `hedron-jinja` / `hedron-conformance` / `hedron-extras` /
`hedron-workbench` / `hedron-posit` / `hedron-elements` `0.58.0`;
Beta (independent) — `fastapi-workbench` `1.0.0`, `hedron-maps`
`0.1.0`, `hedron-charts`
`0.2.0`, `hedron-native` `0.1.2`, `hedron-sample-kit` / `hedron-notebook` /
`hedron-sim` `0.2.0`, `hedron-mcp` `0.2.1`, `hedron-gradio` `0.2.0`, `hedron-runtime-node` / `hedron-runtime-java`
`0.58.0`
(MIT, D-033).
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`, `hedron-conformance`, `hedron-extras`,
`hedron-workbench`, `hedron-posit`, `hedron-elements` (Supported inventory only), `hedron-maps`, `hedron-charts`,
`hedron-native`, `hedron-sample-kit`, `hedron-notebook`, `hedron-sim`, `hedron-mcp`, `hedron-gradio`.
Independent (not coordinated Beta train): `fastapi-workbench` `1.0.0`; experimental runtimes
`hedron-runtime-node` / `hedron-runtime-java` `0.58.0`.

**Phase focus:** Living train is **0.58** (D-101 / D-102 / D-105 / RFC-0085) — progressive
feature and styling authoring. `release-gate-0.58.toml` Verified rows; living tip `v0.58.0`
is on PyPI (`registry_status = "uploaded"`). Prior Published
in-tree **0.57** unified presentation / zero-application-CSS
(D-099 / D-100 / RFC-0084; [#570](https://github.com/eddiethedean/hedron/issues/570);
[#558](https://github.com/eddiethedean/hedron/issues/558)–[#569](https://github.com/eddiethedean/hedron/issues/569)).
Prior Published **0.56** security control plane
(D-097 / D-098 / RFC-0083; [#550](https://github.com/eddiethedean/hedron/issues/550)–[#557](https://github.com/eddiethedean/hedron/issues/557)).
Prior Published **0.55** secure upgradeable workflows
(D-095 / D-096 / RFC-0082; [#544](https://github.com/eddiethedean/hedron/issues/544)–[#549](https://github.com/eddiethedean/hedron/issues/549)).
Prior Published **0.54** authoring-loop / chrome (D-093 / D-094 / RFC-0081;
[#538](https://github.com/eddiethedean/hedron/issues/538)–[#543](https://github.com/eddiethedean/hedron/issues/543)).
Prior Published in-tree **0.53** application DX
(D-091 / D-092 / RFC-0080; [#514](https://github.com/eddiethedean/hedron/issues/514)–[#521](https://github.com/eddiethedean/hedron/issues/521)).
Prior Published in-tree **0.52** conformance authority and HedronPosit lifecycle
(D-089 / D-090 / RFC-0079; [#522](https://github.com/eddiethedean/hedron/issues/522);
companions [#508](https://github.com/eddiethedean/hedron/issues/508)–[#513](https://github.com/eddiethedean/hedron/issues/513)).
Prior Published **0.51** curated extras depth
(D-087 / D-088 / RFC-0078; [#507](https://github.com/eddiethedean/hedron/issues/507)).
Prior in-tree **0.50** Explorer architecture
(D-085 / D-086 / RFC-0077; [#501](https://github.com/eddiethedean/hedron/issues/501)).
Prior Published **0.49** FastAPI/Pydantic convergence
(D-081 / D-084 / RFC-0076; [#380](https://github.com/eddiethedean/hedron/issues/380)).

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](docs/guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred** or still
**Planned**. Live SSE/WS/streaming/preload remain **experimental** (polling Supported —
`polling_only` Accepted in 0.24). Notebook preview is tooling-grade / localhost-only;
MCP is Beta for the declared Supported inventory (0.32 / `hedron-mcp` `0.2.1`); Gradio remote
client interop is Beta for declared allowlisted destinations (0.34 / `hedron-gradio` `0.2.0`). Phase 0.20 closed with **zero Deferred** among **0.20 gate IDs**.
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
| `SR-021` | VoiceOver / NVDA / TalkBack matrix | **Planned** (0.21) | sessions outstanding; [#86](https://github.com/eddiethedean/hedron/issues/86) |
| `PARTICIPANT-021` | Compensated participant floor | **Planned** (0.21) | sessions outstanding; [#86](https://github.com/eddiethedean/hedron/issues/86) |
| `ARTIFACT-021` | Redacted ledger + statement update | **Planned** (0.21) | after sessions; [#86](https://github.com/eddiethedean/hedron/issues/86) |
| `REMEDIATE-021` | Blocker fix / waiver | **Planned** (0.21) | after sessions; [#86](https://github.com/eddiethedean/hedron/issues/86) |
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
| `DATA-027` | Bounded data CRUD / sources / exports | **Verified** (0.27) | D-055 / RFC-0058 |
| `FLASK-027` | Host-only Flask adapter matrices | **Verified** (0.27) | |
| `DJANGO-027` | Host-only Django adapter matrices | **Verified** (0.27) | |
| `HDJ-027` | Versioned HDJ authoring | **Verified** (0.27) | |
| `EXTRAS-027` | Curated extras + experimental-ui quarantine | **Verified** (0.27) | |
| `PARITY-027` | Portable FastAPI/Flask/Django parity | **Verified** (0.27) | |
| `REGRESS-027` | Full suite at 0.27 cut | **Verified** (0.27) | |
| `PKG-027` | `verify_pkg_27.py` packet evidence | **Verified** (0.27) | |
| `LIVE-011-BROWSER` | Full adapter live browser matrix | **Superseded** (0.24) | By `DECIDE-024` `polling_only` / `BROWSER-024` |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Superseded** (0.24) | By `DECIDE-024` `polling_only` / `BROWSER-024` |
| `PERF-10-001` | Load/proxy backpressure evidence | **Superseded** (0.24) | By `DECIDE-024` `polling_only` / `PERF-024` |
| `MORPH-048` | Idiomorph / morph swap | **Deferred** (0.48) | Not vendored; keep innerHTML/outerHTML; later train, not 0.49 |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | **Not** re-homed to 0.24; stays on `0.10.x` |

## Phase 0.58 evidence

- Gate index: [release-gate-0.58.toml](docs/acceptance/release-gate-0.58.toml)
  (all twenty `*-058` rows **Verified**; zero Deferred).
- Acceptance: [RELEASE_0_58.md](docs/acceptance/RELEASE_0_58.md).
- Contracts / inventories: [progressive-tracking-058.toml](docs/acceptance/progressive-tracking-058.toml) ·
  [progressive-starter-docs-058.toml](docs/acceptance/progressive-starter-docs-058.toml) ·
  [upgrade-fixtures-058.md](docs/acceptance/upgrade-fixtures-058.md).
- Implementation: [PROGRESSIVE_AUTHORING_058](docs/implementation/PROGRESSIVE_AUTHORING_058.md).
- What’s new: [guides/whats-new-0.58.md](docs/guides/whats-new-0.58.md).
- Checker: `python scripts/check_release_gate.py 0.58.0`,
  `python scripts/verify_pkg_58.py`.
- Registry: PyPI serves `v0.58.0` (`registry_status = "uploaded"`).

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

## Phase 0.27 evidence

All `*-027` capability gates are **Verified** on the Published `v0.27.0` train:

| Gate | Disposition |
|---|---|
| `DATA-027` | Verified — bounded data CRUD/sources/exports + upgrade fixtures |
| `FLASK-027` | Verified — host-only Flask install/security/lifecycle evidence |
| `DJANGO-027` | Verified — host-only Django install/system-check evidence |
| `HDJ-027` | Verified — HDJ v1 prologue/sinks/async/manifests |
| `EXTRAS-027` | Verified — curated registry + experimental-ui quarantine |
| `PARITY-027` | Verified — portable PAGE/FRAGMENT/CSRF parity + REVIEW-027 |
| `REGRESS-027` / `PKG-027` | Verified — suite + `verify_pkg_27.py` |

SSOT: [RELEASE_0_27](docs/acceptance/RELEASE_0_27.md) ·
[release-gate-0.27.toml](docs/acceptance/release-gate-0.27.toml) ·
[production-grade-inventory-027.toml](docs/acceptance/production-grade-inventory-027.toml).
Cut verify: `python scripts/verify_pkg_27.py`.

## Phase 0.28 evidence

Owning decision: **D-056** / [RFC-0059](docs/rfcs/RFC-0059-PRODUCTION-GRADE-CHARTS-NATIVE.md).
Baseline: Published **`v0.27.0`**. Packages: `hedron-charts` `0.1.11` / `hedron-native`
`0.1.2` — **Beta** for declared Supported inventories.
Locked Supported inventory:
[production-grade-inventory-028.toml](docs/acceptance/production-grade-inventory-028.toml).

| Gate | Status |
|---|---|
| `CHARTS-028` | Verified — static/beginner Supported matrices |
| `INTERACTIVE-028` | Verified — Experimental labels + no production defaults |
| `NATIVE-028` | Verified — wheels / fuzz / sanitizer / fallback injection |
| `SUPPLY-028` | Verified — pins / SBOM / offline / provenance |
| `REGRESS-028` / `PKG-028` | Verified — suite + `verify_pkg_28.py` |

SSOT: [RELEASE_0_28](docs/acceptance/RELEASE_0_28.md) ·
[release-gate-0.28.toml](docs/acceptance/release-gate-0.28.toml) ·
[production-grade-inventory-028.toml](docs/acceptance/production-grade-inventory-028.toml).
Cut verify: `python scripts/verify_pkg_28.py`.

## Phase 0.29 evidence

Owning decision: **D-057** / [RFC-0062](docs/rfcs/RFC-0062-POSIT-WORKBENCH-ADAPTER.md).
Baseline: Published **`v0.28.2`**. Package: `hedron-workbench` `0.30.0` — **Beta**
for the declared Supported inventory.
Locked Supported inventory:
[production-grade-inventory-029.toml](docs/acceptance/production-grade-inventory-029.toml).

| Gate | Status |
|---|---|
| `CONTRACT-029` | Verified — RFC-0062 / D-057 / inventory |
| `RESOLVE-029` | Verified — pure resolver corpus |
| `PATH-029` | Verified — ASGI middleware + 0.3.4 parity (Hedron-adapted) |
| `URL-029` | Verified — mount/redirect/CSRF/cookie/HTMX/assets |
| `RUNNER-029` | Verified — pre-bind launcher + CLI |
| `DX-029` | Verified — check/dry-run + docs |
| `SECURITY-029` | Verified — adversarial suite + review packet |
| `REALWB-029` | Verified — Docker smoke + redacted RESULT.log |
| `COMPAT-029` / `PERF-029` | Verified — isolation/upgrade + middleware budget |
| `REGRESS-029` / `PKG-029` | Verified — suite + `verify_pkg_29.py` |

SSOT: [RELEASE_0_29](docs/acceptance/RELEASE_0_29.md) ·
[release-gate-0.29.toml](docs/acceptance/release-gate-0.29.toml) ·
[production-grade-inventory-029.toml](docs/acceptance/production-grade-inventory-029.toml).
Cut verify: `python scripts/verify_pkg_29.py`.

## Phase 0.32 evidence (Verified — MCP graduation; published `v0.32.0`)

**Owning decision / RFC:** [D-060](docs/DECISIONS.md) ·
[RFC-0065](docs/rfcs/RFC-0065-PRODUCTION-GRADE-MCP.md). Alpha product contract remains
[RFC-0043](docs/rfcs/RFC-0043-MCP-PROJECTION.md) (0.17).
**Baseline tip:** Published `v0.31.0`.
**Tracking:** [#89](https://github.com/eddiethedean/hedron/issues/89).
**Version policy at cut:** independent satellite `hedron-mcp` **`0.2.0` Beta**
(pin `>=0.2.0,<0.3`; current satellite is **`0.2.1`**).

| ID | Disposition | Notes |
|---|---|---|
| `PROTOCOL-032` | **Verified** | Streamable HTTP + SDK matrix + upgrade fixtures |
| `AUTHZ-032` | **Verified** | Host authn reuse; app authz/tenant; adversarial suites |
| `BOUNDS-032` | **Verified** | Size/rate/concurrency/cancel + multi-worker prefix |
| `AUDIT-032` | **Verified** | Redacted structured `HED-MCP-*` audit |
| `REVIEW-032` | **Verified** | [security-review-032](docs/acceptance/security-review-032/BRIEF.md) |
| `REGRESS-032` / `PKG-032` | **Verified** | Inventory/docs/metadata + `verify_pkg_32.py` |

SSOT: [RELEASE_0_32](docs/acceptance/RELEASE_0_32.md) ·
[release-gate-0.32.toml](docs/acceptance/release-gate-0.32.toml) ·
[production-grade-inventory-032.toml](docs/acceptance/production-grade-inventory-032.toml).
Cut verify: `python scripts/verify_pkg_32.py` (no `--allow-planned`).

## Phase 0.37 evidence (Verified — form-associated elements; published `v0.38.0`)

**Owning decision / RFC:** [D-065](docs/DECISIONS.md) ·
[RFC-0060](docs/rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) (extends D-064).
**Baseline tip:** Published `v0.36.0`.
**Tracking:** [#93](https://github.com/eddiethedean/hedron/issues/93) (closed).
**High-severity remediations:** [#230](https://github.com/eddiethedean/hedron/issues/230)–[#237](https://github.com/eddiethedean/hedron/issues/237) closed at cut; follow-on [#244](https://github.com/eddiethedean/hedron/issues/244) closed (element-markup `style=` / `vbscript:` / `data:`).
**Version policy at cut:** Alpha `hedron-elements` **`0.39.0`** (pin `>=0.39.0,<0.40`).

| ID | Disposition | Notes |
|---|---|---|
| `FORM-037` | **Verified** | Native/HTMX form parity across reference fields and hosts |
| `VALIDITY-037` | **Verified** | ElementInternals, fallback, CSRF, server 422 errors |
| `PRIMITIVE-037` | **Verified** | Disclosure/dialog catalog, keyboard/focus, native-first |
| `ACTIONSTATE-037` | **Verified** | Shared `InteractionState` concurrency/cancel/retry/job |
| `INTERACT-037` | **Verified** | Gesture/overlay catalog, top-layer, cleanup |
| `HTMX-037` | **Verified** | Swap/422/history/duplicate/slow/cancel; markup SafeUrl |
| `AT-037` | **Verified** | Keyboard/a11y packet dispositioned |
| `REGRESS-037` / `PKG-037` | **Verified** | Suites + `verify_pkg_37.py`; #230–#237 and #244 closed |

SSOT: [RELEASE_0_37](docs/acceptance/RELEASE_0_37.md) ·
[release-gate-0.37.toml](docs/acceptance/release-gate-0.37.toml) ·
[production-grade-inventory-037.toml](docs/acceptance/production-grade-inventory-037.toml).
Cut verify: `python scripts/verify_pkg_37.py` (no `--allow-planned`).

## Next capability phases

Human AT sessions (`SR-021` / `PARTICIPANT-021` / `ARTIFACT-021` / `REMEDIATE-021`) remain
**Planned** until compensated screen-reader evidence lands
([#86](https://github.com/eddiethedean/hedron/issues/86)). Phase **0.27** is **Published**
(`v0.27.0`; D-055). Phase **0.28** is **Published** (`v0.28.2`; D-056 / RFC-0059).
Phase **0.29** is **Published** (`v0.29.0`; D-057 / RFC-0062). Phase **0.30** is **Published**
(`v0.30.0`; D-058 / RFC-0063). Phase **0.31** is **Published** (`v0.31.0`; D-059 / RFC-0064 /
RFC-0061). Phase **0.32** is **Published** (`v0.32.0` / `hedron-mcp` `0.2.0`; D-060 /
RFC-0065). Phase **0.33** is **Published** (`v0.33.0` / `hedron-posit` `0.33.0` Beta; D-061 /
RFC-0066; [#167](https://github.com/eddiethedean/hedron/issues/167)); see
[implementation plan](docs/implementation/HEDRON_POSIT_033.md) and
[0.33 acceptance packet](docs/acceptance/RELEASE_0_33.md). Phase **0.34** is **Published**
(`v0.34.0` / `hedron-gradio` `0.2.0` Beta; D-062 / RFC-0067; [#90](https://github.com/eddiethedean/hedron/issues/90));
see [implementation plan](docs/implementation/HEDRON_GRADIO_034.md) and
[0.34 acceptance packet](docs/acceptance/RELEASE_0_34.md). Phase **0.35** is **Published** (`v0.35.0`; D-063 / [RFC-0068](docs/rfcs/RFC-0068-WHOLE-FLEET-CLOSURE.md); [#91](https://github.com/eddiethedean/hedron/issues/91)).
Phase **0.36** is **Published** as `v0.36.0` (D-064 / [RFC-0060](docs/rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md); [#92](https://github.com/eddiethedean/hedron/issues/92));
see [implementation plan](docs/implementation/HEDRON_ELEMENTS_036.md) and
[0.36 acceptance packet](docs/acceptance/RELEASE_0_36.md). Phase **0.37** is **Published** as
`v0.37.0` (D-065 / RFC-0060; [#93](https://github.com/eddiethedean/hedron/issues/93) closed;
high-severity remediations
[#230](https://github.com/eddiethedean/hedron/issues/230)–[#237](https://github.com/eddiethedean/hedron/issues/237)
and follow-on [#244](https://github.com/eddiethedean/hedron/issues/244) closed;
see [implementation plan](docs/implementation/HEDRON_ELEMENTS_037.md) and
[0.37 acceptance packet](docs/acceptance/RELEASE_0_37.md)). Phase **0.38** high-fidelity charts is
**Published** as `v0.38.0` / `hedron-charts` `0.2.0` (D-066 /
[RFC-0069](docs/rfcs/RFC-0069-HIGH-FIDELITY-CHARTS.md); `release-gate-0.38.toml` Verified;
[#251](https://github.com/eddiethedean/hedron/issues/251); see
[implementation plan](docs/implementation/HEDRON_CHARTS_038.md),
[grammar catalogs](docs/implementation/CHART_SPEC.md), and
[0.38 acceptance packet](docs/acceptance/RELEASE_0_38.md)). It ships an ABI-conforming
`hedron-chart`, typed `ChartSpec` / `ChartPlan`, modular first-party rendering, visual/a11y/performance/
export/security evidence, and independent `hedron-charts` `0.2.0`. Phase **0.39** rich data / OptimisticMutation is **Published** as `v0.39.0` (D-067 /
[RFC-0060](docs/rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md); `release-gate-0.39.toml` Verified;
[#94](https://github.com/eddiethedean/hedron/issues/94) closed; see
[implementation plan](docs/implementation/HEDRON_RICH_ELEMENTS_039.md),
[rich-surface catalogs](docs/implementation/RICH_SURFACE_039.md), and
[0.39 acceptance packet](docs/acceptance/RELEASE_0_39.md)). It ships ABI-conforming
`hedron-data-editor`, typed `OptimisticMutation` on bounded collection edits, Published
`hedron-chart` cross-filter composition (`compose_chartlink_039`), owned Experimental rich-surface
exceptions, worker/stream bounds, and the locked 27-issue remediation packet. Phase **0.40**
Web Component authoring and interoperability is **Published** as `v0.40.0` (D-068 /
[RFC-0060](docs/rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md); `release-gate-0.40.toml` Verified;
[#95](https://github.com/eddiethedean/hedron/issues/95) closed; see
[implementation plan](docs/implementation/HEDRON_AUTHORING_040.md),
[React migration matrix](docs/implementation/REACT_MIGRATION_MATRIX_040.md), and
[0.40 acceptance packet](docs/acceptance/RELEASE_0_40.md)). It ships the public author kit and
`hedron new element`, plugin/HDJ/Explorer/theme metadata parity, `ReactMigrationMatrix` with an
Experimental island docs/reference, optional `@hedron/elements` modules/types mirror, and the
locked 6-issue remediation packet. Phase **0.41** browser composition, draft transfer, and
navigation is **Published** as `v0.41.0` (D-069 /
[RFC-0060](docs/rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md); `release-gate-0.41.toml` Verified;
[#96](https://github.com/eddiethedean/hedron/issues/96); see
[implementation plan](docs/implementation/HEDRON_COMPOSITION_041.md) and
[0.41 acceptance packet](docs/acceptance/RELEASE_0_41.md)). Phase **0.42** production-grade Web
Component platform is **Published** as `v0.42.0` (D-070 / RFC-0060;
`release-gate-0.42.toml` Verified; [#97](https://github.com/eddiethedean/hedron/issues/97); see
[implementation plan](docs/implementation/HEDRON_ELEMENTS_042.md) and
[0.42 acceptance packet](docs/acceptance/RELEASE_0_42.md)). Phase **0.43** refreshable views,
commands, and typed updates is **Published** as `v0.43.0` (D-071 /
[RFC-0070](docs/rfcs/RFC-0070-REFRESHABLE-VIEWS.md); `release-gate-0.43.toml` Verified;
[#311](https://github.com/eddiethedean/hedron/issues/311); see
[implementation requirements](docs/implementation/INTERACTION_HANDLES_043.md) and
[acceptance packet](docs/acceptance/RELEASE_0_43.md)).
Phase **0.44** type-driven authoring is **Published** as `v0.44.0` (D-072 /
[RFC-0071](docs/rfcs/RFC-0071-TYPE-DRIVEN-AUTHORING.md); D-076; `release-gate-0.44.toml`
Verified; [#318](https://github.com/eddiethedean/hedron/issues/318); see
[implementation requirements](docs/implementation/TYPE_DRIVEN_AUTHORING_044.md) and
[acceptance packet](docs/acceptance/RELEASE_0_44.md)).
Phase **0.45** typed interaction ecosystem convergence is **Published** as `v0.45.0` (in-tree cut,
tag and PyPI published; D-074 / D-077 / [RFC-0072](docs/rfcs/RFC-0072-TYPED-INTERACTION-ECOSYSTEM.md);
`release-gate-0.45.toml` Verified; [#328](https://github.com/eddiethedean/hedron/issues/328); see
[implementation requirements](docs/implementation/TYPED_INTERACTION_ECOSYSTEM_045.md) and
[acceptance packet](docs/acceptance/RELEASE_0_45.md)).
Phase **0.46** package-native typed workflows is **Published** as `v0.46.0` (D-075 / D-079 / [RFC-0073](docs/rfcs/RFC-0073-PACKAGE-NATIVE-WORKFLOWS.md);
`release-gate-0.46.toml` Verified; [#334](https://github.com/eddiethedean/hedron/issues/334); see
[implementation requirements](docs/implementation/PACKAGE_NATIVE_WORKFLOWS_046.md) and
[acceptance packet](docs/acceptance/RELEASE_0_46.md)).
Phase **0.47** first-class maps is **Published** as in-tree `v0.47.0` (tag and PyPI published;
D-078 / D-082 / RFC-0074; `release-gate-0.47.toml` Verified;
tracking [#350](https://github.com/eddiethedean/hedron/issues/350); see
[implementation requirements](docs/implementation/HEDRON_MAPS_047.md) and
[acceptance packet](docs/acceptance/RELEASE_0_47.md)).
Phase **0.48** first-class HTMX extension integration is **Published** as in-tree `v0.48.0`
(tag and PyPI published; D-080 / D-083 / RFC-0075; `release-gate-0.48.toml` Verified except
`MORPH-048` **Deferred**; tracking [#373](https://github.com/eddiethedean/hedron/issues/373); see
[implementation requirements](docs/implementation/HTMX_EXTENSION_INTEGRATION_048.md) and
[acceptance packet](docs/acceptance/RELEASE_0_48.md)).
Phase **0.49** FastAPI/Pydantic convergence is **Published** as `v0.49.1`
(D-081 / D-084 / RFC-0076; `release-gate-0.49.toml` Verified;
tracking [#380](https://github.com/eddiethedean/hedron/issues/380); see
[implementation requirements](docs/implementation/FASTAPI_PYDANTIC_CONVERGENCE_049.md) and
[acceptance packet](docs/acceptance/RELEASE_0_49.md)).
Phase **0.50** Explorer architecture is **in-tree** as `v0.50.3`
(D-085 / D-086 / RFC-0077; `release-gate-0.50.toml` Verified; train tip **`v0.50.3`**;
PyPI latest **`v0.50.1`**; Git tag for 0.50.3 deferred).
tracking [#501](https://github.com/eddiethedean/hedron/issues/501);
related [#496](https://github.com/eddiethedean/hedron/issues/496)–[#500](https://github.com/eddiethedean/hedron/issues/500) /
[#502](https://github.com/eddiethedean/hedron/issues/502) /
[#503](https://github.com/eddiethedean/hedron/issues/503) closed on this cut;
see [implementation requirements](docs/implementation/EXPLORER_050.md) and
[acceptance packet](docs/acceptance/RELEASE_0_50.md).
These phases require Verified evidence before any package maturity label changes. They do not
schedule `1.0`, promote every experimental subfeature, or expand Supported live transports. Close
each tracking issue only when its owning release-gate rows are Verified **and** publish assets exist.
[#373](https://github.com/eddiethedean/hedron/issues/373) and
[#350](https://github.com/eddiethedean/hedron/issues/350) remain open for 0.48 / 0.47 publish assets.
Phase **0.51** curated extras shipped as `v0.52.0` on PyPI (D-087 / D-088 / RFC-0078;
[#507](https://github.com/eddiethedean/hedron/issues/507)); companion
[#504](https://github.com/eddiethedean/hedron/issues/504)–[#506](https://github.com/eddiethedean/hedron/issues/506)
closed as flagship authoring.
