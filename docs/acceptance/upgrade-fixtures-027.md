# Upgrade fixtures plan (0.27 satellite graduation)

**Baseline:** Published **`v0.26.0`**.
**Owning gates:** `DATA-027`, `FLASK-027`, `DJANGO-027`, `HDJ-027`, `EXTRAS-027`
(fixtures feed those gates; inventory agreement closes under `PKG-027`).
**RFC:** [RFC-0058](../rfcs/RFC-0058-PRODUCTION-GRADE-SATELLITES.md).

## Capture set

From the Supported inventories (see
[production-grade-inventory-027.toml](production-grade-inventory-027.toml)):

1. **Data contracts** — DataTable/DataEditor identities, saved-view serialization,
   and documented spreadsheet import/export shapes that must remain stable.
2. **Adapter interaction results** — representative PAGE/FRAGMENT /
   `InteractionResult` / CSRF/header outcomes for Flask and Django Supported
   paths (aligned with FastAPI parity cases).
3. **HDJ manifests** — `.hdj` v1 feature prologue, component-binding metadata,
   and asset/manifest keys required for host integration.
4. **Extras registry** — curated default-extra discovery keys; assert
   experimental-ui symbols remain absent from the default registry.

## Location

- Plan SSOT: this file
- Goldens + tests: `tests/upgrade/` (planned modules such as
  `test_0_26_0_to_0_27_satellites.py` and `goldens_0_26_0/`)

## Pass criteria

Silent drift in golden bytes or structural keys fails CI. Intentional breaks
require an explicit changelog note and golden update in the same PR.
