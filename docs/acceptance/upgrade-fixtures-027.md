# Upgrade fixtures plan (0.27 satellite graduation)

**Baseline:** Published **`v0.26.0`**.
**Owning gates:** `DATA-027`, `FLASK-027`, `DJANGO-027`, `HDJ-027`, `EXTRAS-027`
(fixtures feed those gates; inventory agreement closes under `PKG-027` /
`check_contract_027.py`).
**RFC:** [RFC-0058](../rfcs/RFC-0058-PRODUCTION-GRADE-SATELLITES.md).

## Capture set

From the Supported inventories (see
[production-grade-inventory-027.toml](production-grade-inventory-027.toml)):

1. **Data contracts** (`data_contracts.json`) — DataTable/DataEditor identities,
   saved-view required keys, and documented spreadsheet import/export paths.
2. **Adapter interaction results** (`adapter_interaction.json`) — PAGE/FRAGMENT /
   CSRF/header outcomes for Flask and Django Supported paths with `polling_only`
   and forbidden live parity.
3. **HDJ manifests** (`hdj_manifest.json`) — `.hdj` v1 feature prologue keys,
   sample templates, and asset/manifest keys required for host integration.
4. **Extras registry** (`extras_registry.json`) — curated default-extra discovery
   keys; assert experimental-ui symbols remain absent from the default registry.

## Location

- Plan SSOT: this file
- Goldens: `tests/upgrade/goldens_0_26_0/`
- Tests: `tests/upgrade/test_0_26_0_to_0_27_satellites.py`

## Pass criteria

Silent drift in golden bytes or structural keys fails CI. Intentional breaks
require an explicit changelog note and golden update in the same PR.
