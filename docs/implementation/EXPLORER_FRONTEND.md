# Explorer frontend implementation

## Delivery

**Shipped (0.50):** server-rendered HTML strings in `explorer_router` plus one local CSS file (`/hedron-explorer/static/explorer.css`) and bundled HTMX. Application developers do not need Node.js. There is no independently versioned SPA protocol and no fingerprinted Explorer frontend package. Large tables use cursor pagination and `HED-EXPLORER-0001` truncation banners with next/prev links — not silent slices.

## Views

Shipped navigation covers components, routes, graph, security, a11y, cache, data, charts, maps, extensions, auto, packages, elements, inventory, interactions, features, and settings. Plugin `ExplorerPanelMeta.path` does **not** add nav entries. Dedicated pages/actions/examples/HTMX/render-trace/async-timing views remain Deferred relative to RFC-0007 (covered by routes + component detail).

Large tables use cursor pagination and `HED-EXPLORER-0001` truncation diagnostics (QUERY-050). The 0.49.1 silent slices (`[:200]`, a11y `[:40]`, audit `[:20]`, cache `recent(50)`) are the planning baseline only.

The UI must remain keyboard operable, screen-reader understandable, responsive, and usable without color-only status.

## Safety

The frontend never receives secrets and still treats all displayed source, HTML, JSON, and diagnostic text as untrusted. It does not use arbitrary `eval`, inline event handlers, or remote CDNs. Mutation controls reflect backend authorization rather than hiding forbidden operations only in the interface.

## Verification

Use browser contract tests, CSP tests, accessibility checks, keyboard scenarios, route-version compatibility, request cancellation, and visual regression for critical panels. 0.50 a11y is shell/panel behavior (`A11Y-050`); it does not close `EXPLORER-019`.
