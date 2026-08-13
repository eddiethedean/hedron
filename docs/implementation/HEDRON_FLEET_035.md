# Phase 0.35 implementation plan: whole-fleet production-grade closure

This plan turns [RFC-0068](../rfcs/RFC-0068-WHOLE-FLEET-CLOSURE.md) into reviewable work. It is not
authorization to cut until RFC-0068 is Accepted and every gate row is Verified.

## Outcome

Publish `v0.35.0` with a machine-readable fleet inventory covering every publishable distribution,
solver/compose/docs/supply evidence in agreement, and zero unowned Alpha or ambiguous dispositions.
This phase is **not** Hedron `1.0`.

The phase is complete only when every row in
[`release-gate-0.35.toml`](../acceptance/release-gate-0.35.toml) is Verified.

## Decisions already locked

| Topic | Decision |
|---|---|
| Primary scope | Fleet audit / disposition closure (D-063) |
| Gate IDs | `FLEET-035` … `PKG-035` only — no `PRESENT-035` |
| PRESENT-034 | Folds into `FLEET-035` + `DOCS-035` |
| Baseline | Published `v0.34.0` |
| Tracking | [#91](https://github.com/eddiethedean/hedron/issues/91) |
| Non-goals | Not `1.0`; no SLA/WCAG/VPAT; no `polling_only` reopen |

## Stage 0 — contract refine (no behavior change)

**Goal:** locked cut matrix, inventory, RFC draft, gate manifest (Planned).

Deliverables:

- Draft RFC-0068, D-063, this plan, `production-grade-inventory-035.toml`
- `release-gate-0.35.toml` with Planned rows
- `RELEASE_0_35.md` acceptance skeleton
- Tracking [#91](https://github.com/eddiethedean/hedron/issues/91) synced to 0.35 gates
- `security-review-035/BRIEF.md` stub

**Exit:** `python scripts/verify_pkg_35.py --allow-planned` green.

## Stage 1 — gate plumbing

Checker scripts under `scripts/check_*_035.py`, `_gate_035.py`, `verify_pkg_35.py`,
`check_release_gate.py` `0.35` mapping.

## Stage 2 — fleet inventory enforcement (`FLEET-035`)

- Require disposition on every inventory row
- Fail on unowned Alpha / missing evidence pointers
- Record PRESENT-034 status fields

## Stage 3 — solver matrices (`SOLVER-035`)

- Supported extras combinations, min/max dependencies, offline wheelhouse
- Upgrade from 0.25 and each graduation phase tip; rollback; mixed-version fail; uninstall

## Stage 4 — compose matrices (`COMPOSE-035`)

- Reference-app isolation per production-grade optional package
- Supported combinations with security, a11y/browser, performance, lifecycle, diagnostics budgets

## Stage 5 — docs and supply (`DOCS-035`, `SUPPLY-035`)

- Reconcile whats-ready, package READMEs, release notes, presentation status with inventory
- License inventory, SBOM, provenance, vulnerability disposition, retention, rollback

## Stage 6 — cut

- Accept RFC-0068; flip gates to Verified; `verify_pkg_35.py` without `--allow-planned`
- Bump train to `0.35.0`; publish; close #91

## Cut verification

At `v0.35.0` cut:

```bash
python scripts/verify_pkg_35.py
python scripts/check_release_gate.py 0.35.0 --execute-verified
```

During packet refine:

```bash
python scripts/verify_pkg_35.py --allow-planned
```
