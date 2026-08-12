# Upgrade fixtures plan (0.29 hedron-workbench)

**Baseline:** Published **`v0.28.2`**.
**Owning gates:** `COMPAT-029`, `URL-029`, `PKG-029`
**RFC:** [RFC-0062](../rfcs/RFC-0062-POSIT-WORKBENCH-ADAPTER.md).

## Capture set

1. **Non-Workbench parity** (`workbench_off.json`) — `mode=off` PAGE/FRAGMENT
   HTML and CSRF cookie Path match unadapted Hedron on 0.28.2.
2. **Mount-once URLs** (`workbench_mount.json`) — prefixed local redirect,
   asset href, and cookie Path under a session-shaped mount.
3. **Resolver records** (`workbench_resolve.json`) — redacted text/JSON
   resolution for explicit, namespaced, alias, and discovered inputs.

## Location

- Plan SSOT: this file
- Goldens: `tests/upgrade/goldens_0_28_2/`
- Tests: `tests/upgrade/test_0_28_2_to_0_29_workbench.py`

## Pass criteria

Silent drift in golden bytes or structural keys fails CI. Intentional breaks
require an explicit changelog note and golden update in the same PR.
Uninstalling `hedron-workbench` restores 0.28 launch (`uvicorn module:app`).
