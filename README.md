# Hedron

Hedron is a Python-first framework for building typed, server-rendered component applications with FastAPI, HTML, HTMX, scoped CSS, and optional Web Components—without requiring Node.js.

> **Project status:** Phase 0.0, the specification and project foundation, is complete. Implementation has not started. The next milestone is phase 0.1, the typed rendering core, targeting `v0.1.0`. There is no installable Hedron package yet.

## Product direction

Hedron is designed to combine:

- React-like component composition using typed Python contracts;
- Streamlit-like ease for common Python objects, data tools, and charts;
- FastAPI-native routing, dependency injection, security, OpenAPI, lifespan, and async I/O;
- ordinary HTML, CSS, HTTP, HTMX, and standards-based Web Components;
- an inspectable Component Explorer that explains inferred behavior;
- official development and production paths that do not require npm or a JavaScript bundler.

The initial audience is Python teams building FastAPI CRUD applications, internal tools, dashboards, forms, administrative systems, and data applications.

## Architectural boundaries

- `hedron-core` remains independent of FastAPI, Flask, Django, ASGI, and WSGI.
- HTML endpoints return components; JSON endpoints continue to return models.
- Components are renderable by default but become HTTP-addressable only through explicit registration.
- HTMX owns request-and-swap behavior; Web Components own durable browser-local interaction.
- Authorization, persistence, trust, destructive intent, and application state are never inferred.
- Contextual escaping, typed trust boundaries, accessibility contracts, and private authenticated caching are secure defaults.
- Hedron is not an ORM, identity provider, client-side SPA runtime, durable job queue, distributed cache, or whole-script rerun engine.

## Roadmap

Phase 0.0 publishes no package. Each implementation phase maps to an initial release tag; Python package versions omit the leading `v`.

| Phase | Initial release | Outcome |
|---|---|---|
| 0.0 | None | Accepted specification and project foundation |
| 0.1 | `v0.1.0` | Framework-neutral typed rendering core |
| 0.2 | `v0.2.0` | Secure FastAPI and HTMX application MVP |
| 0.3 | `v0.3.0` | HDN, scoped styles, assets, and themes |
| 0.4 | `v0.4.0` | Explorer, CLI, testing, plugins, and component-author platform |
| 0.5 | `v0.5.0` | Data applications, intelligent rendering, caching, and utility UI |
| 0.6 | `v0.6.0` | Visualization and first-party integrations |
| 0.7 | `v0.7.0` | Flask/Django adapters and production operations |
| 0.8 | `v0.8.0` | Public API freeze, release candidate, and hardening |
| 1.0 | `v1.0.0` | Stable supported Hedron release |

See the complete [roadmap](ROADMAP.md) for scope, feature ownership, RFC assignments, and release gates.

## Documentation

The specification is the current project deliverable and the sole authority for implementation:

- [Specification index](docs/README.md)
- [Current status](docs/STATUS.md) and [pre-coding readiness report](docs/READINESS_REPORT.md)
- [Architecture](docs/ARCHITECTURE.md), [decisions](docs/DECISIONS.md), and [project layout](docs/PROJECT_LAYOUT.md)
- [Foundations](docs/foundations/README.md) and [RFC index](docs/rfcs/README.md)
- [Public API contracts](docs/api/README.md)
- [Implementation specifications](docs/implementation/README.md)
- [Acceptance specifications](docs/acceptance/README.md)
- [Compatibility policy](docs/COMPATIBILITY.md) and [engineering baseline](docs/ENGINEERING_BASELINE.md)

Accepted RFC and API status means the design has been selected; it does not mean the feature is implemented or available before its roadmap phase.

## Starting phase 0.1

The initial implementation target is `hedron-core` at `v0.1.0`. The implementation packet is:

- [Phase 0.1 roadmap scope](ROADMAP.md)
- [Rendering API](docs/api/RENDERING.md), [component API](docs/api/COMPONENT.md), [security types](docs/api/SECURITY_TYPES.md), and [built-ins](docs/api/BUILT_INS.md)
- [Model system](docs/implementation/MODEL_SYSTEM.md), [rendering engine](docs/implementation/RENDERING_ENGINE.md), and [HTML serializer](docs/implementation/HTML_SERIALIZER.md)
- [Component-model acceptance](docs/acceptance/COMPONENT_MODEL.md), [security acceptance](docs/acceptance/SECURITY.md), and [accessibility acceptance](docs/acceptance/ACCESSIBILITY.md)

Installation and usage instructions will be added when the first working package exists. Until then, examples in the specification describe accepted API intent rather than released behavior.

## Contributing

Read [CONTRIBUTING.md](docs/CONTRIBUTING.md) before changing an accepted contract. Material changes require an architectural decision and an RFC revision or superseding RFC. Implementations must name their owning RFC, public contract, implementation specification, and acceptance checks.

## License

No open-source license has been selected. Until the owner adds one, this repository is all rights reserved and must not be publicly distributed as an open-source package.
