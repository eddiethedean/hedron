# Application DX API

**Phase 0.53 application DX contract:** D-091 / D-092 /
[RFC-0080](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md) /
[#514](https://github.com/eddiethedean/hedron/issues/514)–[#521](https://github.com/eddiethedean/hedron/issues/521).
**Stage 1 Implemented** (living tip `v0.57.0`; Published in-tree; tag/PyPI deferred). Stage 1
extends shipped 0.52 seams; it does **not** replace `inject_page_assets`,
`AssetRef`, `Diagnostic`, `Suppression`, `RouteMeta`, `routes_json`,
`JobBackend`, `JobState`, `InteractionCatalog`, `Theme`,
`REQUIRED_A11Y_TOKENS`, or `hedron.__all__` without negotiation.

Public Stage 1 surface (Verified gates; tip `v0.53.0`; Published in-tree; tag/PyPI deferred):

| Symbol | Role | Gate |
|---|---|---|
| `ApplicationAssetSpec` / `ApplicationAssetPlan` / `compile_application_asset_plan` | Dependency-ordered CSS/JS/module emission in the typed CSP-aware pipeline | `ASSET-053` |
| `ApplicabilityInterval` / `RemediationAction` / `normalize_severity_alias` | Version applicability, severity aliases, structured remediation | `DIAG-053` |
| `export_routes_document` / `export_effect_graph` / `ROUTE_DOCUMENT_SCHEMA` / `hedron routes --document` | Versioned typed route and effect graphs (non-executing) | `ROUTE-053` |
| `OperationWorkflow` / `is_terminal_job_state` / `retry_operation` / `TERMINAL_JOB_STATES` | Start/monitor/cancel/retry/busy/terminal/completion over `JobBackend` | `WORKFLOW-053` |
| `generate_interaction_tests` / `GENERATOR_VERSION` (+ `hedron testgen`) | Deterministic reviewable tests from sealed `InteractionCatalog` | `TESTGEN-053` |
| `run_visual_conformance` / `PRIVATE_SELECTORS_SUPPORTED` | Semantic-token compatibility for `default_styles=False` apps | `THEME-053` |
| `discover_public_api` / `hedron discover` | Curated import and stability discovery without silent renames | `DISCOVER-053` |
| `diagnose_installed_fleet` / `hedron fleet` | Read-only train/extras/plugin/asset diagnosis | `FLEET-053` |

## 0.53 contract locks

| Concern | Lock |
|---|---|
| Baseline seams | Consume D-092 shipped markers; do not fork |
| Assets | No CDN fetch, arbitrary inline script, or response-body rewrite requirement |
| Routes | Metadata-only export; never execute handlers |
| Workflow | Compose `JobBackend`; do not reopen `polling_only` |
| Fleet vs author doctor | `FLEET-053` installed app; `DOCTOR-054` remains 0.54 |

Gates: `ASSET-053`, `DIAG-053`, `ROUTE-053`, `WORKFLOW-053`, `TESTGEN-053`,
`THEME-053`, `DISCOVER-053`, `FLEET-053`, `DOCS-053`, `PKG-053`, `REGRESS-053`.

See [APPLICATION_DX_053](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/APPLICATION_DX_053.md) and
[RFC-0080](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md) for Stage 0 locks.
