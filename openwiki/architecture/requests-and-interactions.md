---
type: architecture
title: Requests and partial-page interactions
description: Hedron layers page, view, component, and action routes on FastAPI while selecting full-page or HTMX fragment responses through declared interaction policies.
tags: [routing, requests, htmx, interactions]
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T17:40:19.225Z
sources:
  - id: openwiki-source-437929cbb0f871b0489f77d0
    resource: repo://packages/hedron-core/src/hedron_core/htmx/headers.py
  - id: openwiki-source-77c7e52d0931db41d7101f66
    resource: repo://packages/hedron-core/src/hedron_core/htmx/policy.py
  - id: openwiki-source-1a09e7bd849370e0eafc6c42
    resource: repo://packages/hedron/src/hedron/app/hedron.py
  - id: openwiki-source-969925ba1e7129a581585dc1
    resource: repo://packages/hedron/src/hedron/app/pages.py
  - id: openwiki-source-16f877f1efc223d1a2eac4dc
    resource: repo://packages/hedron/src/hedron/responses/handlers.py
  - id: openwiki-source-e52eceaf634c7f9f9d3d3104
    resource: repo://packages/hedron/src/hedron/routing/route.py
  - id: openwiki-source-751be524ad0c1dd18a8c0169
    resource: repo://packages/hedron/src/hedron/routing/router.py
  - id: openwiki-source-67cdc1d6d9d91e0b10c11909
    resource: repo://tests/integration/test_fastapi_mvp.py
generated: { by: "codex", at: "2026-09-19T15:43:01.076Z" }
---

# Requests and partial-page interactions

Hedron keeps the host application's FastAPI request lifecycle and adds a typed server-rendered transport on top. The [rendering and component model](/openwiki/architecture/rendering-and-components.md) produces the HTML; this layer decides which route owns the request, which response mode is valid, which fragment targets are authorized, and how interaction outcomes become HTTP responses.

## Application and router ownership

`Hedron` subclasses `FastAPI` and `HedronPagesMixin`. Construction creates an application-owned runtime, installs the configured security/session and asset defaults, bootstraps a root `HedronRouter`, and adds runtime-context middleware. Including a `HedronRouter` attaches it to the host application so route registration uses that application's runtime and registry state. A plain FastAPI application can use `HedronRouter` directly, preserving ordinary JSON routes beside HTML routes.

The page mixin exposes the high-level decorators:

- `page(path)` registers navigable PAGE routes and can declare the fragment regions that an HTMX request may target.
- `view(path)` is the canonical safe replaceable fragment surface; it returns a handle carrying route, target, binding, and lifecycle metadata.
- `region(id)` declares a stable markup/allowlist target, defaulting to `#{id}`.
- `action(path)` registers a typed mutation, defaults to `POST`, supports an ordinary HTTP fallback, and accepts explicit authorization, idempotency, and outcome settings.

The lower-level `HedronRouter` uses the same boundaries. A page is included in OpenAPI by default and infers that `HX-Request` selects fragment versus page mode. Views and components default to fragment responses and are hidden from OpenAPI unless explicitly exposed. Actions default to OpenAPI inclusion, use fragment transport, and record CSRF, swap, validation, capability, and idempotency metadata.

## One endpoint conversion boundary

The route wrapper resolves the active `Request`, enforces CSRF before capability checks and side effects, optionally claims an idempotency replay key, invokes the user's sync or async handler, and sends its result through `HedronRoute.convert_endpoint_result`. That conversion preserves native `StarletteResponse` values, renders `InteractionResult` values through the interaction authority, renders `HTML` and components, serializes non-component `Model` values as JSON, and rejects unsupported return types.

The conversion boundary also prepares components against the request context and forces component routes into fragment mode. A page handler can therefore return the same component tree for ordinary navigation or an HTMX request, while the request and route kind select the appropriate shell/fragment response. The route wrapper adds the `Vary` dimensions needed to keep full-page and fragment bodies distinct.

## Declared interaction mechanics

`InteractionPolicy` is the portable contract for synchronization, indicators, CSRF embedding, focus restoration, history behavior, cache variation, and declared fragment regions. Undeclared HTMX targets are rejected by default. `InteractionResult` carries content plus validated status, target/swap, out-of-band updates, triggers, redirects, refreshes, history, cache, and extra-header fields; typed fields are converted into an approved HTMX header set. Default fragment caching is private/no-store and responses vary on HTMX request and history-restore headers, with target variation when policy requires it.

Error handling preserves the transport split: non-HTMX validation and HTTP errors remain framework-native JSON responses, while HTMX requests receive semantic error or validation fragments rendered against framework-owned status chrome. The rejected client `HX-Target` is not reused as an error destination.

The integration tests demonstrate the practical contract: ordinary JSON and HTML endpoints coexist, component routes stay out of OpenAPI by default, dependencies protect addressable components, unsafe actions require a CSRF token, and both sync and async page handlers are supported. For the security implications of these checks, see [security and request boundaries](/openwiki/security/request-boundaries.md); for background work initiated by an interaction, see [runtime state and background jobs](/openwiki/runtime/jobs-and-state.md).
