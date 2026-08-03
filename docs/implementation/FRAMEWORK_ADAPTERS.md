# Framework adapter implementation

## Boundary

`hedron-core` owns immutable adapter-neutral values and protocols. `hedron`, `hedron-flask`, and
`hedron-django` own conversion to native requests, responses, routers, middleware, sessions, CSRF,
validation, lifecycle, and errors. Core code imports no framework or transport type.

## Pipeline

1. The host router parses and validates using native mechanisms.
2. The adapter derives a bounded portable request/interaction context.
3. Application code returns a component, model, native response, or portable interaction result.
4. The shared renderer produces deterministic HTML and assets.
5. The adapter revalidates all response mechanics and constructs a native response.
6. Native middleware, dependency cleanup, sessions, security, and lifecycle remain authoritative.

## Capability model

Each adapter exports a capability record backed by native conformance tests. Portable behavior is
shared; ASGI disconnects, WSGI limitations, dependency/yield lifetimes, validation, sessions/forms,
background work, and lifespan remain capability-specific.

## Dependency graph

Explorer and build consumers use sanitized registry/manifest services owned by core. Optional
framework bridges mount those services without creating adapter-to-FastAPI or circular package
dependencies.

## Verification

Run the portable suite once per adapter, then native framework tests for every advertised
capability, clean imports with other frameworks absent, URL/proxy corpora, package tests, and native
reference slices.
