# Phase 0.53 upgrade and rollback fixtures

**Status:** Verified at Published in-tree `v0.53.0` (D-091 / D-092)<br>
**Planning baseline:** Published in-tree `v0.52.0`<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.52.0`<br>
**Target:** Hedron `v0.53.0`<br>
**Decision/RFC:** D-091 / D-092 / [RFC-0080](../rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md)<br>
**Tracking:** [#514](https://github.com/eddiethedean/hedron/issues/514)–[#521](https://github.com/eddiethedean/hedron/issues/521)

Baseline application DX seams remain read-only during Stage 0.
PKG-053 upgrade source is **0.52**, not 0.51. Do not start Stage 1 during
Stage 1. Living tip is `v0.53.0` (tag/PyPI deferred).

## 0.52.0 install fixtures

1. Page assets: `inject_page_assets`, `AssetRef`, `AssetMeta`, `register_asset`.
2. Diagnostics: `Diagnostic`, `DiagnosticSeverity`, `Suppression`,
   `diagnostics_to_sarif`, `hedron check`.
3. Routes: registry `RouteMeta`, `routes_json`, `hedron routes`, `CatalogEntry`.
4. Workflow: `JobBackend`, `JobHandle`, `JobStatus`, `JobState`,
   `job_status_interaction`.
5. Testgen: `InteractionCatalog`, `compile_interaction_catalog`,
   `seal_app_catalog`.
6. Theme: `Theme`, `REQUIRED_A11Y_TOKENS`, `validate_element_style_contract`,
   `default_styles=False`.
7. Discovery/fleet: `hedron.__all__`, distribution/plugin/asset registries,
   Explorer package-health slice.

## Honesty fixtures (Stage 1 migration)

1. Application assets extend the typed CSP-aware pipeline; do not authorize
   arbitrary response-body rewriting or CDN fetch.
2. Route/effect export remains metadata-only and never executes handlers.
3. Workflow composition layers on `JobBackend` and does not reopen
   `polling_only`.
4. Fleet doctor stays read-only installed-application triage; external-author
   `DOCTOR-054` remains 0.54.
5. Rollback to 0.52.0 restores repository-only DX seams without Stage 1
   contract symbols.

## Frozen 0.52.0 D-092 seams

`inject_page_assets`, `AssetRef`, `Diagnostic`, `Suppression`, `RouteMeta`,
`routes_json`, `JobBackend`, `JobState`, `InteractionCatalog`, `Theme`,
`REQUIRED_A11Y_TOKENS`, `hedron.__all__`.

## Hosts

Flask/Django stay on existing adapter dispositions. No Stage 0 runtime or
package-version change during Stage 0. Cut tip is `v0.53.0`.
