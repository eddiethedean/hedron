# What's new in 0.53

In-tree tip is **0.53.0** (Published; Git tag and PyPI upload deferred). PyPI still
serves **0.52.0** — pin `hedron>=0.58.0,<0.59` from the public index until the 0.53
wheel lands.

## 0.53.0

Application DX contracts (RFC-0080 / D-091 / D-092), Stage 1 Verified:

### Application assets (`ASSET-053`)

- `ApplicationAssetSpec` / `ApplicationAssetPlan` /
  `compile_application_asset_plan` for dependency-ordered CSS/JS/module emission
  in the typed CSP-aware pipeline.
- Extends shipped `inject_page_assets` / `AssetRef` seams; does not authorize
  arbitrary response rewriting.

### Actionable diagnostics (`DIAG-053`)

- `ApplicabilityInterval` / `RemediationAction` / `normalize_severity_alias` for
  version applicability, severity aliases, and structured remediation.
- Builds on `Diagnostic` / `Suppression` / `hedron check`.

### Structured routes (`ROUTE-053`)

- `export_routes_document` / `export_effect_graph` (and `hedron routes --document`)
  for versioned typed route and effect graphs.
- Metadata-only export — never executes handlers.

### Operation workflows (`WORKFLOW-053`)

- `OperationWorkflow` / `is_terminal_job_state` (plus retry/busy/terminal helpers)
  over `JobBackend` without reopening `polling_only`.

### Catalog test generation (`TESTGEN-053`)

- `generate_interaction_tests` (and `hedron testgen`) for deterministic reviewable
  tests from sealed `InteractionCatalog` entries.

### Semantic theming (`THEME-053`)

- `run_visual_conformance` for semantic-token compatibility on
  `default_styles=False` apps.

### Discovery and fleet (`DISCOVER-053` / `FLEET-053`)

- `discover_public_api` / `hedron discover` for curated import and stability
  discovery without silent renames.
- `diagnose_installed_fleet` / `hedron fleet` for read-only train/extras/plugin/asset
  diagnosis.

Shared exit gates `DOCS-053`, `PKG-053`, and `REGRESS-053` are Verified for this cut.
See [Application DX API](../api/APPLICATION_DX.md).
