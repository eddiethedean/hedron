---
status: draft
---

# Production archetype and landmine quarantine (0.25)

!!! note "Packet refine complete — cut still Planned"

    Phase **0.25** packet refine has locked Verified criteria and distinct gate commands.
    Status remains **Planned** until every 0.25-owned gate row is Verified. Do not market the
    archetype as Supported until `ARCHETYPE-025` flips. Living published train remains
    **0.24** — pin `hedron>=0.24.0,<0.25`.

**Owning gates:** `ARCHETYPE-025`, `BUDGET-025`, `EXTRAS-025`, `CHARTS-025`, `SUPPLY-025`,
`REGRESS-025`, `PKG-025`. Decision: **D-053** /
[RFC-0056](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0056-PRODUCTION-QUALITY.md).
Machine twin (extras XOR):
[`extras-quarantine-025.toml`](../acceptance/extras-quarantine-025.toml).
Budgets: [PERFORMANCE_BUDGETS.md](../PERFORMANCE_BUDGETS.md) (§0.25 workloads).

## Canonical archetype (`ARCHETYPE-025`)

Canonical path: **`examples/reference-app`** (compose / Caddy / Redis / multi-worker).
A sibling recipe is **not** the cut target.

### Ingredient checklist (machine-checked)

Cut documentation must cover each ingredient:

```text
reverse-proxy subpath
Redis job/cache
sticky sessions or external session store
HEDRON_ENV=production
CSP
Explorer off
multi-worker
```

Public guides that must link the archetype at cut:

- [Production-quality maturity](../guides/production-quality.md)
- [Production readiness](../guides/production-readiness.md)

Checker: `python scripts/check_archetype_025.py` (refine: `--allow-draft`).

## Load budgets (`BUDGET-025`)

Three named workloads (see [PERFORMANCE_BUDGETS.md](../PERFORMANCE_BUDGETS.md)):

| ID | Workload |
|---|---|
| `W-025-FRAGMENT` | Fragment latency under representative HTMX swap load |
| `W-025-JOB-POLL` | Job status poll fanout |
| `W-025-DATAEDITOR` | DataEditor row-model smoke |

Evidence may be **CI** or an **immutable artifact**. Checker:
`python scripts/check_budget_025.py` (refine: `--allow-planned`).

## Extras quarantine XOR (`EXTRAS-025`)

Landmines in scope: **CodeEditor** host stub, **TerminalView**, **joystick** + **device**
bridges. Cut chooses exactly one path:

| Value | Cut meaning |
|---|---|
| `undecided` | Refine / pre-cut only (`--allow-undecided`) |
| `quarantine` | Move landmines behind a clearly named experimental extra so `hedron[extras]` does not imply product UI |
| `finish_supported` | Reach Supported with evidence for those surfaces |

Do not half-verify both. Normative criteria: [ROADMAP §0.25](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).
Checker: `python scripts/check_extras_025.py`.

## Charts graduation path (`CHARTS-025`)

**Matplotlib** is the conservative **Supported** default charts path.
**Plotly** and **Altair** remain **experimental** until pins + CSP + a11y evidence match the
DataTable bar.

### Graduation checklist (Plotly / Altair)

Full graduation is **not** required for 0.25 cut. The checklist must remain visible:

```text
pinned dependency versions
CSP-compatible asset policy
accessibility evidence matching DataTable bar
```

Checker: `python scripts/check_charts_025.py`.

## Supply process (`SUPPLY-025`)

[RELEASE.md](../RELEASE.md) requires **SBOM** and **evidence-bundle** attach on train tags.
Regenerate instructions remain in the Evidence pack (`scripts/build_evidence_bundle.py`,
`scripts/generate_sbom.py`).

Checker: `python scripts/check_supply_025.py`.

## Locked gate commands

| Gate | Command |
|---|---|
| `ARCHETYPE-025` | `python scripts/check_archetype_025.py` |
| `BUDGET-025` | `python scripts/check_budget_025.py` |
| `EXTRAS-025` | `python scripts/check_extras_025.py` |
| `CHARTS-025` | `python scripts/check_charts_025.py` |
| `SUPPLY-025` | `python scripts/check_supply_025.py` |
| `REGRESS-025` | `bash scripts/ci_checks.sh test --python 3.12` |
| `PKG-025` | `python scripts/verify_pkg_25.py` |

Evidence index: [`release-gate-0.25.toml`](../acceptance/release-gate-0.25.toml).
