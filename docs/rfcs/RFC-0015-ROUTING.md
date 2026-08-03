# RFC-0015: Routing

**Status:** Accepted

## Design

`HedronRouter` is the primary organizational unit. It inherits FastAPI prefixes, tags, dependencies, responses, and operation metadata. `page`, `component`, and `action` are the canonical app-local registration decorators backed by `HedronRoute`; `Hedron` delegates matching decorators to its root router.

Component folders may expose a router module and explicitly discover declared resources. Discovery does not expose every component. Generated internal component URLs use stable registry names under a configurable internal prefix and are hidden from OpenAPI by default.

Reusable packages use `@addressable` to define a resource descriptor and `include_component` to expose it on a selected router. Declaration alone never creates an application route.

Route names and operation IDs are deterministic, collision-checked, mount-aware, and suitable for reverse generation. A component reference resolves through the registry rather than string concatenation. Mounted Hedron sub-applications retain independent registries, themes, and Explorer policy unless intentionally shared.

## Security and compatibility

Router dependencies are the preferred way to apply shared authorization. Route generation never assumes that a parent page’s dependency protects a child resource. Reserved prefixes and conflicts fail at startup.

## Acceptance criteria

- Prefixes, mounts, dependencies, URL reversing, and duplicate names have tests.
- Internal resources are absent from Swagger unless explicitly public.
- Plain FastAPI and `Hedron()` routers produce equivalent route behavior.
