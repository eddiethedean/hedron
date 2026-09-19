---
type: architecture
title: Application and Runtime Lifecycle
description: Application-owned runtime context, ASGI request binding, lifespan startup, registry sealing, and production build gates.
tags:
  - runtime
  - lifecycle
  - fastapi
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T19:14:00.347Z
sources:
  - id: openwiki-source-1a09e7bd849370e0eafc6c42
    resource: repo://packages/hedron/src/hedron/app/hedron.py
  - id: openwiki-source-7aff23735739dee49a4a6aba
    resource: repo://packages/hedron/src/hedron/lifespan.py
  - id: openwiki-source-73da1192b50824bf6ec5581f
    resource: repo://packages/hedron/src/hedron/runtime.py
  - id: openwiki-source-5de9af4e58a3bda9f76af608
    resource: repo://tests/unit/test_app_runtime_scope.py
  - id: openwiki-source-c27df7de33d110296f5248ef
    resource: repo://tests/unit/test_runtime_052.py
generated: { by: "codex", at: "2026-09-19T16:47:17.741Z" }
---

# Application and Runtime Lifecycle

`Hedron` is a FastAPI application subclass whose constructor wires the host
application to an isolated runtime context. Route registration, component
registries, plugin state, cache and job backends, interaction handles, compile
policy, tracing, and concurrency are application-owned services even though
compatibility helpers remain available for core-only callers and tests.

## Context ownership and request scope

`HedronRuntimeContext.from_defaults()` forks the installed registry and creates
new plugin, projection, bundle, handle, and cache-trace state. If the configured
cache or job backend is process-local, it replaces it with a fresh in-memory
backend so two applications cannot silently share mutable state. It copies the
current concurrency and tracing settings into application-owned configuration
objects and creates the matching limiter.

`activate()` returns an `ExitStack` that binds every application service through
the relevant context manager: registry builder, plugin and projection
registries, interaction catalog, cache and cache traces, jobs, limiter,
tracing, compile policy, bundles, and handles. `RuntimeContextMiddleware` enters
that stack around each HTTP or WebSocket request; non-request ASGI scopes pass
through unchanged. Application methods such as route inclusion also activate
the owning runtime so late registration cannot accidentally consult another
application's compatibility builder.

The result is isolation at the boundary where global-looking APIs are used.
Two `Hedron` instances can expose the same route name while retaining separate
registries, cache telemetry, compile policies, feature bundles, and handle
descriptors. The application object, not import order, owns the state that a
request should observe.

## Construction and startup

The `Hedron` constructor creates the runtime before calling `FastAPI`, composes
the user lifespan with Hedron's lifespan, runs the bootstrap steps that install
security/session/routing integrations, and finally adds the runtime middleware.
It accepts explicit cache/job backends and concurrency/tracing configuration,
but still keeps their lifecycle under the application context.

`compose_lifespan()` performs synchronous startup work inside the async lifespan
boundary. It registers the default theme, resolves the project/build root,
loads a build manifest when present, loads enabled plugins, starts the plugin
loader, and seals the component registry and application interaction catalog.
Repeated lifespan entry is safe after the application registry is sealed: it
does not run registration hooks a second time. The optional user lifespan runs
after Hedron startup and before shutdown.

## Production and shutdown gates

Production mode requires a valid `.hedron/build/manifest.json` (or the explicit
build directory) and mounts its precompiled assets. Runtime CSS compilation is
disabled by the compile policy. If the manifest is missing or invalid, startup
fails with a build diagnostic and explains that `hedron build` must run first.
Non-production startup may load a manifest when available, but corrupt optional
metadata is logged and ignored. Production also validates durable backends and
the sealed interaction catalog.

On shutdown the plugin loader is stopped defensively and removed from app state.
The runtime compile policy is restored to its pre-lifespan value, which matters
when a test client or server enters the same application multiple times.

The runtime isolation tests cover registry, cache telemetry, compile policy,
feature bundles, handle descriptors, router inclusion after another app seals,
and one-time component preparation. See [Requests and Interactions](../architecture/requests-and-interactions.md)
for route behavior and [Jobs and Runtime State](jobs-and-state.md) for the
services bound inside this lifecycle.
