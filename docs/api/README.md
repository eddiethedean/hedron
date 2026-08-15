# Public API

Hand-maintained **contracts** for shipped surfaces on the **0.28** train, plus
[Autodoc](AUTODOC.md) (mkdocstrings) for critical signatures. Autodoc is still a
**subset** of every `hedron.__all__` name (~230 exports). The [coverage map](COVERAGE.md)
lists **every** root export → docs page. Public exception types:
[EXCEPTIONS.md](EXCEPTIONS.md).

Accepted RFCs that are not yet importable live in the GitHub maintainer corpus (excluded
from Read the Docs). Adopters should start from the golden-path contracts below.

## Planned 0.43 maintainer contract

[Refreshable views and commands](REFRESHABLE_VIEWS.md) records the accepted D-071 / RFC-0070
public contract for the planned 0.43 phase. It is **not importable on 0.42** and is not part of the
shipped golden path until all 0.43 gates are Verified.

## Start here (golden path)

After [First app → What is HTMX → HTMX interactions → Minimal form](../getting-started/index.md), these
contracts match what you just used:

1. [Hedron](HEDRON.md) — FastAPI application facade
2. [Router](ROUTER.md) — `@page` / `@component` / `@action`
3. [Page](PAGE.md) — navigable HTML documents
4. [Interaction](INTERACTION.md) — `FragmentRegion`, `InteractionResult`
5. [Mount / path prefix](MOUNT.md) — reverse-proxy subpaths and cookie `Path`
6. [CLI](CLI.md) — `hedron check`, `routes`, `new`, `build`

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

## Surfaces introduced in 0.19 (available on the 0.31 train)

These surfaces first shipped in the 0.19 phase and remain on the living **0.42.x**
train (includes the 0.9 authoring break, 0.10 live interaction, and later capability
phases through 0.25).

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
- [Accessibility (`hedron_core.a11y`)](A11Y.md) — introduced in 0.19; available on the living 0.42 train
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

- [Stability classifications](STABILITY.md) — compatibility catalog (current train 0.42.x)
- [Security types](SECURITY_TYPES.md) — `Secret` / `TrustedHtml` / `SafeUrl` / `SecurityPolicy`
- [CSRF composition (0.22)](CSRF_COMPOSITION.md) — strategies, header merge, `CsrfField`
- [Framework adapter contracts](ADAPTERS.md) — Supported FastAPI / Flask / Django
- [Job interaction contracts](JOBS.md) — durable `JobBackend` + polling Supported; SSE experimental

## Current train notes

- Accessibility engineering (`hedron_core.a11y`, Explorer `/a11y`, PE / landmarks /
  `Page(scripts=)`, automated `AT-019`) shipped on **0.19**; living train **0.42.x**
  (**Published**; last **v0.42.0**) — [A11Y API](A11Y.md),
  [What's new in 0.19](../guides/whats-new-0.19.md)
- Native Flask/Django depth, QuerySet DataSource, forms bridge, HDJ manifests/CSP inventory
  (introduced in 0.11; Supported on **0.42.x**)
- Advanced async / observability (`prepare`, audit sink, tracing, durable Redis job status)
  — Supported on **0.42.x**
- Capture UI ships in **0.15+** (no longer deferred); specialty extras in **0.16** are Experimental
- Optional `hedron-extras` curated toolkit ships in **0.16** (`hedron[extras]`) —
  narrative [What's new in 0.16](../guides/whats-new-0.16.md); package
  [CHANGELOG](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-extras/CHANGELOG.md)
- Model demos / inference workflows ship in **0.18** — [Inference API](INFERENCE.md),
  [What's new in 0.18](../guides/whats-new-0.18.md), optional Beta `hedron[gradio]`
