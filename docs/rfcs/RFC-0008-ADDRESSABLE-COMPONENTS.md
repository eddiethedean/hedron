# RFC-0008: Addressable components

**Status:** Accepted

## Definition

An addressable component is an explicitly declared component factory with typed public inputs, dependencies, response policy, and component return contract. It becomes an HTTP resource suitable for HTMX loading, refresh, polling, pagination, previews, caching, and independent tests only after explicit router exposure.

## Rules

- Addressability never follows from component discovery or ordinary rendering.
- `@router.component(path)` is the canonical application-local declaration and exposure API.
- `@addressable` creates a reusable descriptor; `router.include_component(descriptor, path=...)` makes it reachable.
- Public inputs come from the factory signature, not every component prop.
- FastAPI dependencies and security metadata are preserved.
- Registry identifiers generate URLs; request-controlled filesystem or import paths are never used.
- Authentication-sensitive results default to `private, no-store`.
- Lazy child resources do not inherit parent authorization implicitly; shared requirements must be attached through routers or explicit dependencies.

Component references may replace URL strings in buttons and refresh controls. Resolution validates route parameters and records the inferred method, URL, target, and swap.

## Acceptance criteria

- Renderable components and unexposed addressable descriptors produce no route.
- Dependency and authorization failures match ordinary FastAPI behavior.
- Component URLs reverse correctly under router prefixes and mounted applications.
- Identity and cache keys omit secret values.
