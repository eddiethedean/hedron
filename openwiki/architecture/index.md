# Files

- [Monorepo architecture](monorepo.md) - Hedron is a uv-managed Python workspace whose framework-neutral core, FastAPI runtime, satellites, adapters, and tooling have separate package boundaries and maturity contracts.
- [Rendering and component model](rendering-and-components.md) - Components are typed, server-rendered nodes whose identity, slots, preparation, normalization, and response mode are coordinated by the framework-neutral rendering core.
- [Requests and partial-page interactions](requests-and-interactions.md) - Hedron layers page, view, component, and action routes on FastAPI while selecting full-page or HTMX fragment responses through declared interaction policies.
