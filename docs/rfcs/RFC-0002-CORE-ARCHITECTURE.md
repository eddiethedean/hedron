# RFC-0002: Core architecture

**Status:** Accepted

## Summary

Hedron consists of a framework-neutral component engine and framework adapters. The FastAPI adapter is the reference integration and uses only documented FastAPI and Starlette extension points.

## Layers

1. Hedron models and field metadata.
2. Components, node trees, registry entries, and render context.
3. Deterministic HTML serialization and page/fragment render results.
4. Framework adapters for request context, URLs, responses, security hooks, and lifecycle.
5. HTMX, assets, HDN, scoped styles, Explorer, and optional integrations.

Dependency arrows point inward. `hedron-core` has no ASGI, WSGI, or application-framework imports. Browser packages do not alter core rendering semantics.

## Invariants

- A prepared component renders deterministically.
- Registry metadata is the single source for routing, Explorer, OpenAPI, assets, examples, and tests.
- Components never gain endpoints merely by being rendered.
- Framework adapters preserve their host’s dependency, security, and lifecycle authority.
- Optional integrations are lazy and cannot change base behavior when absent.

## Acceptance criteria

- Core rendering tests run without FastAPI installed.
- FastAPI, future Flask, and future Django adapters can pass a shared rendering conformance suite.
- No circular dependency exists between core, adapters, Explorer, and optional integrations.

