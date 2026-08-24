# Public API

Start with the contracts that match Hello / Refresh / a CSRF form. Autodoc signatures
and the full export map sit below that path.

If you know the outcome but not the symbol, use [API by task](by-task.md). It points from
common application jobs to the appropriate guide and contract page.

After [First app → What is HTMX → HTMX interactions → Minimal form](../getting-started/index.md):

1. [Hedron](HEDRON.md) — FastAPI application facade
2. [Router](ROUTER.md) — `@page` / `@component` / `@action`
3. [Page](PAGE.md) — navigable HTML documents
4. [Interaction](INTERACTION.md) — `FragmentRegion`, `InteractionResult`, `swap`
5. [Responses](RESPONSES.md) — PAGE vs FRAGMENT HTML
6. [Exceptions](EXCEPTIONS.md) — CSRF / region HTTP map
7. [Mount / path prefix](MOUNT.md) — reverse-proxy subpaths and cookie `Path`
8. [Auth](AUTH.md) — optional OIDC helpers (`hedron[auth]`)
9. [CSRF composition](CSRF_COMPOSITION.md)
10. [Testing](TESTING.md) — `AppScenario`, HTMX asserts
11. [CLI](CLI.md) — `hedron check`, `routes`, `new`, `build`

!!! tip "`hedron` vs `hedron_core`"

    Day-to-day apps import from `hedron` (FastAPI facade, router, responses, testing).
    Advanced typing and rendering primitives such as `NodeLike`, `RenderMode`, and
    `get_registry` live in `hedron_core`. Prefer `hedron` re-exports when available.

**Stability:** API levels are defined in [STABILITY.md](STABILITY.md). A **minimal
`stable` tier** (render/model/interaction/CSRF/router facades and portable adapter
helpers) is compatibility-protected on the 0.x train. Everything else is `beta` or
`experimental` unless listed. Package maturity remains **Beta** — pin versions.
Live transports stay **experimental**; prefer polling. Upgrade notes:
[upgrade guide](../guides/upgrade.md).

The repository train tip and latest installable PyPI release are **`v0.62.0`**;
application users should pin `hedron>=0.62.0,<0.63`.

!!! note "Contracts vs full reference"

    API pages are hand-maintained contracts, with **mkdocstrings** signatures on
    [Autodoc](AUTODOC.md) (still a subset of every `hedron.__all__` name). Map of
    exports → pages: [Public API coverage map](COVERAGE.md).

    **Contract page template** (required for new/edited flagship pages):

    1. Short example
    2. Signature / members
    3. Parameters
    4. Returns
    5. Errors (HTTP status and/or `HED-*` codes)
    6. See also

    Gold standard: [Field](FIELD.md). Flagship pages ([Hedron](HEDRON.md),
    [Router](ROUTER.md), [Action](ACTION.md), [Interaction](INTERACTION.md),
    [Page](PAGE.md), [CSRF composition](CSRF_COMPOSITION.md), [Jobs](JOBS.md), …)
    should follow that shape. Outline pages
    (for example [Utility components](UTILITY_COMPONENTS.md), [ColorMode](COLORMODE.md))
    may stay shorter — prefer guides + Autodoc when Errors is missing.
    Human error index: [Error codes](../guides/error-codes.md).

## Full catalog

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
- [Accessibility (`hedron_core.a11y`)](A11Y.md)
- [Plugins](PLUGINS.md)
- [Testing](TESTING.md)
- [API diagnostics](DIAGNOSTICS.md)
- [CLI](CLI.md)
- [Jobs](JOBS.md)
- [Prepare lifecycle](PREPARE.md) · [Security audit sink](AUDIT.md) · [Tracing](TRACING.md)

Also: [Configuration](../CONFIGURATION.md) ·
[Compatibility](../COMPATIBILITY.md) · [Glossary](../GLOSSARY.md) ·
[Live interaction guide](../guides/live-interaction.md)

## Stability and adapters

- [Stability classifications](STABILITY.md)
- [Security types](SECURITY_TYPES.md)
- [CSRF composition](CSRF_COMPOSITION.md)
- [Framework adapter contracts](ADAPTERS.md)
- [Job interaction contracts](JOBS.md) — polling Supported; SSE experimental


## Later trains (opt-in)

These contracts compile onto the golden path. They are **not** required for Hello.

- [Refreshable views](REFRESHABLE_VIEWS.md)
- [Type-driven authoring](TYPE_DRIVEN_AUTHORING.md)
- [Interaction catalog](INTERACTION_CATALOG.md)
- [Package-native workflows](PACKAGE_WORKFLOWS.md)
- [Maps](MAPS.md)
- [HTMX extension integration](HTMX_EXTENSIONS.md) — **0.48** Published in-tree (morph Deferred)
- [Hedron HTMX interaction extension](HTMX_HEDRON_EXTENSION.md) — proposed **0.64** contract
- [FastAPI/Pydantic convergence](FASTAPI_PYDANTIC_CONVERGENCE.md) — **0.49** Published in-tree
- [Explorer architecture](EXPLORER_ARCHITECTURE.md) — **0.50** Published in-tree (related [#496](https://github.com/eddiethedean/hedron/issues/496)–[#500](https://github.com/eddiethedean/hedron/issues/500) / [#502](https://github.com/eddiethedean/hedron/issues/502) / [#503](https://github.com/eddiethedean/hedron/issues/503))
- [Curated extras](EXTRAS.md) — historical 0.51 contract; see [Current release and support](../guides/current-release.md) for installable versions.

Public exception types: [EXCEPTIONS.md](EXCEPTIONS.md).
