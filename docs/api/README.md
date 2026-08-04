# Public API

Hedron documentation separates **callable APIs that ship in this release** from
**Accepted design contracts** that are not importable yet.

!!! tip "`hedron` vs `hedron_core`"

    Day-to-day apps import from `hedron` (FastAPI facade, router, responses, testing).
    Advanced typing and rendering primitives such as `NodeLike`, `RenderMode`, and
    `get_registry` live in `hedron_core`. Prefer `hedron` re-exports when available.

**Stability:** Phase 0.8 establishes public classifications in [STABILITY.md](STABILITY.md)
(`beta` | `experimental` | `internal` | `deferred`). Package maturity (Beta/Alpha) is separate
from API level. Upgrade notes: [upgrade guide](../guides/upgrade.md).

!!! note "Contracts vs full reference"

    Many pages began as Accepted design contracts. Adopter-critical pages
    ([Hedron](HEDRON.md), [Interaction](INTERACTION.md), [Responses](RESPONSES.md),
    [Security types](SECURITY_TYPES.md), [Adapters](ADAPTERS.md)) include constructor /
    field tables, errors, and examples. Prefer those plus the guides when learning;
    read source only for unmarked internals.

## Shipped through 0.8

These surfaces are implemented on the **0.8.0** compatibility train (includes all 0.1–0.7
surfaces plus hardening and stability labels).

### Application

- [Hedron](HEDRON.md)
- [Router](ROUTER.md)
- [Page](PAGE.md)
- [Responses](RESPONSES.md)
- [Interaction](INTERACTION.md)
- [State](STATE.md)

### Components

- [Component](COMPONENT.md)
- [Built-ins](BUILT_INS.md)
- [Addressable components](ADDRESSABLE.md)
- [Action](ACTION.md)
- [Auto](AUTO.md)
- [Utility components](UTILITY_COMPONENTS.md)
- [ColorMode](COLORMODE.md)
- [Charts](CHART.md)
- [Content](CONTENT.md)

### Data and models

- [Models and Props](MODELS.md)
- [Field](FIELD.md)
- [Data](DATA.md)
- [Data sources](DATA_SOURCE.md)

### Platform

- [Rendering](RENDERING.md)
- [Themes](THEME.md)
- [Cache](CACHE.md)
- [Security types](SECURITY_TYPES.md)
- [Auth](AUTH.md)
- [Explorer](EXPLORER.md)
- [Plugins](PLUGINS.md)
- [Testing](TESTING.md)
- [API diagnostics](DIAGNOSTICS.md)
- [CLI](CLI.md)

Also: [Configuration](../CONFIGURATION.md) · [Diagnostics format](../DIAGNOSTICS.md) ·
[Compatibility](../COMPATIBILITY.md) · [Glossary](../GLOSSARY.md)

## Stability and adapters

- [Stability classifications](STABILITY.md) — 0.8 compatibility catalog
- [Framework adapter contracts](ADAPTERS.md) — Supported FastAPI / Flask / Django
- [Job interaction contracts](JOBS.md) — durable `JobBackend` + polling (SSE Deferred)

## Deferred contracts

**Accepted ≠ Supported.** These remain Deferred through the freeze (D-036, D-037):

- Django QuerySet as a first-party DataSource
- Official HTMX SSE live transport

## Planned after 0.8

- [Jinja integration](JINJA.md) — optional `hedron-jinja` trusted-template adapter accepted for
  phase 0.11; experimental on first implementation
