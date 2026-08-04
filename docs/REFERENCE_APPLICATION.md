# Reference application specification

The first implementation is validated through a single coherent application rather than isolated demos.

[Try the interactive team-admin and Explorer interfaces](examples/index.md){ .md-button .md-button--primary }

## Scenario

An authenticated team administration application contains:

- a full dashboard page and HTMX navigation;
- a lazy addressable `UserTable` protected by router dependencies;
- typed create, edit, and delete actions with forms, validation fragments, CSRF, and authorization;
- a paged DataEditor with read-only identifiers, writable fields, optimistic concurrency, and audit hooks;
- a Plotly activity chart loaded from an async source;
- `Auto()` rendering for a dataframe and ordinary Python values;
- a scoped async data cache with visible hit/miss behavior;
- a bounded upload/download flow plus metric and status components;
- typed Python composition for canonical authoring and optional Jinja coverage in its owning suite;
- scoped styles, a custom theme, and locally served assets;
- Component Explorer examples, route/HTMX traces, security findings, assets, data, and chart panels.

## Required failure scenarios

- anonymous and unauthorized resource requests;
- invalid forms and forged read-only editor changes;
- stale DataEditor update conflict;
- chart-source timeout with retryable fallback;
- client cancellation during a lazy component load;
- missing optional chart package;
- unsafe raw HTML, URL, and asset-path attempts;
- production startup with Explorer mistakenly enabled.

## Proof obligations

The application must work through `Hedron()` and demonstrate at least one router mounted into plain `FastAPI`. It must use released-style package imports, dependency overrides in tests and examples, generated OpenAPI, strict CSP, an offline/no-Node asset path, browser keyboard tests, and documented deployment behind a root-path proxy.

Phase 0.7 adds two deliberately small native adapter slices rather than forcing the complete
FastAPI application into framework-shaped abstractions:

- the Flask slice proves native routing, request context, CSRF/session integration, validation/error
  fragments, reverse URLs, assets, and the declared WSGI capability set; and
- the Django slice proves native URL configuration, middleware, CSRF/session/forms behavior,
  reverse URLs, assets, async/WSGI capability labels, and the Django QuerySet adapter decision.

The FastAPI application remains the production-operations proof. It deploys with multiple workers
behind a prefixed reverse proxy using external static assets plus executable cache and job
conformance implementations. Adapter slices prove native behavior; they are not cosmetic render-only
demos.

The application grows cumulatively from the static rendering proof in phase 0.1 (`v0.1.0`) through
the complete data-and-visualization workflow in phase 0.6 (`v0.6.0`). Phase 0.7 adds operations and
native adapter slices. Later capability phases extend those slices through their native integration
and deployment paths; clean-install production deployment from built/published artifacts remains a
gate for every promoted capability, not merely a tutorial milestone.
