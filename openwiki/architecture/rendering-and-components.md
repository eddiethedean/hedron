---
type: architecture
title: Rendering and component model
description: Components are typed, server-rendered nodes whose identity, slots, preparation, normalization, and response mode are coordinated by the framework-neutral rendering core.
tags: [rendering, components, html, htmx]
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T19:14:00.347Z
sources:
  - id: openwiki-source-7c4843c448c2abe56f569b0d
    resource: repo://packages/hedron-core/src/hedron_core/component.py
  - id: openwiki-source-3a3cea436d0f3a883ea54413
    resource: repo://packages/hedron-core/src/hedron_core/rendering/normalize.py
  - id: openwiki-source-4cbf0db12ec2f4347d170c4d
    resource: repo://packages/hedron-core/src/hedron_core/rendering/session.py
  - id: openwiki-source-6e4ee1b767c4c2b798950145
    resource: repo://packages/hedron/src/hedron/responses/render.py
  - id: openwiki-source-67cdc1d6d9d91e0b10c11909
    resource: repo://tests/integration/test_fastapi_mvp.py
generated: { by: "codex", at: "2026-09-19T15:43:01.076Z" }
---

# Rendering and component model

Hedron's render path has a useful division of labor: `hedron-core` owns the component and node model, normalization, identity, and serialization contracts; `hedron` adapts the resulting `RenderResult` to FastAPI requests and HTML responses. The [monorepo architecture](/openwiki/architecture/monorepo.md) explains why those responsibilities live in separate packages.

## Components are typed render nodes

`Component[PropsT]` is the reusable server-rendered UI base. Subclasses infer or declare a Pydantic `Props` type, and construction accepts either one props instance or keyword fields—not both. Props validation failures are converted to a diagnostic with secret-safe messaging. Components keep children and slot values as render state; declared slots can be required, optional, or repeated, and missing required slots fail before rendering.

Component identity is derived from its distribution, module, logical name, and identity fields. Only props marked as identity participate, secret fields and `Secret` values are excluded, and an explicit `key` can disambiguate repeated instances. While `render()` executes, request-local identity exposes a collision-free instance ID and render key so built-ins can create stable DOM relationships without inventing global IDs.

Preparation is explicit. `prepare(ctx)` is an optional async hook for request-owned data, while `render()` remains synchronous; constructors are not allowed to perform hidden I/O. A component must override `render()`, and the lifecycle renderer checks slots, detects recursive render cycles, assigns automatic occurrence keys when needed, rejects duplicate instance IDs, and restores identity/style scopes even when rendering fails.

## Normalization is a bounded policy boundary

The node normalizer converts `NodeLike` values into the private node algebra. It handles text and scalar values, native elements, trusted raw nodes, components, component-node adapters, and materialized sequences. `Secret` values cannot enter the render tree, arbitrary generators and iterators are rejected because they may hide I/O, and unsupported values produce a diagnostic instead of being coerced implicitly. Native element metadata is also collected into browser and HTMX feature demand while children are normalized recursively.

`RenderSession` is the orchestration scope for one or more renders. It retains resource-budget state, identity mappings, diagnostics, browser demands, and HTMX extension collection across calls; normalization and serialization remain delegated to their specialized collaborators. Each call returns a `RenderResult` containing HTML, mode, identity deltas, diagnostics, browser plan, HTMX plan, and trace information such as node counts and the browser-plan fingerprint.

## From render result to HTTP response

The FastAPI response layer chooses a page or fragment mode from the request, an explicit `HTML` wrapper, or an existing `RenderResult`. Fragment mode removes the document shell before calling the core renderer. The layer enforces declared HTMX targets, applies the security policy and cache headers, attaches browser/build assets, and returns `PageResponse` for full pages or `FragmentResponse` for partial responses.

The integration tests show the observable contract: a normal page includes the document shell and browser assets, while an `HX-Request` response contains the component content without `<!DOCTYPE html>` or the default stylesheet. The same boundary rejects invented script tags unless the trust path is explicitly reviewed, so custom HTML must respect the [security and request boundaries](/openwiki/security/request-boundaries.md).

For request routing and action lifecycles around this render path, continue to [requests and partial-page interactions](/openwiki/architecture/requests-and-interactions.md).
