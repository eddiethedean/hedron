# What's new in 0.53

In-tree tip is **0.53.0** (Published; Git tag and PyPI upload deferred). PyPI still
serves **0.52.0** — pin `hedron>=0.52.0,<0.53` from the public index until the 0.53
wheel lands.

## 0.53.0

Application DX contracts (RFC-0080 / D-091 / D-092):

### Application assets (`ASSET-053`)

- Ordered, CSP-aware page asset injection via `inject_page_assets`, `AssetRef`, and
  registry `AssetMeta`.
- Extends the typed asset pipeline; does not authorize arbitrary response rewriting.

### Actionable diagnostics (`DIAG-053`)

- Version-aware `Diagnostic` / `DiagnosticSeverity` / `Suppression` with JSON, text,
  and SARIF serializers.
- `hedron check` surfaces stable codes for adopter triage.

### Structured routes (`ROUTE-053`)

- Registry `RouteMeta`, `routes_json`, and CLI `hedron routes`.
- Metadata-only export — never executes handlers.

### Operation workflows (`WORKFLOW-053`)

- Long-running operation composition on `JobBackend` / `JobHandle` / `JobStatus` /
  `JobState` without reopening `polling_only`.

### Catalog test generation (`TESTGEN-053`)

- `InteractionCatalog` / `CatalogEntry` and sealed app catalogs for generated checks.

### Semantic theming (`THEME-053`)

- `Theme`, required a11y tokens, element style contracts, and `default_styles=False`.

### Discovery and fleet (`DISCOVER-053` / `FLEET-053`)

- Curated API discovery (`hedron discover`) and installed-fleet doctor
  (`hedron fleet`) for read-only triage of apps on the living train.

Shared exit gates `DOCS-053`, `PKG-053`, and `REGRESS-053` are Verified for this cut.
