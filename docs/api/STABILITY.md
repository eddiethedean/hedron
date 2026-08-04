# Public stability classifications

**Status:** Phase 0.8 freeze baseline  
**Version:** `0.8.0`

This catalog freezes Hedron's public surface for the `v0.8.0` → `1.0.0rcN` train. Levels apply to
documented contracts; symbols not listed here are **internal** unless a later decision promotes them.

## Levels

| Level | Meaning |
|---|---|
| `stable` | Semver-stable after `v1.0.0`. Breaking changes require a major bump and migration notes. |
| `beta` | Intended for production use on the 0.8 train; may receive additive changes and documented fixes through RC. Breaking changes require changelog + diagnostic when feasible. |
| `experimental` | May change or be removed without a major bump. Must be labeled in docs and Explorer. |
| `internal` | Not a public promise. Private serializer nodes, private modules, and underscore-prefixed APIs. |
| `deferred` | Accepted design not advertised as Supported until a later decision (for example QuerySet DataSource, SSE). |

Package maturity classifiers (Beta/Alpha on PyPI) describe distribution readiness; the levels above
describe **API/artifact** promises.

## Artifact classes

| Class | Public promise | Format / pin |
|---|---|---|
| Python public API | `__all__` exports of first-party packages | Import paths and type signatures |
| CLI | `hedron` subcommands and documented JSON/SARIF shapes | Command set in [CLI.md](CLI.md) |
| Configuration | `[tool.hedron]` schema | [CONFIGURATION.md](../CONFIGURATION.md) |
| Diagnostics | `HED-*` codes + SARIF/JSON exporters | [DIAGNOSTICS.md](../DIAGNOSTICS.md) |
| Plugin protocol | `PluginMeta`, `PluginCapabilities`, `PluginContext`, entry point `hedron.plugins` | [PLUGINS.md](PLUGINS.md) |
| Registry metadata | Documented fields of `ComponentMeta`, `AddressableMeta`, `RouteMeta` | Public; private Explorer-only fields are internal |
| HDN | Source language (preferred `.hdx` / `template.hdx`; legacy `.hdn` still discovered) + `HDN_FORMAT_VERSION` / `RenderProgram` | Versioned compiled artifact |
| Build manifests | `BUILD` / `ASSET` / `CSS_SYMBOL` manifest format versions | Versioned; digest fields public |
| Rendered markup | Semantic structure and documented attributes for built-ins | Serializer implementation nodes are **internal** |
| HTMX interaction | Approved headers, status matrix, fragment regions, cache `Vary` | [INTERACTION.md](INTERACTION.md) |
| Framework adapters | Capability matrix rows labeled Supported / Experimental / Deferred | [ADAPTERS.md](ADAPTERS.md) |
| Browser assets | Bundled HTMX (and optional chart runtimes) exact pin + digest | [COMPATIBILITY.md](../COMPATIBILITY.md) |
| Test helpers | `hedron.testing` documented exports | [TESTING.md](TESTING.md) |

## Package export classifications (0.8 freeze)

### `hedron` (Beta distribution) — primarily `beta`

Facade re-exports of core built-ins, `Hedron`, `HedronRouter`, responses, interaction helpers,
security helpers, session state, cache decorators, CLI entry, and testing helpers are **beta**.
Lazy optional surfaces (`hedron[data]`, `hedron[charts]`, `hedron[auth]`, content helpers) inherit
the optional package level.

### `hedron-core` (Beta) — primarily `beta`

Component protocol, models, rendering (`render` → `RenderResult`), registry registration APIs,
security types (`Secret`, `TrustedHtml`, `SafeUrl`), HDN compile/load, themes, diagnostics, portable
adapter types, and interaction policy types are **beta**. Concrete HTML serializer node classes
remain **internal** (see [RENDERING.md](RENDERING.md)).

Documented but submodule-imported plugin types (`hedron_core.plugins.*`) are **beta**.

### `hedron-data` (Beta) — `beta`

`DataTable`, `DataEditor`, column helpers, and documented data-source protocols are **beta**.
AG Grid backend helpers remain **beta** with the same security/CSP contracts as 0.5–0.7.

### `hedron-charts` (Alpha distribution)

- `MatplotlibChart` / `MatplotlibAdapter` / static SVG path: **beta** API on an Alpha distribution.
- `PlotlyChart` / `AltairChart` full interactive runtimes: **experimental** until first-party pinned
  offline runtimes and browser evidence promote them.
- `LineChart` convenience: **beta**.

### `hedron-flask` / `hedron-django` (Beta) — `beta` Supported adapters

Public constructors, response helpers, route/view wrappers, and URL reversers are **beta**.
Capability rows marked Deferred (QuerySet DataSource) stay **deferred**.

### `hedron-explorer` (Beta) — `beta` for `explorer_router`; panel internals **internal**

### `hedron-sample-kit` (Alpha) — **experimental** sample plugin surface

## Deferred through the freeze

| Item | Decision | Destination |
|---|---|---|
| Django QuerySet DataSource | D-036 | post-1.0 |
| HTMX SSE live transport | D-037 | post-1.0 |
| Flask Blueprint / `init_app` ergonomic layer | research | post-1.0 |
| Django AppConfig convenience layer | research | post-1.0 |
| Navigation preload | HTMX audit | post-1.0 |

## Inventory check

`scripts/check_stability_inventory.py` verifies that every name in first-party package `__all__`
lists appears in this catalog's package sections or an explicit allowlist, and that STABILITY.md
exists. Gate ID: `FRZ-001`.
