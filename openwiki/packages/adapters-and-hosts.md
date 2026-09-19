---
type: reference
title: Adapters and Host Integrations
description: How Flask, Django, Jinja, FastAPI Workbench, and Posit hosts bind Hedron rendering, interaction, security, and deployment behavior.
tags:
  - adapters
  - hosts
  - deployment
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T19:14:00.347Z
sources:
  - id: openwiki-source-58f99f87a902d45beb58a50f
    resource: repo://packages/fastapi-workbench/src/fastapi_workbench/config.py
  - id: openwiki-source-ad9422ba6fe943a957ac4bc8
    resource: repo://packages/fastapi-workbench/src/fastapi_workbench/middleware.py
  - id: openwiki-source-74f926d4e23f5bc6bae8de5d
    resource: repo://packages/fastapi-workbench/src/fastapi_workbench/resolve.py
  - id: openwiki-source-c76e668e47893eb2076784c8
    resource: repo://packages/hedron-django/src/hedron_django/middleware.py
  - id: openwiki-source-493ac11cff1ab3d5d4f63697
    resource: repo://packages/hedron-django/src/hedron_django/routing.py
  - id: openwiki-source-b2668e52c624aa669e607299
    resource: repo://packages/hedron-flask/src/hedron_flask/app.py
  - id: openwiki-source-b17b135cc2880c8bf31bcb78
    resource: repo://packages/hedron-flask/src/hedron_flask/routing.py
  - id: openwiki-source-c7d1d154753e4194be406202
    resource: repo://packages/hedron-jinja/src/hedron_jinja/binding.py
  - id: openwiki-source-84598da8abe0708e7b3a5b73
    resource: repo://packages/hedron-jinja/src/hedron_jinja/integration.py
  - id: openwiki-source-a048bda6e4c093ca8c679fd5
    resource: repo://packages/hedron-posit/src/hedron_posit/config.py
  - id: openwiki-source-e942ce090321d78c385305ee
    resource: repo://packages/hedron-posit/src/hedron_posit/products.py
  - id: openwiki-source-07eca43993ed14a29ade62c2
    resource: repo://tests/adapters/django/test_django_adapter.py
  - id: openwiki-source-1c2022d117c268cc19791866
    resource: repo://tests/adapters/fastapi_workbench/test_resolve.py
  - id: openwiki-source-48a6596ce0b0e0940877c319
    resource: repo://tests/adapters/flask/test_flask_adapter.py
  - id: openwiki-source-a98440671af850fafac5a3ad
    resource: repo://tests/adapters/posit/test_resolve_connect.py
  - id: openwiki-source-583f0b6e720ec0ab174602c0
    resource: repo://tests/jinja/test_integration.py
generated: { by: "codex", at: "2026-09-19T16:47:17.741Z" }
---

# Adapters and Host Integrations

Hedron keeps its component, interaction, security, and render contracts in the
core packages while host adapters translate those contracts into framework
lifecycles. The adapters are not independent rendering engines: they own route
registration, request identity, response conversion, middleware, and host
deployment details, then delegate component preparation and compilation to the
shared core.

## Flask and Django request adapters

`HedronFlask` supports both direct construction with an import name and
application-factory composition through `init_app()`. Initialization attaches
the extension, mounts static assets, and binds a URL reverser. Its `page`,
`view`, and `action` helpers wrap native Flask routes so component values,
`InteractionResult`, and compiled outcomes become framework responses. Unsafe
methods are CSRF-protected before the view runs; the adapter also derives
request mode and authentication signals from the Flask request.

`HedronDjango` provides the corresponding Django application and response
surface. Its routing helpers reverse named URL patterns, seed a CSRF cookie for
safe requests, validate unsafe requests, compile interaction values, and
support both synchronous and ASGI-safe asynchronous preparation. The Django
security middleware binds the request security plane, applies the configured
`SecurityPolicy` response headers, and unbinds the request state even when the
view fails.

Both adapters preserve host-native responses and URL conventions while keeping
Hedron's fragment, interaction, and CSRF semantics aligned. Their capability
records and feature/catalog helpers let package extensions opt into the host
without reaching into private framework state.

## Jinja as a checked rendering host

`hedron-jinja` is a stricter integration boundary than a raw template render.
`HedronJinja` binds typed component aliases, assets, providers, themes, and
application-scoped handles through an immutable `JinjaBinding`. Binding and
template checks freeze the environment before rendering, validate component
and asset declarations, and expose the small HDJ grammar: guards, components,
slots, and conditional assets.

Each render creates a request-local session that collects assets, headers,
diagnostics, traces, and component identity metadata under explicit budgets.
Direct Jinja streaming is rejected because it could emit HTML before metadata
is complete. The supported streaming shape is `two_phase_stream()`: finish the
`RenderResult` first, then yield body chunks. Async environments use
`render_async()` rather than silently buffering through the synchronous path.

## Workbench and Posit deployment

`fastapi-workbench` owns deployment resolution shared by the Posit adapter.
`WorkbenchConfig` is immutable and accepts explicit mode, host, port, mount,
public base, topology, worker, proxy, and launch settings. Pure resolution
returns a secret-free `ResolvedDeployment`; it does not import an app, bind a
socket, or execute a binary. Mount paths and public origins are normalized and
validated so proxy prefixes, cookie paths, redirects, and browser URLs cannot
become unsafe absolute or traversal paths. The middleware then applies the
resolved mount and request-target rules, and the runner loads or prepares the
ASGI app and exports the resolved runtime state.

`hedron-posit` composes this core with product detection and Connect-specific
configuration. `PositConfig` nests Workbench and Connect settings; product
resolution returns evidence for `auto`, `workbench`, or `connect`. When Connect
is active, Workbench mode is forced off because Connect owns the mount. Cookie
mode and bridge settings are validated explicitly, unsupported bridge secrets
fail closed, and the Posit middleware adds only the branding and compatibility
behavior that the resolved deployment supports.

The adapter tests exercise route/response parity, CSRF and security headers,
template contracts, mount normalization, environment precedence, product
selection, cookie handling, and launcher behavior. See [Application and Runtime
Lifecycle](../runtime/application-lifecycle.md) for the context these adapters
enter and [Security and Request Boundaries](../security/request-boundaries.md)
for the shared request protections.
