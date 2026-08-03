# Component registry implementation

## Purpose

The registry is the single metadata graph for components, pages, addressable factories, actions, routes, props, examples, HDN, styles, assets, browser modules, security policy, accessibility contracts, and integration ownership.

## Lifecycle

Contributions are collected during import and plugin registration into an unsealed builder. Application lifespan validates identifiers, resolves dependencies, creates routes and manifests, then seals an immutable registry snapshot. Development reload builds a replacement snapshot atomically rather than mutating the active graph.

## Identity

Logical identifiers include namespace, component name, and optional package version. Route names, style scopes, asset ownership, and operation IDs derive from explicit stable functions. Absolute paths and secret values are stored only in redacted development source metadata, never public manifests.

## Queries

Consumers can resolve components, inverse consumers, routes, examples, assets, styles, adapters, and inference traces through read-only interfaces. Explorer uses sanitized views rather than raw internal objects.

## Verification

Test collision detection, dependency cycles, deterministic ordering, sealing, atomic reload, plugin failure rollback, serialization, redaction, and equivalence between routing, Explorer, OpenAPI, and build consumers.

