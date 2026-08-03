# Public API

Hedron documentation separates **callable APIs that ship in this release** from
**Accepted design contracts** that are not importable yet.

!!! tip "`hedron` vs `hedron_core`"

    Day-to-day apps import from `hedron` (FastAPI facade, router, responses, testing).
    Advanced typing and rendering primitives such as `NodeLike`, `RenderMode`, and
    `get_registry` live in `hedron_core`. Prefer `hedron` re-exports when available.

## Shipped in 0.4

These surfaces are implemented and published on the **0.4.0** train.

### Application

- [Hedron](HEDRON.md)
- [Router](ROUTER.md)
- [Page](PAGE.md)
- [Responses](RESPONSES.md)
- [State](STATE.md)

### Components

- [Component](COMPONENT.md)
- [Built-ins](BUILT_INS.md)
- [Addressable components](ADDRESSABLE.md)
- [Action](ACTION.md)

### Data and models

- [Models and Props](MODELS.md)
- [Field](FIELD.md)

### Platform

- [Rendering](RENDERING.md)
- [Themes](THEME.md)
- [Security types](SECURITY_TYPES.md)
- [Explorer](EXPLORER.md)
- [Plugins](PLUGINS.md)
- [Testing](TESTING.md)
- [API diagnostics](DIAGNOSTICS.md)
- [CLI](CLI.md)

Also: [Configuration](../CONFIGURATION.md) · [Diagnostics format](../DIAGNOSTICS.md) ·
[Compatibility](../COMPATIBILITY.md) · [Glossary](../GLOSSARY.md)

## Planned contracts

**Accepted ≠ shipped.** These design contracts describe future public APIs. They are
**not** importable in 0.4. Do not treat them as a product catalog for this release.

- [Auto](AUTO.md) — phase 0.5+
- [Utility components](UTILITY_COMPONENTS.md) — phase 0.5+
- [Data](DATA.md) — phase 0.5+
- [Data sources](DATA_SOURCE.md) — phase 0.5+
- [Charts](CHART.md) — phase 0.5+
- [Cache](CACHE.md) — phase 0.5+

Each shipped page documents purpose, signatures or representative usage, guarantees,
errors, and extension boundaries. Material public changes require the decision and RFC
process described under Project → Internals.
