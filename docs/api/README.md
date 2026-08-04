# Public API

Hedron documentation separates **callable APIs that ship in this release** from
**Accepted design contracts** that are not importable yet.

## Start here (golden path)

After [Install → First app → HTMX → Minimal form](../getting-started/index.md), these five
contracts match what you just used:

1. [Hedron](HEDRON.md) — FastAPI application facade
2. [Router](ROUTER.md) — `@page` / `@component` / `@action`
3. [Page](PAGE.md) — navigable HTML documents
4. [Interaction](INTERACTION.md) — `FragmentRegion`, `InteractionResult`
5. [CLI](CLI.md) — `hedron check`, `routes`, `new`, `build`

!!! tip "`hedron` vs `hedron_core`"

    Day-to-day apps import from `hedron` (FastAPI facade, router, responses, testing).
    Advanced typing and rendering primitives such as `NodeLike`, `RenderMode`, and
    `get_registry` live in `hedron_core`. Prefer `hedron` re-exports when available.

**Stability:** Phase 0.10 continues the public classifications in [STABILITY.md](STABILITY.md)
(`beta` | `experimental` | `internal` | `deferred`). No public symbol is classified
`stable` yet — that level is reserved for a future promotion decision. Package maturity
(Beta/Alpha) is separate from API level. Upgrade notes: [upgrade guide](../guides/upgrade.md).

!!! note "Contracts vs full reference"

    API pages are hand-maintained contracts, with **mkdocstrings** signatures for critical
    surfaces on [Autodoc](AUTODOC.md) (live helpers, adapters, and core facades — still a
    subset of every `hedron.__all__` name). For a map of every export to a doc
    page, see [Public API coverage map](COVERAGE.md). Adopter-critical narrative pages
    ([Hedron](HEDRON.md), [Router](ROUTER.md), [Action](ACTION.md),
    [Interaction](INTERACTION.md), [Models](MODELS.md), [Responses](RESPONSES.md),
    [Security types](SECURITY_TYPES.md), [Auto](AUTO.md), [SSE](SSE.md),
    [Streaming](STREAMING.md), [Component](COMPONENT.md), [Page](PAGE.md), [Field](FIELD.md))
    include constructor / field tables, returns, errors, and examples. Prefer those plus
    the guides when learning; use autodoc + source when verifying unmarked internals.
    Human error index: [Error codes](../guides/error-codes.md).

## Shipped through 0.10

These surfaces are implemented in the published **0.10.1** train (includes the 0.9 authoring break
and 0.10 live interaction).

### Application

- [Hedron](HEDRON.md)
- [Router](ROUTER.md)
- [Page](PAGE.md)
- [Responses](RESPONSES.md)
- [Interaction](INTERACTION.md)
- [State](STATE.md)
- [SSE](SSE.md) · [Streaming](STREAMING.md) · [WebSocket channel](WEBSOCKET_CHANNEL.md) · [Preload](PRELOAD.md)

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
- [Jobs](JOBS.md)

Also: [Configuration](../CONFIGURATION.md) · [Diagnostics format](../DIAGNOSTICS.md) ·
[Compatibility](../COMPATIBILITY.md) · [Glossary](../GLOSSARY.md) ·
[Live interaction guide](../guides/live-interaction.md)

## Stability and adapters

- [Stability classifications](STABILITY.md) — 0.8+ compatibility catalog (0.10 live surfaces)
- [Framework adapter contracts](ADAPTERS.md) — Supported FastAPI / Flask / Django
- [Job interaction contracts](JOBS.md) — durable `JobBackend` + polling; SSE Supported in 0.10

## Deferred contracts

**Accepted ≠ Supported.** These remain Deferred (D-036 / D-041 / D-045):

- Django QuerySet as a first-party DataSource (0.11)
- First-party camera/microphone capture UI (0.15)

## Planned after 0.10

- Native Flask/Django depth and HDJ route/CSRF/forms reconciliation — phase 0.11
- Capture UI — phase 0.15
