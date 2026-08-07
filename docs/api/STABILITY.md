# Public stability classifications

**For adopters:** Pin `hedron>=0.20.0,<0.21`. Treat the small **stable** table below as
the compatibility promise; everything else is `beta` / `experimental` and may change on
`0.x`. Capability readiness (Supported vs Experimental) lives on
[What’s ready](../guides/whats-ready.md). Package maturity on PyPI remains **Beta**.

<details markdown>
<summary>Maintainer catalog metadata</summary>

**Status:** Phase 0.20 production security floor (**Ready to cut / Implemented on `main`**
as `0.20.0`; last published PyPI/git = `v0.19.0`).
A **minimal `stable` tier** is already listed below (D-038: no calendar `1.0` scheduled).
**Version:** `0.20.0` / catalog baseline
`0.8`+`0.10`+`0.11`+`0.12`+`0.13`+`0.14`+`0.15`+`0.16`+`0.17`+`0.18`+`0.19`+`0.20`

This catalog classifies Hedron's public surface beginning with `v0.8.0` and reflects the
`0.20.0` train on `main`. Levels apply to documented contracts; symbols not listed here are
**internal** unless a later phase explicitly promotes them.

</details>

## Levels

| Level | Meaning |
|---|---|
| `stable` | Compatibility-protected across `0.x` phases. Incompatible change requires an accepted decision, migration path, deprecation evidence, and at least one intervening minor phase. |
| `beta` | Intended for production use; may receive additive changes and documented minor-phase revisions with changelog, migration, diagnostic, and evidence obligations. |
| `experimental` | May change or be removed without a major bump. Must be labeled in docs and Explorer. Prefer polling over experimental live transports in production. |
| `internal` | Not a public promise. Private serializer nodes, private modules, and underscore-prefixed APIs. |
| `deferred` | Accepted design not advertised as Supported until a later decision. |

Package maturity classifiers (Beta/Alpha on PyPI) describe distribution readiness; the levels above
describe **API/artifact** promises.

## Minimal `stable` tier

The following contracts are **`stable`** (compatibility-protected on the 0.x train).
Everything else remains `beta` / `experimental` unless listed below. Package maturity on
PyPI remains **Beta** — pin versions. Maturity source of truth for product claims:
[What’s ready](../guides/whats-ready.md).

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

Optional extras (`hedron[data]`, `hedron[charts]`, `hedron[extras]`, `hedron[auth]`, content helpers) are **not**
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
- **beta:** remaining built-ins, session state, cache decorators, testing helpers
  (`AppScenario`, HTMX asserts #22–#26, Dialog/Tabs/Pagination/Lazy #24), CLI core commands,
  `region` / `@fragment` / `swap` ergonomics, typed controls / surface chrome, media Range
  helpers, Map/GeoJSON, `BrowserContext` / `BrowserStorage`, Math, IFrame, optional identity
  helpers (`hedron.oidc`, session hardening), named connection registry, capture UI, shell
  primitives (`HtmxLink`/`NavLink`, `OobHost`/`AttrHost`, `AppShell`/`MainPanel`), public
  `render_interaction`, dashboard graph / patch facades, `InteractionRecorder`, and model-demo /
  inference / workflow facades re-exported from core.
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
  portable adapter capability types, `DashboardBinding` / `InteractionGraph` / `TriggerContext`,
  `PropertyPatch` / `CollectionPatch`, shell builtins (`HtmxLink`/`NavLink`, `OobHost`/`AttrHost`,
  `AppShell`/`MainPanel`), Dialog/Tabs/Pagination/Lazy markup asserts, `InferenceInterface` /
  `ModelDemo` / `ExampleSet` / `PredictionFeedback`, presentation builtins, `InferencePolicy`,
  `InferenceWorkflow`, and `hedron_core.a11y` (`AccessibilityContract`, profile, scenarios,
  governance helpers, surface validators).
- Concrete HTML serializer node classes remain **internal**.

### `hedron-data` (Beta) — `beta`

- `DataTable` / `DataEditor`, column catalog, saved views, `TransformPlan`, typed grid events: **beta**
- Dask/Snowflake sources, AG Grid Community host: **beta**
- Spreadsheet I/O / collab helpers: **beta**

### `hedron-charts` (Alpha distribution, versioned independently as `0.1.x`)

- `MatplotlibChart` / static SVG: **beta** API on Alpha distribution.
- `PlotlyChart` / `AltairChart`: **experimental**.
- `LineChart` / `AreaChart` / `BarChart` / `ScatterChart`: **beta**.
- Optional adapters + offline runtime pins: **experimental** (Alpha distribution).

### `hedron-flask` / `hedron-django` (Beta) — `beta` Supported adapters

Live helpers are **experimental** (polling remains Supported fallback).

### `hedron-explorer` (Beta) — `beta` for `explorer_router`; panel internals **internal**

### `hedron-sample-kit` (Alpha, versioned independently as `0.1.x`) — **experimental**

### `hedron-jinja` / HDJ (Beta) — `beta`; HDJ format v1 frozen

### `hedron-conformance` (Beta) — `beta`

Language-neutral fixture kit and runner. Cross-language runtimes that consume the kit remain
**experimental** until separately labeled Supported.

### `hedron-extras` (Beta) — `beta` composition/workbenches; specialty **experimental**

Optional curated toolkit (`hedron[extras]`). Composition UI, DataExplorer, JSONEditor, CodeEditor,
image tools, calendar/signature/typeahead, display recipes, and browser-Python sandbox are **beta**.
`TerminalView`, joystick, and device-bridge surfaces are **experimental** and fail closed without
explicit policy (RFC-0038). Native desktop shell is packaging documentation only.

### `hedron-notebook` (Alpha / experimental — phase 0.17)

Optional server-side notebook preview helper ([RFC-0042](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0042-NOTEBOOK-PREVIEW.md)).
Distinct from the 0.16 browser-Python sandbox. D-015 separate distribution; maturity Alpha /
API `experimental`. Localhost-oriented; not Supported production.

### `hedron-mcp` (Alpha / experimental — phase 0.17)

Optional deny-by-default MCP Streamable HTTP projection
([RFC-0043](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0043-MCP-PROJECTION.md)).
D-015 separate distribution; maturity Alpha / API `experimental`. Disabled and empty by default;
not Supported production tools.

### `hedron-gradio` (Alpha / experimental — phase 0.18)

Optional Gradio client interoperability
([RFC-0049](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0049-GRADIO-ADAPTER.md)).
D-015 / D-049 separate distribution; maturity Alpha / API `experimental`. Discover is empty while
disabled; absence adds no core cost. Not Supported production parity with Gradio's UI runtime.

### Phase 0.17 surfaces on existing packages (shipped)

| Symbol / contract | Package | Level | RFC / gate |
|---|---|---|---|
| `DashboardBinding` / `InteractionGraph` / `TriggerContext` | `hedron-core` / `hedron` | `beta` | RFC-0040 / `GRAPH-017` |
| `PropertyPatch` / `CollectionPatch` / collection selectors | `hedron-core` | `beta` | RFC-0041 / `PATCH-017` |
| `HtmxLink` / `NavLink`, `OobHost` / `AttrHost`, `AppShell` / `MainPanel` | `hedron` / `hedron-core` | `beta` | RFC-0044 / `SHELL-017` |
| Public `render_interaction` (InteractionResult → Response) | `hedron` | `beta` | RFC-0044 / `SHELL-017` |
| Dialog / Tabs / Pagination / Lazy markup asserts | `hedron-core` / `hedron.testing` | `beta` | `ASSERT-017` / #24 |

### Phase 0.18 surfaces on existing packages (shipped)

| Symbol / contract | Package | Level | RFC / gate |
|---|---|---|---|
| `InferenceInterface` / `ModelDemo` / `ActionRegistry` | `hedron-core` / `hedron` | `beta` | RFC-0045 / `DEMO-018` |
| `ExampleSet` / presentation builtins / `PredictionFeedback` | `hedron-core` | `beta` | RFC-0046 |
| `InferencePolicy` / `ModelDemoScenario` | `hedron-core` | `beta` | RFC-0047 |
| `InteractionRecorder` | `hedron` | `beta` | RFC-0048 / `RECORD-018` |
| `InferenceWorkflow` + structured editor | `hedron-core` | `beta` | RFC-0050 / `WORKFLOW-018` |

### Phase 0.19 surfaces on existing packages (shipped)

| Symbol / contract | Package | Level | RFC / gate |
|---|---|---|---|
| `AccessibilityContract` / contract catalog | `hedron-core` (`hedron_core.a11y`) | `beta` | RFC-0051 / `CONTRACT-019` |
| Standards profile / claim boundaries | `hedron-core` (`hedron_core.a11y`) | `beta` | RFC-0023 / `PROFILE-019` |
| `AccessibilityScenario` / axe → SARIF helpers | `hedron-core` / `hedron.testing` | `beta` | RFC-0052 / `TEST-019` |
| `LandmarkProps` / landmark builtins as real types | `hedron-core` | `beta` | `LANDMARK-019` |
| `Page(scripts=[SafeUrl…])` allowlisted PE scripts | `hedron-core` | `beta` | `SCRIPT-019` |
| Evidence inventory / statement / waiver governance | `hedron-core` (`hedron_core.a11y`) | `beta` | RFC-0055 / `GOVERN-019` |

### `hedron-native` (Alpha, versioned independently as `0.1.x`) — **experimental** accel

Optional Rust HTML-escape acceleration with pure-Python fallback. Absence never changes public
semantics (D-048).

## Deferred destinations

Historical notes (resolved in 0.11+): these items were once deferred destinations; they are
**Supported in 0.11** (or Experimental for live helpers) on the current line. Kept here so
older upgrade notes remain navigable.

| Item | Decision | Status |
|---|---|---|
| Django QuerySet DataSource | D-046 | **Supported** since 0.11 |
| Flask Blueprint / `init_app` ergonomic layer | D-041 / D-046 | **Supported** since 0.11 |
| Django AppConfig convenience layer | D-041 / D-046 | **Supported** since 0.11 |
| Celery / RQ `JobBackend` bridges | D-046 | **Supported** optional bridges (shared Redis for multi-worker) |
| Flask / Django live helpers | D-044 / D-046 | **Experimental** API; polling **Supported** |
| Camera / microphone capture UI | D-045 | **Supported** since 0.15 (with policy limits) |

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
