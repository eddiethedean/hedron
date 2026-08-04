# Public API

Hedron documentation separates **callable APIs that ship in this release** from
**Accepted design contracts** that are not importable yet.

!!! tip "`hedron` vs `hedron_core`"

    Day-to-day apps import from `hedron` (FastAPI facade, router, responses, testing).
    Advanced typing and rendering primitives such as `NodeLike`, `RenderMode`, and
    `get_registry` live in `hedron_core`. Prefer `hedron` re-exports when available.

**Stability:** Phase 0.10 continues the public classifications in [STABILITY.md](STABILITY.md)
(`beta` | `experimental` | `internal` | `deferred`). Package maturity (Beta/Alpha) is separate
from API level. Upgrade notes: [upgrade guide](../guides/upgrade.md).

!!! note "Contracts vs full reference"

    API pages are hand-maintained contracts (not yet mkdocstrings autodoc). Adopter-critical
    pages ([Hedron](HEDRON.md), [Router](ROUTER.md), [Action](ACTION.md),
    [Interaction](INTERACTION.md), [Models](MODELS.md), [Responses](RESPONSES.md),
    [Security types](SECURITY_TYPES.md), [Auto](AUTO.md), [SSE](SSE.md),
    [Streaming](STREAMING.md)) include constructor / field tables, returns, errors, and
    examples. Prefer those plus the guides when learning; read source for unmarked
    internals. Human error index: [Error codes](../guides/error-codes.md).

## Shipped through 0.10

These surfaces are implemented in the published **0.10.0** train (includes the 0.9 authoring break
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
