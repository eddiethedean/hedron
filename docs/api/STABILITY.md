# Public stability classifications

**Status:** Phase 0.11 Flask/Django depth (**published** `v0.11.0`); readiness track toward a future
stable tier (D-038: no calendar `1.0` scheduled).
**Version:** `0.11.0` / catalog baseline `0.8`+`0.10`+`0.11`

This catalog classifies Hedron's public surface beginning with `v0.8.0` and reflects the published
`v0.11.0` train. Levels apply to documented contracts; symbols not listed here are **internal**
unless a later phase explicitly promotes them.

## Levels

| Level | Meaning |
|---|---|
| `stable` | Compatibility-protected across `0.x` phases. Incompatible change requires an accepted decision, migration path, deprecation evidence, and at least one intervening minor phase. |
| `beta` | Intended for production use; may receive additive changes and documented minor-phase revisions with changelog, migration, diagnostic, and evidence obligations. |
| `experimental` | May change or be removed without a major bump. Must be labeled in docs and Explorer. Prefer polling over experimental live transports in production. |
| `internal` | Not a public promise. Private serializer nodes, private modules, and underscore-prefixed APIs. |
| `deferred` | Accepted design not advertised as Supported until a later decision (for example capture UI). |

Package maturity classifiers (Beta/Alpha on PyPI) describe distribution readiness; the levels above
describe **API/artifact** promises.

## Minimal `stable` tier (0.11.1 readiness)

The following contracts are promoted to **`stable`** (compatibility-protected on the 0.x train).
Everything else remains `beta` / `experimental` unless listed below.

| Symbol / contract | Package |
|---|---|
| `render`, `RenderResult`, `RenderMode`, `RenderContext` | `hedron-core` |
| `Component`, `Page`, `Text`, `html` | `hedron-core` |
| `Model`, `Props`, `FormModel`, `Field` | `hedron-core` |
| `Secret`, `TrustedHtml`, `SafeUrl`, `UrlPurpose` | `hedron-core` |
| `InteractionResult`, `InteractionPolicy`, `FragmentRegion`, `OobUpdate` | `hedron-core` / `hedron` |
| `authorize_htmx_target`, `authorize_oob_update`, approved HTMX response headers | `hedron-core` |
| `Hedron`, `HedronRouter`, `HedronRoute` | `hedron` |
| `csrf_token_for_request`, CSRF cookie/header/form field names on `SecurityPolicy` | `hedron` |
| `redirect_local`, `redirect_external` | `hedron` |
| Adapter `respond` / `component_response` / `interaction_response` helpers | `hedron-flask`, `hedron-django` |
| Portable harness: `fastapi_fixture`, `flask_fixture`, `django_fixture`, `assert_page_document`, `assert_fragment_body`, `assert_htmx_trigger` | `hedron_core.testing.adapters` (re-exported as `hedron.testing.adapters`) |

Optional extras (`hedron[data]`, `hedron[charts]`, `hedron[auth]`, content helpers) are **not**
stable via the root facade — import them from their packages.

## Artifact classes

| Class | Public promise | Format / pin |
|---|---|---|
| Python public API | `__all__` exports of first-party packages | Import paths and type signatures |
| CLI | Core subcommands `new`, `dev`, `build`, `check`, `routes`, `components` | [CLI.md](CLI.md); graph/audit/eject are experimental |
| Configuration | `[tool.hedron]` schema | [CONFIGURATION.md](../CONFIGURATION.md) |
| Diagnostics | `HED-*` codes + SARIF/JSON exporters | [DIAGNOSTICS.md](https://github.com/eddiethedean/hedron/blob/main/docs/DIAGNOSTICS.md) |
| Plugin protocol | `PluginMeta`, `PluginCapabilities`, `PluginContext`, entry point `hedron.plugins`, `load_plugins` | [PLUGINS.md](PLUGINS.md); loader lives in `hedron-core` |
| Registry metadata | Documented fields of `ComponentMeta`, `AddressableMeta`, `RouteMeta` | Public; private Explorer-only fields are internal |
| HDJ authoring | `.hdj` format v1, `hedron-jinja`, `TemplateSpec`, `HedronJinja` | Format frozen as v1; package is `beta`; trusted templates only |
| Build manifests | `BUILD` / `ASSET` / `CSS_SYMBOL` manifest format versions | Versioned; digest fields public |
| Rendered markup | Semantic structure and documented attributes for built-ins | Serializer implementation nodes are **internal** |
| HTMX interaction | Approved headers, status matrix, fragment regions (fail-closed), cache `Vary` | [INTERACTION.md](INTERACTION.md) |
| Framework adapters | Capability matrix rows labeled Supported / Experimental / Deferred | [ADAPTERS.md](ADAPTERS.md) |
| Browser assets | Bundled HTMX (and optional chart runtimes) exact pin + digest | [COMPATIBILITY.md](../COMPATIBILITY.md) |
| Test helpers | `hedron.testing` / `hedron_core.testing` documented exports | [TESTING.md](TESTING.md) |

## Package export classifications

### `hedron` (Beta distribution)

- **stable:** facade re-exports of the minimal stable tier above; `Hedron` / router / CSRF helpers.
- **beta:** remaining built-ins, session state, cache decorators, testing helpers, CLI core commands.
- **experimental:** live transports — import from `hedron.experimental`
  (`SseResponse`, `job_status_sse_response`, `sse_response`,
  `StreamingComponentResponse`, `stream_*`, `accept_page_session_channel`,
  `send_region_update`, `ALLOW_MISSING_ORIGIN`, navigation preload helpers).
  Prefer polling until ops gates close. Root attribute access remains as a compat shim.
- Lazy optional surfaces (`hedron[data]`, `hedron[charts]`, `hedron[auth]`, content helpers) inherit
  the optional package level and are **not** part of the root stable facade.

### `hedron-core` (Beta)

- **stable:** symbols in the minimal stable tier.
- **beta:** component catalog, themes, diagnostics, registry, jobs protocols, plugin loader,
  portable adapter capability types.
- Concrete HTML serializer node classes remain **internal**.

### `hedron-data` (Beta) — `beta`

### `hedron-charts` (Alpha distribution, versioned independently as `0.1.x`)

- `MatplotlibChart` / static SVG: **beta** API on Alpha distribution.
- `PlotlyChart` / `AltairChart`: **experimental**.
- `LineChart`: **beta**.

### `hedron-flask` / `hedron-django` (Beta) — `beta` Supported adapters

Live helpers are **experimental** (polling remains Supported fallback).

### `hedron-explorer` (Beta) — `beta` for `explorer_router`; panel internals **internal**

### `hedron-sample-kit` (Alpha, versioned independently as `0.1.x`) — **experimental**

### `hedron-jinja` / HDJ (Beta) — `beta`; HDJ format v1 frozen

## Deferred destinations

| Item | Decision | Destination |
|---|---|---|
| Django QuerySet DataSource | D-046 | Supported in 0.11 |
| Flask Blueprint / `init_app` ergonomic layer | D-041 / D-046 | Supported in 0.11 |
| Django AppConfig convenience layer | D-041 / D-046 | Supported in 0.11 |
| Celery / RQ `JobBackend` bridges | D-046 | Supported extras in 0.11 |
| Flask / Django live helpers | D-044 / D-046 | Experimental API; polling Supported |
| First-party camera/microphone/Audio/Video capture UI | D-045 | 0.15 |

## Live transports (0.10+) — experimental until ops gates close

| Item | Decision | Notes |
|---|---|---|
| HTMX SSE live observation | D-037 / D-044 | **experimental**; polling Supported fallback |
| Navigation preload | D-044 | **experimental**; opt-in |
| Focused streaming / page-session WebSocket | D-044 | **experimental** on FastAPI |
| Dialog / ChatMessage / ChatInput | D-045 | **beta** (history application-owned) |

Exports: `SseResponse`, `job_status_sse_response`, `StreamingComponentResponse`,
`accept_page_session_channel`, `send_region_update`, `Dialog`, `ChatMessage`, `ChatInput`.

## Removed surfaces

HDN source, discovery, compiler/evaluator/formatter/runtime, `RenderProgram`, format constants,
artifacts, and compile/load/run APIs were removed in 0.9 under D-041. They have no compatibility
package or runtime flag.

## Inventory check

`scripts/check_stability_inventory.py` verifies that every name in first-party package `__all__`
lists appears in this catalog's package sections or an explicit allowlist, and that STABILITY.md
exists. Gate ID: `FRZ-001`.
