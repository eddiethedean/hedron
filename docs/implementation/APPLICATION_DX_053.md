# Application DX contracts (`v0.53`)

**Status:** Stage 0 Accepted; Stage 1 Implemented for all eight workstreams
(`ASSET-053`–`FLEET-053` Verified; shared exit gates `DOCS-053` / `PKG-053` /
`REGRESS-053` Verified). Living tip is `v0.53.0` (Published in-tree; tag/PyPI
deferred).<br>
**Tracking:** [#514](https://github.com/eddiethedean/hedron/issues/514)–[#521](https://github.com/eddiethedean/hedron/issues/521)<br>
**Decision/RFC:** D-091, refined by D-092 /
[RFC-0080](../rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md)<br>
**Planning baseline:** Published in-tree `v0.52.0` (D-092 Stage 0 contract)<br>
**Target:** Hedron `v0.53.0` (in-tree Published; Git tag / PyPI upload deferred)

## Consume shipped, do not fork (D-092)

- Assets: `inject_page_assets`, `AssetRef`, `AssetMeta`, `register_asset`
- Diagnostics: `Diagnostic`, `DiagnosticSeverity`, `Suppression`,
  `diagnostics_to_sarif`, `hedron check`
- Routes: `RouteMeta`, `routes_json`, `hedron routes`, `CatalogEntry`
- Workflow: `JobBackend`, `JobHandle`, `JobStatus`, `JobState`,
  `job_status_interaction`
- Testgen: `InteractionCatalog`, `compile_interaction_catalog`,
  `seal_app_catalog`
- Theme: `Theme`, `REQUIRED_A11Y_TOKENS`, `validate_element_style_contract`,
  `default_styles=False`
- Discovery/fleet: `hedron.__all__`, distribution/plugin/asset registries,
  Explorer package-health
- Do **not** reopen `polling_only`, `MORPH-048`, Explorer 0.50, extras 0.51,
  conformance/Posit 0.52, 0.54 package doctor, or `SR-021`

## Stage 1 seam map (eight workstreams)

| Workstream | Issue | Gate | Stage 1 seam focus |
|---|---|---|---|
| Assets | #514 | `ASSET-053` | Dependency-ordered application assets in the typed CSP-aware page plan |
| Diagnostics | #515 | `DIAG-053` | Applicability interval, severity aliases, justified suppression, remediation |
| Routes | #516 | `ROUTE-053` | Versioned typed route/effect documents and deterministic graph export |
| Workflow | #517 | `WORKFLOW-053` | Start/monitor/cancel/retry, busy, terminal, completion over `JobBackend` |
| Testgen | #518 | `TESTGEN-053` | Deterministic reviewable tests from redacted sealed catalogs |
| Theme | #519 | `THEME-053` | Semantic-token compatibility and reusable visual conformance |
| Discovery | #520 | `DISCOVER-053` | Versioned curated imports and stability discovery without renames |
| Fleet | #521 | `FLEET-053` | Read-only installed-application train/extras/plugin/asset diagnosis |

Shared exit gates: `DOCS-053`, `PKG-053`, `REGRESS-053`.

## Architecture

```text
hedron / hedron-core     application DX contracts over shipped 0.52 seams
       │
       ├── assets / inject_page_assets / AssetRef
       ├── diagnostics / Diagnostic / Suppression
       ├── routes / RouteMeta / routes_json
       ├── workflow / JobBackend / JobState
       ├── testgen / InteractionCatalog
       ├── theme / Theme / REQUIRED_A11Y_TOKENS
       ├── discovery / hedron.__all__
       └── fleet / installed-application doctor (not DOCTOR-054)
```

1. Stage 0 locks contracts only; Stage 1 implements gate evidence.
2. Application assets never authorize arbitrary response rewriting.
3. Route export never executes handlers; workflow does not reopen polling-only.
4. Fleet doctor complements—does not replace—0.54 external-author `DOCTOR-054`.

## Contract locks

- [application-dx-inventory-053.toml](../acceptance/application-dx-inventory-053.toml)
- [application-assets-053.toml](../acceptance/application-assets-053.toml)
- [application-contracts-053.toml](../acceptance/application-contracts-053.toml)
- [application-tooling-053.toml](../acceptance/application-tooling-053.toml)
