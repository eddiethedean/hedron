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

**Stability:** API levels are defined in [STABILITY.md](STABILITY.md). A **minimal
`stable` tier** (render/model/interaction/CSRF/router facades and portable adapter
helpers) is compatibility-protected on the 0.x train. Everything else is `beta` or
`experimental` unless listed. Package maturity remains **Beta** on PyPI — pin versions.
Live transports stay **experimental**; prefer polling. Upgrade notes:
[upgrade guide](../guides/upgrade.md).

!!! note "Contracts vs full reference"

    API pages are hand-maintained contracts, with **mkdocstrings** signatures for critical
    surfaces on [Autodoc](AUTODOC.md) (live helpers, adapters, and core facades — still a
    subset of every `hedron.__all__` name). For a map of every export to a doc
    page, see [Public API coverage map](COVERAGE.md).     Flagship narrative pages ([Hedron](HEDRON.md), [Router](ROUTER.md),
    [Action](ACTION.md), [Interaction](INTERACTION.md), [Page](PAGE.md), [SSE](SSE.md),
    [Streaming](STREAMING.md), [Field](FIELD.md), and peers linked below) aim for
    constructor / field tables, returns, errors, and examples. Some outline pages
    (for example [Utility components](UTILITY_COMPONENTS.md), [ColorMode](COLORMODE.md))
    are shorter summaries — prefer guides + Autodoc when a page lacks an Errors section.
    Human error index: [Error codes](../guides/error-codes.md).

## Shipped through 0.10

These surfaces are implemented on the **0.15.0** train (includes the 0.9 authoring break
and 0.10 live interaction; **pending cut** of `v0.15.0`—last published train is
**0.14.x**).

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
- [Prepare lifecycle](PREPARE.md) · [Security audit sink](AUDIT.md) · [Tracing](TRACING.md)

Also: [Configuration](../CONFIGURATION.md) · [Diagnostics format](https://github.com/eddiethedean/hedron/blob/main/docs/DIAGNOSTICS.md) ·
[Compatibility](../COMPATIBILITY.md) · [Glossary](../GLOSSARY.md) ·
[Live interaction guide](../guides/live-interaction.md)

## Stability and adapters

- [Stability classifications](STABILITY.md) — compatibility catalog (current train 0.15)
- [Framework adapter contracts](ADAPTERS.md) — Supported FastAPI / Flask / Django
- [Job interaction contracts](JOBS.md) — durable `JobBackend` + polling Supported; SSE experimental

## Current train notes

- Native Flask/Django depth, QuerySet DataSource, forms bridge, HDJ manifests/CSP inventory
  (introduced in 0.11; Supported on **0.15.0**, pending cut)
- Advanced async / observability (`prepare`, audit sink, tracing, durable Redis job status)
  — **0.15.0** (pending cut)
- Capture UI ships in **0.15** (no longer deferred)