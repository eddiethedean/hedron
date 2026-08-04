# Public stability classifications

**Status:** Phase 0.10 live interaction (**published** `v0.10.1`)
**Version:** `0.10.1`

This catalog classifies Hedron's public surface beginning with `v0.8.0` and reflects the published
`v0.10.1` train. Levels apply to documented contracts; symbols not listed here are **internal**
unless a later phase explicitly promotes them.

## Levels

| Level | Meaning |
|---|---|
| `stable` | Compatibility-protected across `0.x` phases. Incompatible change requires an accepted decision, migration path, deprecation evidence, and at least one intervening minor phase. |
| `beta` | Intended for production use; may receive additive changes and documented minor-phase revisions with changelog, migration, diagnostic, and evidence obligations. |
| `experimental` | May change or be removed without a major bump. Must be labeled in docs and Explorer. |
| `internal` | Not a public promise. Private serializer nodes, private modules, and underscore-prefixed APIs. |
| `deferred` | Accepted design not advertised as Supported until a later decision (for example QuerySet DataSource, capture UI). |

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
| HDJ authoring | `.hdj` format v1, `hedron-jinja`, `TemplateSpec`, `HedronJinja` | Format and profile expansions are versioned; package is `beta`; trusted templates only |
| Build manifests | `BUILD` / `ASSET` / `CSS_SYMBOL` manifest format versions | Versioned; digest fields public |
| Rendered markup | Semantic structure and documented attributes for built-ins | Serializer implementation nodes are **internal** |
| HTMX interaction | Approved headers, status matrix, fragment regions, cache `Vary` | [INTERACTION.md](INTERACTION.md) |
| Framework adapters | Capability matrix rows labeled Supported / Experimental / Deferred | [ADAPTERS.md](ADAPTERS.md) |
| Browser assets | Bundled HTMX (and optional chart runtimes) exact pin + digest | [COMPATIBILITY.md](../COMPATIBILITY.md) |
| Test helpers | `hedron.testing` documented exports | [TESTING.md](TESTING.md) |

## Package export classifications (0.10 baseline)

### `hedron` (Beta distribution) — primarily `beta`

Facade re-exports of core built-ins, `Hedron`, `HedronRouter`, responses, interaction helpers,
security helpers, session state, cache decorators, CLI entry, testing helpers, and 0.10 live
helpers (`SseResponse`, `job_status_sse_response`, `StreamingComponentResponse`,
`accept_page_session_channel`, `send_region_update`, `Dialog`, `ChatMessage`, `ChatInput`,
preload helpers) are **beta**.
Lazy optional surfaces (`hedron[data]`, `hedron[charts]`, `hedron[auth]`, content helpers) inherit
the optional package level.

### `hedron-core` (Beta) — primarily `beta`

Component protocol, models, rendering (`render` → `RenderResult`), registry registration APIs,
security types (`Secret`, `TrustedHtml`, `SafeUrl`), themes, diagnostics, portable adapter types,
and interaction policy types are **beta**. Concrete HTML serializer node classes remain
**internal** (see [RENDERING.md](RENDERING.md)).

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

### `hedron-jinja` / HDJ (Beta) — `beta`

`TemplateSpec`, `TemplateSource`, `HedronJinja`, and `HedronJinjaExtension` are **beta**. Templates
are trusted application code. Standard HTML/CSS/JS/Jinja/HTMX source is part of the target surface;
hostile-template sandboxing is not a supported capability.

## Deferred destinations

| Item | Decision | Destination |
|---|---|---|
| Django QuerySet DataSource | D-036 / D-041 | 0.11 |
| Flask Blueprint / `init_app` ergonomic layer | D-041 | 0.11 |
| Django AppConfig convenience layer | D-041 | 0.11 |
| First-party camera/microphone/Audio/Video capture UI | D-045 | 0.15 |

## Supported in 0.10 (live)

| Item | Decision | Notes |
|---|---|---|
| HTMX SSE live observation | D-037 / D-044 | Polling remains Supported fallback |
| Navigation preload | D-044 | Opt-in; disabled by default until policy enabled |
| Focused streaming / page-session WebSocket | D-044 | FastAPI Supported host |
| Dialog / ChatMessage / ChatInput | D-045 | History application-owned |

## Removed surfaces

HDN source, discovery, compiler/evaluator/formatter/runtime, `RenderProgram`, format constants,
artifacts, and compile/load/run APIs were removed in 0.9 under D-041. They have no compatibility
package or runtime flag.

## Inventory check

`scripts/check_stability_inventory.py` verifies that every name in first-party package `__all__`
lists appears in this catalog's package sections or an explicit allowlist, and that STABILITY.md
exists. Gate ID: `FRZ-001`.
