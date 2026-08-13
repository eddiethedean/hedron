# RFC-0068: Whole-fleet production-grade closure

**Status:** Accepted

**Target phase:** 0.35 (`v0.35.0` train)

**Stability:** `beta` (process / fleet-audit contract; not Hedron `1.0`)

**Evidence:** [RELEASE_0_35.md](../acceptance/RELEASE_0_35.md) ·
[release-gate-0.35.toml](../acceptance/release-gate-0.35.toml) ·
[production-grade-inventory-035.toml](../acceptance/production-grade-inventory-035.toml) ·
[security-review-035/BRIEF.md](../acceptance/security-review-035/BRIEF.md)

**Related:** D-063; [ROADMAP §0.35](../ROADMAP.md); tracking
[#91](https://github.com/eddiethedean/hedron/issues/91);
[DEFAULT_PRESENTATION_033_PLUS.md](../implementation/DEFAULT_PRESENTATION_033_PLUS.md)
(`PRESENT-034` Deferred → 0.35)

## Summary

Close the ROADMAP **0.26+ package-graduation program** with a whole-fleet audit so every
publishable Hedron distribution has either:

1. production-grade status for a **declared Supported scope**, or
2. an explicit **terminal disposition** outside ambiguous Alpha.

This RFC is the **fleet closure** contract: inventory schema, disposition enum, gate IDs,
solver/compose/docs/supply evidence rules, and cut requirements. It does **not** rename
`v0.35.0` to `1.0`, promote every experimental surface, or reopen live-transport decisions.

## Motivation

Phases 0.26–0.34 graduated core, satellites, charts/native, Workbench, tooling, MCP, Posit,
and Gradio under per-phase inventories. Remaining Alpha/ambiguous package labels
(`hedron-notebook`, `hedron-sample-kit`, `hedron-sim`, Node/Java runtimes), experimental
namespaces (live SSE/WS, `experimental-ui`), and deferred **PRESENT-034** presentation work
still need machine-checked owner + disposition rows. Adopters and maintainers need one fleet
inventory that agrees with the solver, docs, and supply evidence.

## Design

### Package dispositions

Every inventory row MUST set `disposition` to exactly one of:

| Disposition | Meaning |
|---|---|
| `production_grade` | Declared Supported (or tooling-grade Supported) scope with prior Verified evidence |
| `incubator` | Owned future evidence destination (named phase or issue); may remain Alpha |
| `fixture` | Retained internal test / sample fixture; not a production fleet claim |
| `eol` | Explicitly removed or end-of-life; must not remain an ambiguous published Alpha |

### Fleet inventory schema

Machine-checked in
[production-grade-inventory-035.toml](../acceptance/production-grade-inventory-035.toml):

- `baseline` — Published tip entering the phase (`v0.34.0`)
- `packages` — every publishable distribution name
- Per package: `owner`, `maturity`, `channel`, `pin`, `evidence`, `disposition`,
  `supported` / `experimental` / `excluded` surface lists (or pointer to prior inventory)

### Gate meanings

| Gate | Verified means |
|---|---|
| `FLEET-035` | Inventory covers every package/tool; no Alpha/ambiguous row lacks owner + disposition; PRESENT-034 status recorded |
| `SOLVER-035` | Supported extras, min/max deps, offline wheelhouse, upgrades, rollback, mixed-version fail, uninstall |
| `COMPOSE-035` | Reference-app isolation and supported combinations pass security/a11y/browser/perf/lifecycle/diagnostics budgets |
| `DOCS-035` | Metadata, readiness/compatibility, API inventories, examples, release notes, and default presentation docs agree with inventory |
| `SUPPLY-035` | License inventory, SBOM, provenance, vulnerability disposition, retention, rollback for published artifacts |
| `REGRESS-035` / `PKG-035` | Cross-language/package suite and whole-fleet release rehearsal; zero Deferred 0.35-owned rows |

### PRESENT-034 fold-in

Deferred default presentation gallery/geometry (`PRESENT-034`) is audited under
`FLEET-035` + `DOCS-035`. There is **no** `PRESENT-035` gate ID. Gallery implementation may
land in later stages of the 0.35 engineering plan; Stage 0 only locks the disposition.

### Alpha / experimental leftovers (must be dispositioned)

- Package maturity Alpha: `hedron-notebook`, `hedron-sample-kit`, `hedron-sim`,
  `hedron-runtime-node`, `hedron-runtime-java`
- Experimental capability surfaces: live SSE/WS/streaming/preload; Plotly/Altair;
  `experimental-ui` / CodeEditor host stub; MCP mutations; Gradio vendor extensions
- Human AT sessions (`#86`) remain Planned / not Supported — out of 0.35 production-grade
  claims unless separately dispositioned as incubator

### Threat / honesty model

- Ambiguous maturity labels that disagree with docs or PyPI
- Unowned Alpha packages kept only to enlarge the published fleet
- Solver combinations that install Experimental surfaces as if Supported
- Supply artifacts missing license/SBOM/provenance for a published channel

## Gate ownership

| Gate | Owner |
|---|---|
| `FLEET-035`, `SOLVER-035`, `COMPOSE-035`, `DOCS-035`, `SUPPLY-035`, `REGRESS-035`, `PKG-035` | `hedron` (train) |

## Non-goals

- Renaming `v0.35.0` to `1.0`, freezing experimental APIs, or claiming all features Supported
- Commercial SLA, hosted-service, legal compliance, WCAG conformance, VPAT/ACR, or certification
- Keeping abandoned packages published solely to make the fleet look larger
- Reopening the polling-only live-transport decision without a separately accepted evidence packet
- Inventing `PRESENT-035` as a separate gate ID

## Acceptance

- RFC-0068 Accepted before `v0.35.0` cut
- Every 0.35-owned gate Verified with zero Deferred
- Fleet inventory published with `v0.35.0`; zero unowned Alpha / ambiguous dispositions
- Living tip honesty: refine does not bump `docs/release.toml` until cut
