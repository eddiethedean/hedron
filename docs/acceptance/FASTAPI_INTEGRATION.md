# FastAPI integration acceptance

## Conformance

- [ ] `HedronRoute` preserves path/query/header/cookie/body parsing and validation.
- [ ] `Depends`, `Security`, scopes, router dependencies, yield cleanup, and dependency overrides behave like FastAPI.
- [ ] Sync and async endpoints, exception handlers, middleware, lifespan, background tasks, and explicit responses work.
- [ ] JSON and HTML routes coexist without changing JSON behavior.
- [ ] Plain `FastAPI` plus `HedronRouter` requires no application subclass.
- [ ] Prefixes, mounts, root paths, URL reversing, and sub-applications work.

## Documentation and security

- [ ] HTML responses have accurate content types and OpenAPI schemas.
- [ ] Internal resources are hidden by default.
- [ ] Authorization metadata is preserved on component resources.
- [ ] No monkey patch or undocumented FastAPI internal is required.

## Exit

The FastAPI compatibility matrix and shared adapter conformance suite pass for the declared supported versions.

