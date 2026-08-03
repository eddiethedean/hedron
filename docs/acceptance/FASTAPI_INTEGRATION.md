# FastAPI integration acceptance

## Conformance

- [x] `HedronRoute` preserves path/query/header/cookie/body parsing and validation.
- [x] `Depends`, `Security`, scopes, router dependencies, and yield cleanup behave like FastAPI.
- [ ] Dependency overrides are covered by a dedicated conformance suite. *(partial: FastAPI mechanism retained; Hedron-specific override fixtures deferred)*
- [x] Sync and async page endpoints work; lifespan composition and security middleware are installed by `Hedron()`.
- [ ] Dedicated coverage for exception handlers, `BackgroundTasks`, mounts, `root_path`, and sub-applications beyond the reference app. *(framework-compatible; matrix incomplete)*
- [x] JSON and HTML routes coexist without changing JSON behavior.
- [x] Plain `FastAPI` plus `HedronRouter` requires no application subclass; `HTML(...)` returns convert on `HedronRoute`; `mount_hedron_static(app)` serves bundled HTMX.
- [x] Component URL references (`ComponentRef` / `resolve_route_path`) respect registered paths and methods.

## Documentation and security

- [x] HTML responses have accurate content types and OpenAPI `text/html` metadata for pages.
- [x] Internal component resources are hidden by default (`include_in_schema=False`).
- [x] Authorization metadata is preserved when callers supply dependencies on `include_component`.
- [x] No monkey patch or undocumented FastAPI internal is required.
- [x] History restore requests (`HX-History-Restore-Request`) render PAGE mode.

## Exit

The FastAPI compatibility matrix for the declared supported versions is green for the phase 0.2 MVP surface (pages, fragments, actions, CSRF, OpenAPI hide-by-default, plain `HTML()` + static mount). Broader adapter conformance remains open for later phases.
