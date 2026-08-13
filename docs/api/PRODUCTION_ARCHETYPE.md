---
status: published
---

# Production archetype and landmine quarantine (0.25)

!!! tip "Verified on the 0.25 train"

    Canonical production archetype packet (`ARCHETYPE-025` … `PKG-025`) is **Verified**.
    Pin `hedron>=0.34.0,<0.35`.

    **Ship today:** [Ship a Hedron app](../guides/ship.md) ·
    [What’s ready](../guides/whats-ready.md) ·
    [`examples/reference-app`](https://github.com/eddiethedean/hedron/tree/main/examples/reference-app).

**Program context:** [Production-quality maturity](../guides/production-quality.md) ·
[RFC-0056](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0056-PRODUCTION-QUALITY.md)
· maintainer decision D-053 (GitHub
[DECISIONS](https://github.com/eddiethedean/hedron/blob/main/docs/DECISIONS.md)).

**Owning gates (maintainer evidence IDs):** `ARCHETYPE-025`, `BUDGET-025`, `EXTRAS-025`,
`CHARTS-025`, `SUPPLY-025`, `REGRESS-025`, `PKG-025` (all **Verified**).

Machine twin (extras quarantine):
[extras-quarantine-025.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/extras-quarantine-025.toml)
(GitHub-only). Budgets:
[PERFORMANCE_BUDGETS.md](../PERFORMANCE_BUDGETS.md) (§0.25 workloads).

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

Checker: `python scripts/check_archetype_025.py`.

## Load budgets (`BUDGET-025`)

Three named workloads (see [PERFORMANCE_BUDGETS.md](../PERFORMANCE_BUDGETS.md)):

| ID | Workload |
|---|---|
| `W-025-FRAGMENT` | Fragment latency under representative HTMX swap load |
| `W-025-JOB-POLL` | Job status poll fanout |
| `W-025-DATAEDITOR` | DataEditor row-model smoke |

Evidence may be **CI** or an **immutable artifact**. Checker:
`python scripts/check_budget_025.py`.

## Extras quarantine XOR (`EXTRAS-025`)

Landmines in scope: **CodeEditor** host stub, **TerminalView**, **joystick** + **device**
bridges. Cut disposition: **`quarantine`**.

| Value | Cut meaning |
|---|---|
| `undecided` | Refine / pre-cut only (`--allow-undecided`) |
| `quarantine` | Move landmines behind a clearly named experimental extra so `hedron[extras]` does not imply product UI |
| `finish_supported` | Reach Supported with evidence for those surfaces |

**Chosen path:** `quarantine` via **`hedron[experimental-ui]`**. Quarantine is
**registration/discovery gated**, not import-gated: landmines remain importable from
`hedron_extras.experimental` (and related workbench/specialty modules), but **default plugin
registration** skips `*_experimental` entry points unless you set `HEDRON_EXPERIMENTAL_UI=1`
or explicitly enable `hedron_extras_experimental`. The named extra is an honesty/pin signal
(install footprint for adopters who opt in); it does not enforce import blocking. Curated
**`hedron[extras]`** remains the product toolkit and does **not** register or re-export those
surfaces.

Do not half-verify both. Normative criteria:
[ROADMAP §0.25](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md)
(GitHub-only). Checker: `python scripts/check_extras_025.py`.
Machine twin: [extras-quarantine-025.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/extras-quarantine-025.toml).

## Charts graduation path (`CHARTS-025`)

**Matplotlib** is the conservative **Supported** default charts path.
**Plotly** and **Altair** remain **experimental** until pins + CSP + a11y evidence match the
DataTable bar.

### Graduation checklist (Plotly / Altair)

Full graduation is **not** required for the 0.25 cut. The checklist must remain visible:

```text
pinned dependency versions
CSP-compatible asset policy
accessibility evidence matching DataTable bar
```

Checker: `python scripts/check_charts_025.py`.

## Supply process (`SUPPLY-025`)

The maintainer
[RELEASE](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md)
runbook requires **SBOM** and **evidence-bundle** attach on train tags.
Regenerate instructions remain in the [Evidence pack](../guides/evidence-pack.md)
(`scripts/build_evidence_bundle.py`, `scripts/generate_sbom.py`).

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
