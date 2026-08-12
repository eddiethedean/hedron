# Upgrade fixtures plan (0.30 dual-package cut)

**Baseline:** Published **`v0.30.0`** (Hedron) and public **`fastapi-workbench` `0.3.4`**.
**Owning gates:** `COMPAT-030`, `DEPENDENCY-030`, `PKG-030`
**RFC:** [RFC-0063](../rfcs/RFC-0063-FASTAPI-WORKBENCH-EXTRACTION.md).

## Capture set

### Public `fastapi-workbench` 0.3.4 → monorepo `1.0.0`

1. **CLI parity** (`fwb_cli_034.json`) — `run`, `check`, `--dry-run`, and `--factory`
   entry points accept the same module targets and emit redacted JSON/text diagnostics.
2. **Env aliases** (`fwb_env_034.json`) — `WORKBENCH_FORCE`, `BASE_PATH`,
   `PUBLIC_BASE_URL`, `HOST`, `PORT`, and related 0.3.4 aliases warn via `FWB-0008`
   while namespaced `FASTAPI_WORKBENCH_*` wins.
3. **Path parity** (`fwb_path_034.json`) — session/project/proxy mount normalization
   bytes match the locked 0.3.4 corpus (`path_parity_034.json` lineage).

### `hedron-workbench` 0.29 → 0.30

1. **Non-Workbench parity** (`workbench_off.json`) — `mode=off` PAGE/FRAGMENT HTML and
   CSRF cookie Path match unadapted Hedron on 0.30.0.
2. **Mount-once URLs** (`workbench_mount.json`) — prefixed local redirect, asset href,
   and cookie Path under a session-shaped mount.
3. **Delegation records** (`workbench_delegate.json`) — `hedron-workbench` resolves and
   serves through `fastapi-workbench` with `HEDRON_ROOT_PATH` export before import.
4. **Dependency floor** (`workbench_dep.json`) — mixed-version refusal, uninstall rollback,
   and `fastapi-workbench>=1.0.0,<2.0` floor/ceiling enforcement.

## Location

- Plan SSOT: this file
- Goldens: `tests/upgrade/goldens_0_29_0/` and `tests/upgrade/goldens_fwb_034/`
- Tests: `tests/upgrade/test_0_29_0_to_0_30_workbench.py`,
  `tests/upgrade/test_fwb_034_to_1_0.py`

## Pass criteria

Silent drift in golden bytes or structural keys fails CI. Intentional breaks require an
explicit changelog note and golden update in the same PR. Uninstalling either package
restores ordinary Uvicorn launch (`uvicorn module:app`).
