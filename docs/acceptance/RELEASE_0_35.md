# Hedron `v0.35` whole-fleet production-grade closure acceptance

**Status:** **Planned** (packet refine; target `v0.35.0`).

Phase 0.35 is the final audit of the 0.26+ package-graduation program: every publishable
distribution has an owned Supported (or tooling-grade Supported) scope **or** an explicit
terminal disposition. Baseline: Published `v0.34.0`. Evidence is indexed by
[`release-gate-0.35.toml`](release-gate-0.35.toml). **Zero Deferred:** every 0.35-owned gate
must be Verified at cut.

Owning decision: [D-063](../DECISIONS.md). Design:
[RFC-0068](../rfcs/RFC-0068-WHOLE-FLEET-CLOSURE.md) (Draft at refine; Accepted at cut).
Implementation: [HEDRON_FLEET_035](../implementation/HEDRON_FLEET_035.md). Tracking:
[#91](https://github.com/eddiethedean/hedron/issues/91).

## Release contract

- Living tip remains `v0.34.0` during refine; cut coordinates `hedron` / core packages to `0.35.0`.
- Independent satellites (`hedron-mcp`, `hedron-gradio`, `hedron-charts`, `hedron-native`,
  `fastapi-workbench`) keep their own version lines unless a disposition requires otherwise.
- Fleet inventory [`production-grade-inventory-035.toml`](production-grade-inventory-035.toml)
  covers every `packages/*` Python distribution plus published Node/Java runtimes.
- Deferred **PRESENT-034** folds into **`FLEET-035` + `DOCS-035`** (no `PRESENT-035` gate).
- Python 3.11–3.14 remain the supported interpreter matrix.
- This phase is **not** Hedron `1.0`.

## Entry criteria

- [x] `v0.34.0` published; D-062 Accepted; #90 closed
- [x] Gradio / Posit / MCP / tooling graduation packets published through 0.34
- [x] Draft RFC-0068 and implementation plan present
- [x] Tracking issue #91 bound to phase 0.35 gate IDs
- [x] Planned release-gate rows and checker ownership reviewed

## Exact cut matrix

| Lane | Topology | Required evidence |
|---|---|---|
| Fleet inventory | Every publishable package + runtime | `FLEET-035` disposition coverage |
| Solver clean | Flagship extras + satellites from clean resolver | `SOLVER-035` min/max, offline, upgrade, rollback |
| Upgrade path | From `v0.25` and each graduation phase tip | `SOLVER-035` upgrade fixtures |
| Compose isolation | Reference app + each production-grade optional package | `COMPOSE-035` security/a11y/browser/perf |
| Compose combinations | Documented Supported extra combinations | `COMPOSE-035` combination matrix |
| Docs / presentation | whats-ready, package READMEs, PRESENT-034 status | `DOCS-035` |
| Supply | PyPI/npm/Maven artifacts | `SUPPLY-035` SBOM/provenance/license |
| Mixed-version fail | Unsupported mixed satellite pins | `SOLVER-035` fail-closed |

## Locked evidence gates

| Gate | Owner | Verified means |
|---|---|---|
| `FLEET-035` | `hedron` | Inventory covers every package/tool; no Alpha/ambiguous row lacks owner + disposition |
| `SOLVER-035` | `hedron` | Extras, offline, upgrades, rollback, mixed-version fail, uninstall |
| `COMPOSE-035` | `hedron` | Reference-app isolation and combinations pass budgets |
| `DOCS-035` | `hedron` | Docs/metadata/examples/presentation status agree with inventory |
| `SUPPLY-035` | `hedron` | License, SBOM, provenance, vulnerability, retention, rollback |
| `REGRESS-035` | `hedron` | Full cross-language/package suite |
| `PKG-035` | `hedron` | Whole-fleet release rehearsal; all gate commands pass with zero Deferred |

## Required adversarial / honesty cases

- Unowned or ambiguous Alpha package labels vs docs/PyPI disagreement
- Experimental live transports or experimental-ui treated as Supported by solver defaults
- Missing SBOM/provenance for a published channel
- PRESENT-034 status omitted from fleet/docs reconcile
- Abandoned packages kept solely to enlarge the published fleet

## Cut verification

At `v0.35.0` cut (every 0.35-owned row Verified):

```bash
python scripts/verify_pkg_35.py
python scripts/check_release_gate.py 0.35.0 --execute-verified
```

During packet refine:

```bash
python scripts/verify_pkg_35.py --allow-planned
python scripts/check_release_gate.py 0.34.0 \
  --evidence-manifest docs/acceptance/release-gate-0.35.toml \
  --allow-planned
```

(Refine uses living tip `0.34.0` for package metadata; evidence manifest is the 0.35 Planned gate file.)

## Exit

- [ ] Exact cut matrix has no `TBD` on Supported lanes
- [ ] RFC-0068 Accepted and implementation matches it
- [ ] Every 0.35-owned release-gate row Verified with zero Deferred
- [ ] Fleet inventory published with `v0.35.0`; zero unowned Alpha rows
- [ ] Close #91 after release assets are published on GitHub/PyPI
