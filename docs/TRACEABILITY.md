# Specification traceability

This matrix identifies the primary public, implementation, and acceptance owner for each architecture area.

| Area / RFCs | Public contract | Implementation | Acceptance |
|---|---|---|---|
| Vision and core (0001–0002) | `HEDRON`, `COMPONENT` | Model, renderer, registry | Component model, capability roadmap |
| Components and lifecycle (0003, 0025) | `COMPONENT`, `MODELS`, `FIELD`, `PAGE` | Model system, rendering engine, serializer | Component model |
| Security boundary values (0012) | `SECURITY_TYPES` | Model system, serializer, security controls | Security, component model |
| Rendering and built-ins (0002–0003, 0025) | `RENDERING`, `BUILT_INS` | Renderer, serializer, registry | Component model, accessibility |
| FastAPI and routing (0004, 0015) | `HEDRON`, `ROUTER`, `RESPONSES` | Router generator | FastAPI integration |
| Portable adapters (0002, 0009, 0015, 0018) | `ADAPTERS`, `RESPONSES`, `STATE` | Framework adapters | Adapters |
| Declarative authoring (0005, 0030, 0031) | `COMPONENT`, `JINJA`, `STABILITY` | Legacy HDN parser/compiler; planned separate `hedron-jinja` adapter | HDN migration + Jinja gates |
| Styles and themes (0006, 0022) | `THEME` | CSS compiler, asset pipeline | Scoped styles, accessibility |
| Explorer and DX (0007, 0024) | `AUTO`, `EXPLORER` | Explorer backend/frontend, registry | Explorer |
| Caching and utilities (0013, 0024, 0026) | `CACHE`, `UTILITY_COMPONENTS`, `COLORMODE` | Cache layer, ColorMode, security controls | Caching/utilities |
| Addressability and HTMX (0008–0009) | `ADDRESSABLE`, `ACTION`, `RESPONSES` | Router, renderer, security | FastAPI, security |
| Data (0010, 0027) | `DATA`, `DATA_SOURCE` | Models, `hedron-data`, browser/asset integration | DataEditor |
| Visualization (0011) | `CHART` | Asset/plugin pipelines | Visualization |
| Security and accessibility (0012, 0023) | All | Security controls, serializer | Security, accessibility |
| Async and state (0013, 0026) | `ADDRESSABLE`, `ACTION`, `DATA_SOURCE` | Async runtime | Async |
| Durable jobs (0013, 0026, 0028) | `JOBS`, `RESPONSES` | Job interaction runtime | Jobs, async |
| Session and state scopes (0026) | `STATE` | Router/dependency adapters, cache layer | Security, async |
| Plugins and packages (0014, 0018) | Extension protocols | Plugin loader, build | Packaging/deployment |
| OpenAPI and CLI (0016–0017) | Router/response metadata | OpenAPI generator, build | FastAPI, packaging |
| Testing and performance (0019–0020) | Test helpers later | Every subsystem | Performance and subsystem suites |
| Browser and deployment (0021, 0028) | `DATA`, `CHART`, `THEME`, `ADAPTERS` | Explorer frontend, assets, build, operations | Accessibility, packaging, operations |
| Observability and operating diagnostics (0012, 0013, 0020, 0028) | `DIAGNOSTICS`, `ADAPTERS`, `JOBS` | Observability, operations | Observability, performance, security |
| Roadmap (0029) | All | All | Capability phases |
| Declarative authoring reset (0030) | Component authoring alternatives and legacy audit | Superseded by RFC-0031 | Historical HDN reset gate |
| Optional Jinja integration (0031) | Trusted templates, typed component bindings, metadata, migration | Planned separate package | Jinja + HDN migration gates, phase 0.11 |

Every implementation pull request must name the owning RFC, public contract if any, implementation
specification, and acceptance checks. Phase 0.6 closure and later work also names stable evidence IDs
and the commands/artifacts that will satisfy them.
