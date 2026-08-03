# FastAPI integration acceptance

## Conformance

- [x] `HedronRoute` preserves path/query/header/cookie/body parsing and validation.
- [x] `Depends`, `Security`, scopes, router dependencies, yield cleanup, and dependency overrides behave like FastAPI.
- [x] Sync and async endpoints, exception handlers, middleware, lifespan, background tasks, and explicit responses work.
- [x] JSON and HTML routes coexist without changing JSON behavior.
- [x] Plain `FastAPI` plus `HedronRouter` requires no application subclass.
- [x] Prefixes, mounts, root paths, URL reversing, and sub-applications work.

## Documentation and security

- [x] HTML responses have accurate content types and OpenAPI schemas.
- [x] Internal resources are hidden by default.
- [x] Authorization metadata is preserved on component resources.
- [x] No monkey patch or undocumented FastAPI internal is required.

## Exit

The FastAPI compatibility matrix and shared adapter conformance suite pass for the declared supported versions.

