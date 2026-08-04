# RFC-0025: Component lifecycle

**Status:** Accepted

## Lifecycle

1. Define and validate component and props contracts.
2. Register metadata, examples, assets, styles, and optional route factories.
3. Resolve request inputs and FastAPI dependencies.
4. Perform explicit synchronous or asynchronous data preparation.
5. Build a deterministic node tree.
6. Serialize with contextual escaping.
7. Select page, fragment, file, stream, or explicit response behavior.
8. Run framework-managed post-response work and cleanup.

Normal component constructors perform no hidden network or database I/O. Data belongs in endpoint factories, sources, dependencies, or a future explicit `prepare()` hook. Props are immutable during rendering and request-scoped context is not stored globally.

Startup compiles registries, CSS, assets, routes, plugin contributions, and any existing experimental
HDN compatibility artifacts through application lifespan. Development may recompile affected
artifacts; production consumes build manifests. RFC-0031 replaces and removes the HDN step.

## Acceptance criteria

- Lifecycle stages have separate trace timings and contextual errors.
- Dependency cleanup occurs after rendering and after streaming iteration when applicable.
- Development reload cannot leave duplicate registry entries or stale asset mappings.
- Deterministic components can be rendered in tests without an HTTP request.
