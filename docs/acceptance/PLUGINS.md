# Plugin acceptance

## Loader *(phase 0.4)*

- [x] Plugins discover through a documented entry-point group and optional `[tool.hedron].plugins` filter.
- [x] Compatibility gates reject incompatible Hedron major ranges before contributions activate.
- [x] Failed validation discards the temporary registry builder (startup rollback).
- [x] Startup/shutdown hooks run in deterministic forward/reverse order.
- [x] Capability metadata covers Python, browser JS, styles, assets, Explorer panels, routes, and remote needs.
- [x] Plugins contribute Explorer panel metadata through public contracts only.

## Exit

A third-party sample package registers a component, style, asset, diagnostic owner, and Explorer metadata via the public plugin/registry APIs.
