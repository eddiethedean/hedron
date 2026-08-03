# Explorer frontend implementation

## Delivery

The Explorer frontend is an official browser package served as fingerprinted local assets. It may be authored with build tooling internally, but consuming Hedron applications require no Node.js installation. Its protocol is versioned independently from the Python backend.

## Views

Navigation covers components, pages, actions, routes, diagnostics, security, settings, and plugins. Detail panels cover preview, props, examples, request simulation, HTMX inference, graph, render trace, styles, assets, data, visualization, accessibility, security, async timing, and source where permitted.

The UI must remain keyboard operable, screen-reader understandable, responsive, and usable without color-only status. Large graphs and traces use bounded pagination or virtualization.

## Safety

The frontend never receives secrets and still treats all displayed source, HTML, JSON, and diagnostic text as untrusted. It does not use arbitrary `eval`, inline event handlers, or remote CDNs. Mutation controls reflect backend authorization rather than hiding forbidden operations only in the interface.

## Verification

Use browser contract tests, CSP tests, accessibility checks, keyboard scenarios, route-version compatibility, request cancellation, and visual regression for critical panels.

