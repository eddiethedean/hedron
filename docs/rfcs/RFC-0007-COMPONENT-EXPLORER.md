# RFC-0007: Component Explorer

**Status:** Proposed

## Purpose

The Explorer is Hedron’s development control center and the primary implementation of “explain the magic.” It consumes the same registry used by rendering, routing, OpenAPI, assets, examples, tests, and diagnostics.

## Areas

- Components, pages, actions, routes, examples, and settings.
- Isolated previews with editable safe props and dependency overrides.
- Request simulation with headers, status, timings, HTML, and HTMX traces.
- Component graph, inverse consumers, render trace, source, HDN, styles, assets, and cache behavior.
- Accessibility, security, performance, and package-capability diagnostics.

## Security

Explorer routes are unregistered outside development by default. Production enablement requires explicit configuration, authentication, redaction, rate limits, audit logging, and mutation simulation disabled unless separately enabled. Controls cannot select arbitrary modules, paths, URLs, or headers.

## Acceptance criteria

- Every framework inference records a human-readable reason.
- Secrets, cookies, authorization headers, local paths, and sensitive values are redacted.
- Preview output uses the same renderer and assets as the application.
- Explorer absence in production is testable at the routing level.

