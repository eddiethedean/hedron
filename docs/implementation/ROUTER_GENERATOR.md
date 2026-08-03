# Router generator implementation

## Inputs and outputs

The generator consumes sealed registry entries for pages, addressable components, and actions and emits `HedronRoute` registrations on a `HedronRouter`. It preserves user-supplied FastAPI metadata and adds normalized Hedron response and registry metadata.

## Route handling

The route wrapper delegates parameter parsing, dependencies, security, and exception flow to FastAPI. After the endpoint returns it passes explicit responses through, awaits supported results, validates component return contracts, selects page/fragment behavior, renders, and builds the correct response class.

Generated paths use configurable internal prefixes and declared public parameters. Component references reverse through FastAPI/Starlette routing with registry identity rather than concatenating strings. Conflicts, unsupported return annotations, unsafe methods, and missing security context diagnostics occur at startup where possible.

## Middleware boundary

Cross-cutting request/response behavior such as request IDs and outer security headers belongs in middleware. Component validation, rendering, HTMX selection, and route-specific OpenAPI metadata belong in the route handler.

## Verification

Reuse FastAPI dependency, error, path, mount, root-path, lifespan, response, background-task, and OpenAPI tests as conformance scenarios. Include sync/async endpoints, yield cleanup, cancellation, explicit responses, and router dependency inheritance.

