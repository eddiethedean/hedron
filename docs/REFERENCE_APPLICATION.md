# Reference application specification

The first implementation is validated through a single coherent application rather than isolated demos.

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
- HDN for one custom component and Python composition for another;
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

The application grows cumulatively from the static rendering proof in phase 0.1 (`v0.1.0`) through the complete data-and-visualization workflow in phase 0.6 (`v0.6.0`). Its clean-install production deployment is the phase 0.8 (`v0.8.0`) architectural validation gate, not merely a tutorial milestone.
