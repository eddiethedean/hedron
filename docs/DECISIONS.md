# Architectural decisions

This is the authoritative decision log for the 0.1 specification baseline. Accepted decisions remain in force until superseded by a later numbered entry.

| ID | Status | Decision |
|---|---|---|
| D-001 | Accepted | Python is the reference implementation; pure Python remains supported. |
| D-002 | Accepted | `hedron` is the FastAPI flagship distribution; Flask and Django use separate adapters. |
| D-003 | Accepted | `HedronRoute`, `HedronRouter`, response classes, lifespan, middleware, DI, StaticFiles, and OpenAPI hooks are the integration foundation. |
| D-004 | Accepted | `hedron-core` imports no FastAPI, Flask, Django, ASGI, or WSGI types. |
| D-005 | Accepted | JSON endpoints return models; HTML endpoints return components. |
| D-006 | Accepted | `Hedron()` may be a convenience application, but it is a thin composition of FastAPI extension points, not a parallel runtime. |
| D-007 | Accepted | Components are renderable by default; addressability and public exposure are explicit. |
| D-008 | Accepted | HTMX is the default request/swap layer; Web Components own persistent browser-local interaction. |
| D-009 | Accepted | Hedron-owned `Model`, `Props`, `FormModel`, and `Field` expose a constrained Pydantic-backed type system. |
| D-010 | Accepted | HDN is optional and advanced; built-in Python components provide the beginner path. |
| D-011 | Accepted | Scoped styles use structural CSS rewriting, stable names, external assets, and light DOM by default. |
| D-012 | Accepted | The Component Explorer uses the same registry as rendering, routing, OpenAPI, tests, and assets. |
| D-013 | Accepted | Security is cross-cutting: contextual escaping, explicit trusted types, CSRF, safe URLs, private authenticated caching, and production-disabled Explorer. |
| D-014 | Accepted | Async I/O is supported at endpoints, dependencies, actions, sources, and plugin lifecycles; rendering stays synchronous until evidence requires otherwise. |
| D-015 | Accepted | The required dependency set stays small; integrations are lazy extras or separate packages. |
| D-016 | Accepted | DataEditor uses typed change sets and a Web Component; Tabulator is the proposed default adapter. |
| D-017 | Accepted | `Auto()` uses an ordered, inspectable renderer registry and always permits explicit override. |
| D-018 | Accepted | Rust acceleration and cross-language bindings are deferred until contracts stabilize and benchmarks justify them. |
| D-019 | Accepted | General streamed HTML is deferred; lazy addressable components are the default deferred-loading pattern. |
| D-020 | Accepted | Durable work belongs to external job systems; FastAPI `BackgroundTasks` is used only for small post-response work. |

## Open decisions before implementation

- O-001: minimum and maximum supported Python versions.
- O-002: initial FastAPI and Pydantic compatibility ranges.
- O-003: monorepo package layout and whether `hedron-explorer` ships in the flagship distribution or as a default development extra.
- O-004: exact public decorators and naming for pages, addressable components, and actions.
- O-005: initial HTML node representation and serializer API.
- O-006: asset fingerprint and stable component identifier formats.
- O-007: the smallest built-in component set needed for the first vertical slice.

