# RFC-0008: Addressable components

**Status:** Proposed

## Definition

An addressable component is an explicitly registered component factory with a route, typed public inputs, dependencies, response policy, and component return contract. It is an HTTP resource suitable for HTMX loading, refresh, polling, pagination, previews, caching, and independent tests.

## Rules

- Addressability never follows from component discovery or ordinary rendering.
- Public inputs come from the factory signature, not every component prop.
- FastAPI dependencies and security metadata are preserved.
- Registry identifiers generate URLs; request-controlled filesystem or import paths are never used.
- Authentication-sensitive results default to `private, no-store`.
- Lazy child resources do not inherit parent authorization implicitly; shared requirements must be attached through routers or explicit dependencies.

Component references may replace URL strings in buttons and refresh controls. Resolution validates route parameters and records the inferred method, URL, target, and swap.

## Acceptance criteria

- Unregistered components return no route.
- Dependency and authorization failures match ordinary FastAPI behavior.
- Component URLs reverse correctly under router prefixes and mounted applications.
- Identity and cache keys omit secret values.

