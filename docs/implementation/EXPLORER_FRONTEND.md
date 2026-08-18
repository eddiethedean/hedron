# Explorer frontend implementation

## Delivery

**Shipped (0.49.1):** server-rendered HTML strings in `explorer_router` plus one local CSS file (`/hedron-explorer/static/explorer.css`) and bundled HTMX. Application developers do not need Node.js. There is no independently versioned SPA protocol and no fingerprinted Explorer frontend package.

**Planned (0.50):** keep server-authoritative HTML with HTMX partial navigation. Internal authoring of Explorer assets may use build tooling; consuming apps still require no Node. Contracts: [RFC-0077](../rfcs/RFC-0077-EXPLORER-ARCHITECTURE.md), [EXPLORER_050](EXPLORER_050.md).

## Views

Shipped navigation covers components, routes, graph, security, a11y, cache, data, charts, maps, extensions, auto, packages, elements, inventory, interactions, features, and settings. Plugin `ExplorerPanelMeta.path` does **not** add nav entries. Dedicated pages/actions/examples/HTMX/render-trace/async-timing views remain Deferred relative to RFC-0007 (covered by routes + component detail).

Large tables currently use silent slices (components `[:200]`, a11y `[:40]`, audit `[:20]`, cache `recent(50)`). Pagination or typed truncation diagnostics are a 0.50 QUERY-050 target, not shipped.

The UI must remain keyboard operable, screen-reader understandable, responsive, and usable without color-only status.

## Safety

The frontend never receives secrets and still treats all displayed source, HTML, JSON, and diagnostic text as untrusted. It does not use arbitrary `eval`, inline event handlers, or remote CDNs. Mutation controls reflect backend authorization rather than hiding forbidden operations only in the interface.

## Verification

Use browser contract tests, CSP tests, accessibility checks, keyboard scenarios, route-version compatibility, request cancellation, and visual regression for critical panels. 0.50 a11y is shell/panel behavior (`A11Y-050`); it does not close `EXPLORER-019`.
