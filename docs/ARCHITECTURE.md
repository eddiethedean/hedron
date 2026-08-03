# Architecture overview

## Product shape

Hedron is a collection of typed component primitives, FastAPI routers and routes, response classes, middleware, compiler/build tools, and developer tooling. It extends FastAPI rather than creating a separate web runtime.

## Request path

1. A request enters ordinary FastAPI/Starlette middleware.
2. `HedronRoute` delegates parsing, dependency injection, security, and exception behavior to FastAPI.
3. A page, action, or addressable-component factory returns a model, explicit response, or component contract.
4. Hedron selects page or fragment mode and validates the return value.
5. The deterministic renderer builds a node tree, collects assets, and serializes safe HTML.
6. A FastAPI/Starlette response carries HTML, cache policy, security headers, and approved HTMX headers.
7. HTMX performs resource-level requests and swaps; Web Components retain bounded browser-local interaction.

## Package boundaries

```text
hedron                         FastAPI flagship and beginner API
├── hedron-core                models, components, renderer, HDN, registry protocols
├── FastAPI / Starlette        routing, DI, security, ASGI, responses
└── optional integrations      Explorer, data, charts, content, browser adapters

hedron-flask ──> hedron-core   framework-native Flask adapter
hedron-django -> hedron-core   framework-native Django adapter
```

`hedron-core` does not import application-framework or transport types. Integrations depend on stable core/adapter protocols and are lazy where optional. Distribution and import boundaries are normative in [Project layout](PROJECT_LAYOUT.md).

## Shared registry

A sealed registry snapshot is consumed by rendering, routing, OpenAPI, Explorer, assets, examples, tests, CLI, security diagnostics, and build tooling. No subsystem independently rediscovers components or invents identifiers.

## Build and runtime

Development builds registry, HDN, scoped CSS, assets, examples, and diagnostics incrementally. Production uses precompiled deterministic manifests and locally served fingerprinted assets. Node.js is not required by application developers or deployments.

## Architectural invariants

- Rendering never implies route exposure.
- Request props never default to all component props.
- Framework security dependencies remain authoritative.
- Rendering contains no hidden I/O.
- Secrets do not enter public metadata, identities, caches, or diagnostics.
- Every inference has an explanation and override.
