---
status: implemented
---

# Framework adapter contracts

**Target:** phase 0.7A, with concrete Flask and Django bindings in 0.7C–0.7D.

Hedron's portable adapter surface represents only semantics that can exist without a raw framework
request or response. It covers:

- normalized HTMX request facts and page/fragment/history mode;
- interaction content, status, OOB updates, approved headers, history, and cache policy;
- reverse-URL requests resolved by the host router;
- static/build-manifest asset references;
- authenticated/session-scope signals without session contents;
- lifecycle resource descriptions and sanitized diagnostics; and
- declared capability metadata.

Concrete adapters translate these values to native FastAPI, Flask, or Django requests, responses,
routers, middleware, validation, sessions, CSRF, and lifecycle hooks. Core contracts never retain a
raw request, response, session, dependency, database handle, or application object.

## Portable baseline

Supported adapters produce equivalent safe HTML and HTTP semantics for page/fragment selection,
approved HTMX headers, status/error fragments, OOB mechanics, cache variation, assets, and reverse
URLs. Every header is revalidated at the adapter boundary; an arbitrary header mapping cannot bypass
redirect, selector, cache, or security policy.

## Capability declaration

Each adapter publishes a machine-readable capability record. Claims include sync/async endpoints,
disconnect cancellation, cooperative deadlines, yield/dependency lifetime, sessions, CSRF/forms,
background work, lifespan, route reversal, root-path/script-name handling, and Explorer mounting.
Capabilities are labeled portable, ASGI, WSGI, or framework-specific and link to native evidence.

Unsupported capability access fails explicitly or follows a documented degraded path; Hedron never
simulates framework authority or silently claims parity.
