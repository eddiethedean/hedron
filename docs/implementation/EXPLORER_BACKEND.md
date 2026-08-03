# Explorer backend implementation

## Architecture

The backend is an optional development router over sanitized registry views and trace stores. It never imports application modules from user-supplied names or reads arbitrary paths. Preview and request operations reference registered identifiers only.

## Services

- Component, route, action, asset, style, plugin, and example queries.
- Isolated example rendering with declared FastAPI dependency overrides.
- Addressable-resource request simulation through the application test transport.
- Render, HTMX, cache, async, security, accessibility, and performance traces.
- Build and diagnostic results with stable codes and source references.

Mutation simulation is disabled by default. Example data sources are isolated from production persistence unless an explicit authenticated configuration says otherwise.

## Production policy

The router is not registered outside development by default. Production mode requires a separate authorization dependency, rate limits, audit events, strict redaction, restricted headers, and explicit operation allowlists.

## Verification

Test absence in production, authorization, registry-only addressing, redaction, path and URL injection, dependency override isolation, mutation policy, trace bounds, and parity between preview and application rendering.

