# What's new in 0.45

**Published `v0.45.0`** (in-tree cut; tag/PyPI deferred). Owning decisions: D-074 / D-077.
Tracking: [#328](https://github.com/eddiethedean/hedron/issues/328).

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

## Layers

1. **Catalog and manifest** — compile/seal after plugins, fail closed on production mismatch.
2. **Projections and hosts** — namespaced metadata plus Flask/Django/Jinja adapters.
3. **Tooling and fleet** — Explorer/CLI/OpenAPI plus current-surface package providers.

## Compatibility

Pin the train to `hedron>=0.45.0,<0.46`. Rollback: pin `>=0.44.0,<0.45`. 0.42/0.43/0.44 apps that do not read the catalog stay request-path identical.
