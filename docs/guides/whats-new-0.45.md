# What's new in 0.45

**Published `v0.45.0`**. Owning decisions: D-074 / D-077.
Tracking: [#328](https://github.com/eddiethedean/hedron/issues/328).

For new apps, pin `hedron>=0.51.0,<0.52`; see [What’s new in 0.51](whats-new-0.51.md).

## Highlights

Typed interaction ecosystem convergence is a sealed, read-only index over shipped 0.43/0.44
artifacts:

- **`InteractionCatalog` / `CatalogEntry`** index `BaseHandleDescriptor` fingerprints and optional
  redacted `hedron.type` TypeSchema fingerprints. They do not route, validate, authorize, or execute.
- **`interactions.json`** is an atomic sibling of the existing build `manifest.json`.
- **`PackageProjection` / `ProjectionProvider`** describe current package surfaces in reverse-DNS
  namespaces. Direct package APIs remain usable with no catalog.
- Flask/Django/Jinja project portable facts and keep host exceptions. They do not become FastAPI DI
  or TypeSchema producers.
- Explorer, CLI (`hedron inspect interactions`), OpenAPI fingerprint extensions, and `AppScenario`
  consume the public catalog.
- MCP/Gradio may consume catalog facts. Registration and catalog presence never grant exposure.

This is not `FeatureBundle`, `DataWorkspace`, `McpExposure`, a new client runtime, or a Supported
human AT claim.

## Fixes in this cut

- `FormBody` commands reject non-form `Content-Type` values with HTTP 415 instead of executing on
  defaults (#329). Completes the JSON-only #321 allowlist.

## Layers

1. **Catalog and manifest** — compile/seal after plugins, fail closed on production mismatch.
2. **Projections and hosts** — namespaced metadata plus Flask/Django/Jinja adapters.
3. **Tooling and fleet** — Explorer/CLI/OpenAPI plus current-surface package providers.

## Compatibility

Historical 0.45 pin was `hedron>=0.45.0,<0.46`. For new apps, pin `hedron>=0.51.0,<0.52`.
Rollback of a 0.45-era app: pin `>=0.44.0,<0.45`. 0.42/0.43/0.44 apps that do not read the catalog stay request-path identical.
