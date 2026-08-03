# Architectural decisions

This is the authoritative decision log for the phase 0.0 specification baseline. Accepted decisions remain in force until superseded by a later numbered entry.

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
| D-016 | Accepted | DataEditor uses typed change sets and a Web Component; Tabulator is the initial default adapter. |
| D-017 | Accepted | `Auto()` uses an ordered, inspectable renderer registry and always permits explicit override. |
| D-018 | Accepted | Rust acceleration and cross-language bindings are deferred until contracts stabilize and benchmarks justify them. |
| D-019 | Accepted | General streamed HTML is deferred; lazy addressable components are the default deferred-loading pattern. |
| D-020 | Accepted | Durable work belongs to external job systems; FastAPI `BackgroundTasks` is used only for small post-response work. |
| D-021 | Accepted | Hedron exposes scoped cache decorators and Streamlit-inspired utility components while leaving cache services, storage, and durable state to the application ecosystem. |
| D-022 | Superseded | The original pre-1.0 roadmap used cumulative releases 0.1 through 0.9; D-031 replaces only that numbering. |
| D-023 | Superseded | The initial matrix was CPython 3.12–3.14 with FastAPI `>=0.141.1,<0.142`, Pydantic `>=2.13.4,<2.14`, and bundled HTMX 2.0.10. Python range superseded by D-034. |
| D-034 | Accepted | Supported CPython is 3.11–3.14 (`requires-python = ">=3.11,<3.15"`). FastAPI `>=0.141.1,<0.142`, Pydantic `>=2.13.4,<2.14`, and bundled HTMX 2.0.10 remain as under the compatibility policy. |
| D-024 | Accepted | Hedron uses the documented monorepo distribution/import layout; Explorer is installed through `hedron[dev]`, not required by production `hedron`. |
| D-025 | Accepted | `@app.page`/`@router.page`, `@app.component`/`@router.component`, and `@app.action`/`@router.action` are the canonical app-local decorators. `@addressable` defines a reusable component resource that becomes reachable only through `include_component`. |
| D-026 | Accepted | Public code renders through opaque `ComponentNode`/`NodeLike` contracts and `render(...) -> RenderResult`; concrete serializer nodes and the serializer implementation remain private in 0.x. |
| D-027 | Accepted | Logical IDs are readable namespaced identifiers; generated instance and asset IDs use versioned SHA-256-derived formats with collision checks as specified in `IDENTIFIERS.md`. |
| D-028 | Accepted | The phase 0.1/0.2 built-in component catalog is fixed by `api/BUILT_INS.md`; later data, utility, and chart catalogs remain assigned to their roadmap phases. |
| D-029 | Accepted | The repository uses a uv workspace, Hatchling, Ruff, Pyright, pytest/pytest-anyio, and the configuration and diagnostic contracts documented for 0.0. |
| D-030 | Superseded | No open-source license is inferred; license selection blocks public publication but not local phase 0.1 implementation. Superseded by D-033. |
| D-031 | Accepted | The specification phase is 0.0, every subsequent pre-1.0 phase shifts down by one minor number through the phase 0.8 release candidate, and the stable target remains phase 1.0. Scope, order, and gates are otherwise unchanged. |
| D-032 | Accepted | Phase 0.0 publishes no package. Each implementation phase `0.N` has initial release tag `v0.N.0` and Python package version `0.N.0`; phase 1.0 has `v1.0.0`/`1.0.0`. First-party distributions use the coordinated release train, and patch releases remain within their owning roadmap phase. |
| D-033 | Accepted | Hedron is licensed under the MIT License; the repository root and each publishable distribution ship `LICENSE` with matching package metadata. |
| D-035 | Accepted | Phase 0.7 retains the `v0.7.0` train but is governed by a phase 0.6 behavioral closure gate and staged internal gates: portable adapter foundation, FastAPI operations, Flask, Django, jobs/conformance, and an optional-transport decision. Portable semantics are shared; ASGI, WSGI, and framework-native differences are explicit capability claims. Phase 0.8 is feature-frozen hardening, and final-version rehearsals use published `1.0.0rcN` artifacts before `v1.0.0`. Completion from phase 0.6 onward requires linked automated or immutable evidence; checked prose alone is not release evidence. This supersedes D-031 only where D-031 preserved the former 0.7/0.8 scope and gate shape unchanged. |
| D-036 | Accepted | Django QuerySet as a first-party `hedron-data` DataSource is Deferred for the `v0.7.0` Supported adapter claim. Apps may bridge QuerySets themselves; Hedron does not advertise QuerySet paging/security as a portable contract until a later decision. |
| D-037 | Accepted | Phase 0.7 external cache and durable job conformance targets Redis (`redis` client, JSON `h1:` keys). FastAPI `BackgroundTasks` remains non-durable (D-020). Official HTMX SSE extension is Deferred post-1.0; bounded polling is the Supported job-status transport. |

## Phase 0.7 entry blockers

Entry blockers for adapter implementation (COMPATIBILITY ranges, evidence ledgers, core ownership,
Explorer acyclic deps) are closed for the `v0.7.0` train. Remaining work is staged gates 0.7A–0.7F.

Changes to accepted decisions require an explicit superseding decision and affected RFC/API updates.
