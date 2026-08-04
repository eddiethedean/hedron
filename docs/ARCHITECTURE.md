# Architecture overview

## Product shape

Hedron is a collection of typed component primitives, a framework-neutral renderer
(`hedron-core`), and thin host adapters. The flagship `hedron` package extends FastAPI
rather than inventing a separate web runtime. Supported Beta adapters
(`hedron-flask`, `hedron-django`) render the same portable components and
`InteractionResult` contracts without depending on FastAPI.

## Request paths

### FastAPI (flagship)

1. A request enters ordinary FastAPI/Starlette middleware.
2. `HedronRoute` delegates parsing, dependency injection, security, and exception behavior to FastAPI.
3. A page, action, or addressable-component factory returns a model, explicit response, or component.
4. Hedron selects page or fragment mode and validates the return value.
5. The deterministic renderer builds a node tree, collects assets, and serializes safe HTML.
6. A FastAPI/Starlette response carries HTML, cache policy, security headers, and approved HTMX headers.
7. HTMX performs resource-level requests and swaps; Web Components retain bounded browser-local interaction.

### Flask / Django (Supported adapters)

1. A request enters Flask or Django middleware (sessions, CSRF, auth as configured by the app).
2. A view returns a component, `InteractionResult`, or host response.
3. Adapter helpers (`hedron_route` / `hedron_view`, `respond`, `interaction_response`) authorize
   fragment/OOB policy and merge validated HTMX headers.
4. The same `hedron-core` renderer produces HTML.
5. The host framework returns an HTTP response (WSGI or ASGI).

Adapter **Supported** claims exclude documented Deferred rows (official HTMX SSE transport;
Django QuerySet as a first-party DataSource; Hedron-owned Django forms). See
[Compatibility](COMPATIBILITY.md) and [adapter acceptance](acceptance/ADAPTERS.md).

## Package boundaries

```text
hedron                         FastAPI flagship and beginner API
├── hedron-core                models, components, renderer, registry protocols; legacy experimental HDN
├── FastAPI / Starlette        routing, DI, security, ASGI, responses
└── optional integrations      Explorer, data, charts, sample plugins

hedron-flask ──> hedron-core   Flask adapter (Beta Supported; no FastAPI)
hedron-django ─> hedron-core   Django adapter (Beta Supported; Django >=5.2,<6)
```

`hedron-core` does not import application-framework or transport types. Integrations
depend on portable core/adapter protocols and are lazy where optional. Distribution and
import boundaries are normative in [Project layout](PROJECT_LAYOUT.md).

## Shared registry

A sealed registry snapshot is consumed by rendering, routing, OpenAPI, Explorer, assets,
examples, tests, CLI, security diagnostics, and build tooling. No subsystem independently
rediscovers components or invents identifiers.

## Build and runtime

Development builds the registry, scoped CSS, legacy experimental HDN (`.hdn`) where present,
assets, examples, and diagnostics incrementally. Production uses precompiled deterministic
manifests and locally served fingerprinted assets. Node.js is not required by application
developers or deployments.

## Architectural invariants

- Rendering never implies route exposure.
- Request props never default to all component props.
- Framework security dependencies remain authoritative for each host.
- Rendering contains no hidden I/O.
- Secrets do not enter public metadata, identities, caches, or diagnostics.
- Every inference has an explanation and override.
