---
type: packages
title: Packages and extension surfaces
description: Hedron keeps framework-neutral behavior in hedron-core, application transport in hedron, and optional data, presentation, host, and integration capabilities in separately matured packages.
tags: [packages, extensions, adapters, bundles]
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T19:14:00.347Z
sources:
  - id: openwiki-source-1991748f385ebfab8fa9296f
    resource: repo://packages/hedron-core/src/hedron_core/adapter.py
  - id: openwiki-source-6db10f7ca19ecef676d788a2
    resource: repo://packages/hedron-core/src/hedron_core/bundles.py
  - id: openwiki-source-fdc52392c424ccda1dbb4fab
    resource: repo://packages/hedron-django/pyproject.toml
  - id: openwiki-source-1b850dc7c0e7bcc595dfafbf
    resource: repo://packages/hedron-flask/pyproject.toml
  - id: openwiki-source-05ea6ed7da91f0ad6003a506
    resource: repo://packages/hedron-mcp/pyproject.toml
  - id: openwiki-source-751be524ad0c1dd18a8c0169
    resource: repo://packages/hedron/src/hedron/routing/router.py
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
generated: { by: "codex", at: "2026-09-19T15:43:01.076Z" }
---

# Packages and extension surfaces

Choose an extension seam by asking which boundary owns the behavior. The framework-neutral [component and rendering core](/openwiki/architecture/rendering-and-components.md) should not acquire host-framework dependencies; the FastAPI package owns application routing and request conversion; satellites and adapters integrate optional capabilities without silently promoting them into the stable platform.

## Core, runtime, and satellites

`hedron-core` provides portable component, HTML, identity, interaction, and rendering contracts. `hedron` adds the FastAPI application/router surface. Data, charts, maps, Jinja/HDJ, Explorer, native acceleration, notebook, Gradio, MCP, simulation, and `edron` live in their own workspace packages, which keeps optional dependencies and maturity claims visible. The [monorepo architecture](/openwiki/architecture/monorepo.md) has the package map; the support matrix is the authority for stable versus beta status.

When a capability is a host integration, use an adapter package rather than branching the core. The portable adapter contract classifies capabilities as portable, ASGI, WSGI, or framework-specific and records support evidence, notes, and stability. The capability matrix currently describes FastAPI, Flask, and Django separately: all share safe HTML and HTMX header capabilities, while disconnect cancellation, lifespan, forms, URL helpers, querysets, and streaming vary by host.

The first-party Flask and Django packages each depend on `hedron-core` and their host framework, and both are published as Beta. `hedron-mcp` is also a separate Beta package with a deny-by-default MCP Streamable HTTP description, a plugin entry point, and dependencies on `hedron-core`, MCP, and Starlette. These package boundaries make it possible to install an integration deliberately and test its compatibility independently.

## Feature bundles

Feature packages should expose a `FeatureProvider.to_bundle()` method or construct an immutable `FeatureBundle`. A bundle declares its namespaced logical ID, provider/version, views, commands, components, projections, requirements, dependencies, limitations, and optional capabilities; it describes registration and does not execute application behavior itself.

`Hedron.include()` is the host-facing entry point for a bundle. Inclusion records state on the owning application, validates required host/package/browser capabilities, checks dependency order and depth, detects duplicate bundle IDs and handle conflicts, and refuses inclusion after the application catalog is sealed. Registration is guarded so a failure does not leave partial artifacts. Third-party providers must use their own namespace rather than claiming privileged `hedron:` IDs.

## Route and adapter seams

For a FastAPI feature, prefer the public `Hedron`/`HedronRouter` surfaces: register a page, view, component, or action and use declared fragment regions, dependencies, capabilities, and idempotency options. `include_component()` is the explicit bridge for an addressable descriptor or factory, with fragment transport and opt-in OpenAPI exposure. See [requests and partial-page interactions](/openwiki/architecture/requests-and-interactions.md) for the route lifecycle.

For a new host framework, implement the adapter contract and document the capability differences rather than copying FastAPI internals. For a reusable UI/data capability, put the package-local models and provider in a satellite, compile it to a bundle, and let the host materialize handles and own registration. For a browser-local behavior, use the typed browser/HTMX demand paths described in the README; arbitrary script injection is outside the authoring model.

Before depending on a satellite in a public contract, check [quality and release contracts](/openwiki/operations/quality-and-release.md) and the support matrix. Version numbers do not override the package's declared maturity.
