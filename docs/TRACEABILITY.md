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
| Declarative authoring (0005, 0030, 0031) | `COMPONENT`, `JINJA`, `STABILITY` | Explicit `.hdj` format and standards-first adapter; removed HDN history | HDJ replacement gates |
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
| HDJ authoring (0031) | Versioned `.hdj` prologue/profile, trusted Jinja body, Hedron bridges, full HTMX/HTML/CSS/JS surface, metadata, immediate replacement | `hedron-jinja` implementation | HDJ + HDN removal gates, phase 0.9 |
| Live transport (0032) | Live SSE/WS/stream/preload contracts | `hedron` live helpers + core framing | release-gate-0.10 |
| Data-app surface NiceGUI expansions (0033–0036) | Maps, media download/Range, surface chrome, scenario marks | Implemented — phase 0.15 (Published) | 0.15 release gate |
| Curated/specialty extras (0037–0038) | CodeEditor/interactive extras; terminal/robotics/native shell | Accepted — phase 0.16 implemented | [release-gate-0.16.toml](acceptance/release-gate-0.16.toml) |
| Interaction authoring ergonomics (0039) | `region`/`@fragment`, `swap` builders, dev region diagnostics + Explorer click preview | Implemented — phase 0.15 DX (Published) | 0.15 release gate |
| Reactive dashboards / agent interfaces (0040–0044) | InteractionGraph / patches / notebook / MCP / shell DX | Implemented — phase 0.17 **Published** (`v0.17.0`) | [release-gate-0.17.toml](acceptance/release-gate-0.17.toml) |
| Model demos / inference workflows (0045–0050) | `InferenceInterface` / `ModelDemo` / `ExampleSet` / feedback / `InferencePolicy` / recorder / Gradio adapter / workflows | Implemented — phase 0.18 **Published** (`v0.18.0`) | [release-gate-0.18.toml](acceptance/release-gate-0.18.toml) |
| Accessibility engineering / inclusive authoring (0051–0055; RFC-0023 umbrella) | `AccessibilityContract` / profile / scenarios / Explorer a11y / PE / landmarks / Page scripts / governance | Published as phase 0.19 (`v0.19.0`); living train is `0.25.0` (**Published**) | [release-gate-0.19.toml](acceptance/release-gate-0.19.toml) |
| Production security floor / adapter parity (RFC-0012 / 0021 / 0028; D-051) | HTMX/eval floor, mount helpers, prod gates, Flask/Django regions/CSP/AuthSignal, scaffolds, wheel smoke | Implemented — phase 0.20 **Published** (`v0.20.0`) | [release-gate-0.20.toml](acceptance/release-gate-0.20.toml) |
| CSRF / SecurityPolicy composition (RFC-0012 / 0019 / 0024; D-051) | Pluggable CSRF strategies, composable headers, `CsrfField` / Form HTMX kwargs | Implemented — phase 0.22 **Published** (`v0.22.0`) | [release-gate-0.22.toml](acceptance/release-gate-0.22.toml) |
| Production-quality maturity program (RFC-0056; D-053) | Stable-tier expansion (**0.23 Published**), live-transport disposition (**0.24 Published** — `polling_only`), production archetype / landmine quarantine (**0.25 Published** / Verified); optional undated `1.0` DoD | 0.23–0.25 Verified (0.21 human AT sessions remain P0) | [release-gate-0.23.toml](acceptance/release-gate-0.23.toml) · [STABLE_FACADE](api/STABLE_FACADE.md) · [LIVE_DISPOSITION](api/LIVE_DISPOSITION.md) · [PRODUCTION_ARCHETYPE](api/PRODUCTION_ARCHETYPE.md) · [0.24](acceptance/release-gate-0.24.toml) · [0.25](acceptance/release-gate-0.25.toml) |

Every implementation pull request must name the owning RFC, public contract if any, implementation
specification, and acceptance checks. Phase 0.6 closure and later work also names stable evidence IDs
and the commands/artifacts that will satisfy them.
