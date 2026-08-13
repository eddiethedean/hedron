# Hedron `v0.35` whole-fleet production-grade closure acceptance

**Status:** **Published** as `v0.35.0` (2026-08-13).

Phase 0.35 is the final audit of the 0.26+ package-graduation program: every publishable
distribution has an owned Supported (or tooling-grade Supported) scope **or** an explicit
terminal disposition. Baseline: Published `v0.34.0`. Evidence is indexed by
[`release-gate-0.35.toml`](release-gate-0.35.toml). **Zero Deferred:** every 0.35-owned gate
is Verified at cut.

Owning decision: [D-063](../DECISIONS.md). Design:
[RFC-0068](../rfcs/RFC-0068-WHOLE-FLEET-CLOSURE.md) (**Accepted** 2026-08-13).
Implementation: [HEDRON_FLEET_035](../implementation/HEDRON_FLEET_035.md). Tracking:
[#91](https://github.com/eddiethedean/hedron/issues/91).

## Release contract

- Coordinated `hedron` / core packages `0.35.0`.
- Independent satellites (`hedron-mcp`, `hedron-gradio`, `hedron-charts`, `hedron-native`,
  `fastapi-workbench`) keep their own version lines.
- Fleet inventory [`production-grade-inventory-035.toml`](production-grade-inventory-035.toml)
  covers every `packages/*` Python distribution plus published Node/Java runtimes.
- Deferred **PRESENT-034** folds into **`FLEET-035` + `DOCS-035`** (no `PRESENT-035` gate).
- Python 3.11–3.14 remain the supported interpreter matrix.
- This phase is **not** Hedron `1.0`.

## Entry criteria

- [x] `v0.34.0` published; D-062 Accepted; #90 closed
- [x] Gradio / Posit / MCP / tooling graduation packets published through 0.34
- [x] RFC-0068 Accepted and implementation plan present
- [x] Tracking issue #91 bound to phase 0.35 gate IDs
- [x] Planned release-gate rows and checker ownership reviewed

## Exact cut matrix

| Lane | Topology | Required evidence |
|---|---|---|
| Fleet inventory | Every publishable package + runtime | `tests/ops/test_fleet_035.py` / `check_fleet_035.py` |
| Solver clean | Flagship extras + satellites | `tests/ops/test_solver_035.py` / `upgrade-fixtures-035.md` |
| Upgrade path | From `v0.25` history table + `v0.34` executable | `tests/upgrade/test_0_34_to_0_35_fleet.py` |
| Compose isolation | Reference app + each PG optional package | `tests/ops/test_compose_035.py` |
| Compose combinations | data + charts + jinja | `tests/ops/test_compose_035.py` |
| Docs / presentation | whats-ready + PRESENT-034 honesty | `check_docs_035.py` |
| Supply | PyPI/npm/Maven artifacts | `fleet-supply-035/` + `check_supply_035.py` |
| Mixed-version fail | Unsupported mixed satellite pins | `test_solver_035.py` |

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

## Cut verification

```bash
python scripts/verify_pkg_35.py
python scripts/check_release_gate.py 0.35.0 --execute-verified
```

## Exit

- [x] Exact cut matrix has no `TBD` on Supported lanes
- [x] RFC-0068 Accepted and implementation matches it
- [x] Every 0.35-owned release-gate row Verified with zero Deferred
- [x] Fleet inventory published with `v0.35.0`; zero unowned Alpha rows
- [x] Close #91 after release assets are published on GitHub/PyPI
