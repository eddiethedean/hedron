# Upgrade fixtures plan (`CORE-026`)

**Baseline:** Published **`v0.25.2`**.
**Owning gate:** `CORE-026`.
**RFC:** [RFC-0057](../rfcs/RFC-0057-PRODUCTION-GRADE-CORE.md).

## Capture set

From the Supported facade (see [STABLE_FACADE.md](../api/STABLE_FACADE.md) and
[production-grade-inventory-026.toml](production-grade-inventory-026.toml)):

1. **Serialized identities** — component/model type identities and registry keys
   that must remain stable across the upgrade.
2. **Diagnostics snapshots** — sanitized diagnostic views used by Explorer /
   tooling (no secrets).
3. **Build / asset manifests** — production asset manifest shape and required
   keys for the FastAPI flagship path.
4. **HTMX interaction results** — representative `InteractionResult` / fragment
   swap payloads for CRUD form submit and poll status.

## Location

- Plan SSOT: this file
- Goldens + tests: `tests/upgrade/test_0_25_2_to_0_26_facade.py` and
  `tests/upgrade/goldens_0_25_2/`

## Pass criteria

Silent drift in golden bytes or structural keys fails CI. Intentional breaks
require an explicit changelog note and golden update in the same PR.
