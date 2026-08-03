# RFC-0004: FastAPI integration

**Status:** Proposed

## Design

`HedronRoute(APIRoute)` recognizes component return contracts, runs normal FastAPI dependency and request processing, validates the returned component type, and selects a Hedron response. `HedronRouter(APIRouter)` organizes pages, components, and actions. `Hedron(FastAPI)` is a thin convenience application configured with those primitives.

Hedron uses FastAPI lifespan, middleware, `BackgroundTasks`, `StaticFiles`, dependency overrides, custom operation IDs, and OpenAPI extensions. It does not monkey-patch FastAPI response serialization.

## Modes

- In `Hedron()`, a component annotation and component result produce HTML automatically.
- In plain `FastAPI()`, handlers return `HTML(component)` and opt into documentation with `hedron_response(...)` or the router.
- Explicit Starlette/FastAPI `Response` objects pass through unchanged.

## Requirements

- `Depends`, `Security`, yield dependencies, exception handlers, middleware, and request validation retain normal behavior.
- Internal component resources use `include_in_schema=False` unless explicitly public.
- Route metadata records render modes, component identity, HTMX behavior, and Explorer links.

## Acceptance criteria

- Equivalent FastAPI dependency tests pass on Hedron routes.
- Component and JSON routes coexist in one router.
- Plain FastAPI adoption requires no application subclass.

