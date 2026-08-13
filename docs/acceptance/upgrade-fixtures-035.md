# Upgrade fixtures — phase 0.35 (whole-fleet closure)

Baseline: Published **`v0.34.0`**. Cut: **`v0.35.0`**.

## Goldens / suites

- `tests/upgrade/test_0_34_to_0_35_fleet.py` — inventory baseline, dispositions, PRESENT-034 honesty
- `tests/ops/test_solver_035.py` — Supported extras declarations, Gradio Beta pin, mixed satellite pins
- `tests/ops/test_fleet_035.py` — workspace coverage

## Pin migration (history table)

| From tip | Historical pin | At 0.35 cut |
|---|---|---|
| `v0.25.x` | `hedron>=0.25.0,<0.26` | `hedron>=0.35.0,<0.36` |
| `v0.30.0` | `hedron>=0.30.0,<0.31` | `hedron>=0.35.0,<0.36` |
| `v0.32.0` | `hedron>=0.32.0,<0.33` | `hedron>=0.35.0,<0.36` |
| `v0.33.0` | `hedron>=0.33.0,<0.34` | `hedron>=0.35.0,<0.36` |
| `v0.34.0` | `hedron>=0.34.0,<0.35` | `hedron>=0.35.0,<0.36` |

Independent satellites stay on their own lines (`hedron-mcp` / `hedron-gradio` `>=0.2.0,<0.3`,
`hedron-charts` / tooling `0.1.x`, `fastapi-workbench` `>=1,<2`).

## Offline / mixed-version

- Offline wheelhouse rehearsal: [`fleet-supply-035/OFFLINE_INSTALL.md`](fleet-supply-035/OFFLINE_INSTALL.md)
- Mixed-version: train packages must not be mixed with older train floors; satellite majors remain distinct from the train pin (enforced in `test_solver_035.py`)
- Uninstall / absence of optional satellites must add no core cost (inventory `excluded` honesty)

## Behavior notes

- No package graduation behavior change beyond fleet disposition honesty
- PRESENT-034 gallery remains deferred/experimental — not silently Supported
- CI executes the **0.34 → 0.35** path; earlier tips are documented in the history table above
