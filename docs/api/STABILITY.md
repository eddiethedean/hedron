# Public stability classifications

**For adopters:** Hedron 1.0.7 is published on PyPI. Require `hedron>=1.0.0`. Treat the **stable**
tables below as the SemVer compatibility promise; everything
else is `beta` / `experimental` and may change on the documented schedule. Capability readiness
(Supported vs Experimental) lives on [What’s ready](../guides/whats-ready.md). Only
`hedron-core` and `hedron` are Stable packages in the repository; all other packages are
independent Beta satellites.

<details markdown>
<summary>Maintainer catalog metadata</summary>

**Status:** Verified and published **1.0.x** release (`v1.0.7`). `v0.67.0` remains the
immutable migration baseline.
Prior: 0.50 Explorer architecture; 0.49 FastAPI/Pydantic; 0.48 HTMX; 0.25 archetype; 0.24
live disposition; 0.23 stable-tier expansion; 0.22 CSRF / SecurityPolicy composition.
A **minimal `stable` tier** plus the **expanded 0.23 CRUD/admin facade** are listed below.
D-114/D-115/D-116/D-117 define the verified 1.0 one-way task and component-engine graph,
retain the public Web Component ABI, and supersede
D-038's no-calendar clause; the existing
D-053 / RFC-0056 and D-054 / RFC-0057 evidence and stable-tier obligations remain in force.
**Version:** `1.0.x` / catalog baseline
`0.8`+`0.10`+`0.11`+`0.12`+`0.13`+`0.14`+`0.15`+`0.16`+`0.17`+`0.18`+`0.19`+`0.20`+`0.21`+`0.22`+`0.23`+`0.24`+`0.25`+`0.26`+`0.27`+`0.28`+`0.50`+`0.51`

This catalog classifies Hedron's public surface beginning with `v0.8.0` and reflects the
`1.0.x` repository train. Levels apply to documented contracts; symbols not listed here are
**internal** unless a later phase explicitly promotes them.

</details>

## Levels

| Level | Meaning |
|---|---|
| `stable` | Compatibility-protected throughout `1.x`. An incompatible change requires the next major release plus an accepted decision, migration path, and deprecation evidence. |
| `beta` | Intended for production use; may receive additive changes and documented minor-phase revisions with changelog, migration, diagnostic, and evidence obligations. |
| `experimental` | May change or be removed without a major bump. Must be labeled in docs and Explorer. Prefer polling over experimental live transports in production. |
| `internal` | Not a public promise. Private serializer nodes, private modules, and underscore-prefixed APIs. |
| `deferred` | Accepted design not advertised as Supported until a later decision. |

Package maturity classifiers (Stable/Beta/Alpha) describe distribution readiness; the levels above
describe **API/artifact** promises. The stable 1.0 package boundary is `hedron-core` plus
`hedron`, `edron`, `hedron-data`, `hedron-charts`, and `hedron-maps`; host/tooling satellites keep
their independent Beta maturity.

## Minimal `stable` tier

The following contracts are **`stable`** (compatibility-protected throughout 1.x).
Everything else remains `beta` / `experimental` unless listed in the
[expanded 0.23 tier](#expanded-stable-tier-023) below. Satellite packages remain Beta even
when a capability is Supported. Maturity source of truth for product claims:
[What’s ready](../guides/whats-ready.md). Beginner import inventory:
[STABLE_FACADE.md](STABLE_FACADE.md). Full root `__all__` tier map:
[SYMBOL_TIERS.md](SYMBOL_TIERS.md).

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

## Expanded stable tier (0.23)

!!! note "Expanded stable tier from 0.23"

    These contracts are **`stable`** since **`v0.23.0`** (D-053 / RFC-0056) — the narrow
    Supported CRUD/admin happy path. Beginner import inventory:
    [STABLE_FACADE.md](STABLE_FACADE.md).
    Migration: additive promotions only — no removal from the minimal tier; any later
    boundary shrink requires an accepted decision and an intervening minor phase
    (same rule as other `stable` contracts).

Also inventoried on the Beginner facade (already minimal-stable): `Hedron`,
`HedronRouter`, `Page`, `Text`, `html`.

| Symbol / contract | Package / module |
|---|---|
| `Hedron.region`, `Hedron.fragment`; `FragmentRegion` (router `fragment_regions=`) | `hedron` |
| `swap`, `swap_oob`, `retarget`, `redirect_htmx` | `hedron` |
| `Poll` | `hedron` |
| `enqueue_durable`, `job_status_response` | `hedron.jobs` |
| `JobBackend`, `JobStatus`, `JobHandle`, `JobState`, `set_job_backend`, `get_job_backend` | `hedron_core.jobs` |
| `SecurityPolicy`, `SecurityPolicy.from_name`, profiles `development` / `standard` / `strict` | `hedron` |
| `SecurityHeadersPolicy` | `hedron` |
| `CsrfField`, `Form`, `Hx` | `hedron` |
| `DoubleSubmitCookieCsrf`, `SessionTokenCsrf`, `CsrfStrategy` | `hedron` |
| `Stack`, `TextInput`, `TextArea`, `SubmitButton`, `RefreshButton`, `FormErrors`, `FormField`, `Label` | `hedron` |
| `AppScenario` | `hedron.testing` |
| `assert_page_document`, `assert_fragment_body`, `assert_htmx_trigger`, `assert_hx_retarget`, `assert_oob_present`, `assert_hx_push_url`, `assert_hx_redirect`, `assert_hx_reswap` | `hedron.testing` |

### Out of 0.23

| Surface | Disposition |
|---|---|
| `job_status_sse_response` and other `hedron.experimental` live helpers | Remain **experimental**; 0.24 Accepted `polling_only` |
| Optional notebook / Gradio / MCP packages | Their later package graduations do not expand the 0.23 stable facade |
| `hedron[data]` / DataEditor, extras, OIDC product surface | Stay `beta` (Supported capability OK) |
| Dialog / Tabs / Pagination / Lazy, Map / media / capture, dashboards, inference | Stay `beta` |

## Artifact classes

| Class | Public promise | Format / pin |
|---|---|---|
| Python public API | `__all__` exports of first-party packages | Import paths and type signatures |
| CLI | Compatibility-protected core: `new`, `dev`, `build`, `check`, `routes`, `components` | [CLI.md](CLI.md); additional shipped commands are API `beta` |
| Configuration | `[tool.hedron]` schema | [CONFIGURATION.md](../CONFIGURATION.md) |
| Diagnostics | `HED-*` codes + SARIF/JSON exporters | [DIAGNOSTICS.md](https://github.com/eddiethedean/hedron/blob/main/docs/DIAGNOSTICS.md) |
| Plugin protocol | `PluginMeta`, `PluginCapabilities`, `PluginContext`, `PluginContribution`, `PluginDefinition`, entry point `hedron.plugins`, `load_plugins` | [PLUGINS.md](PLUGINS.md); loader lives in `hedron-core` |
| Registry metadata | Documented fields of `ComponentMeta`, `AddressableMeta`, `RouteMeta` | Public; private Explorer-only fields are internal |
| HDJ authoring | `.hdj` format v1, `hedron-jinja`, `TemplateSpec`, `HedronJinja` | Format frozen as v1; package is `beta`; trusted templates only |
| Build manifests | `BUILD` / `ASSET` / `CSS_SYMBOL` manifest format versions | Versioned; digest fields public |
| Rendered markup | Semantic structure and documented attributes for built-ins | Serializer implementation nodes are **internal** |
| HTMX interaction | Approved headers, status matrix, fragment regions (fail-closed), cache `Vary` | [INTERACTION.md](INTERACTION.md) |
| Framework adapters | Capability matrix rows labeled Supported / Experimental / Deferred | [ADAPTERS.md](ADAPTERS.md) |
| Browser assets | Bundled HTMX (and optional chart runtimes) exact pin + digest | [COMPATIBILITY.md](../COMPATIBILITY.md) |
| Test helpers | `hedron.testing` / `hedron_core.testing` documented exports | [TESTING.md](TESTING.md) |

## Package export classifications

### `hedron` (Stable distribution)

- **stable:** facade re-exports of the minimal stable tier above; `Hedron` / router / CSRF helpers;
  plus the [expanded 0.23 tier](#expanded-stable-tier-023): `region` / `fragment` / `swap` /
  `swap_oob` / `retarget` / `redirect_htmx` / `Poll` / `CsrfField` / `Form` / `Hx` /
  `SecurityPolicy` / `SecurityHeadersPolicy` / CSRF strategy types / beginner form chrome
  (`Stack`, `TextInput`, …); `hedron.jobs` helpers `enqueue_durable` / `job_status_response`;
  `hedron.testing` `AppScenario` + listed HTMX asserts.
- **beta:** remaining built-ins, session state, cache decorators, testing helpers not in the
  0.23 allowlist (Dialog/Tabs/Pagination/Lazy #24 markup asserts stay beta), CLI core commands,
  controls / surface chrome beyond the beginner set, media Range
  helpers, Map/GeoJSON, `BrowserContext` / `BrowserStorage`, Math, IFrame, optional identity
  helpers (`hedron.oidc`, session hardening), named connection registry, capture UI, shell
  primitives (`HtmxLink`/`NavLink`, `OobHost`/`AttrHost`, `AppShell`/`MainPanel`), public
  `render_interaction`, dashboard graph / patch facades, `InteractionRecorder`, and model-demo /
  inference / workflow facades re-exported from core. Phase 0.43 handle/update symbols are **beta**:
  historical `@app.refreshable`, `@app.command`, `FragmentHandle`, `BoundFragment`, `ActionHandle`, `Refresh`,
  `refresh`, `patches`, `FragmentHost`, `Patch`, `PatchSet`, `RefreshIntent`. Phase 0.44 type-driven
  authoring symbols are **beta**: `ViewParams`, `FormBody`, `Sensitive`, `InstanceKey`, `Control`,
  `Refreshes`, `Updates`, `OutcomeMap`, `case`, `CommandResult`, `RefreshableView`,
  `CommandHandler`, `TypeSchema`. Phase 0.45 catalog symbols are **beta**: `InteractionCatalog`,
  `CatalogEntry`, `InteractionManifest`, `PackageProjection`, `ProjectionProvider`,
  `Hedron.interactions`. Phase 0.46 package-workflow symbols are **beta**: `FeatureBundle`,
  `FeatureRequirement`, `FeatureConflictError`, `Hedron.include_feature`, `DataWorkspace`,
  `ChartInteraction`, `McpExposure`, `RemoteWorkflow`.
  In the 1.0 canonical surface, `@app.view`, `@app.action`, and `app.include` are the ordinary
  task paths; the machine-enumerated stable promise is maintained in
  `docs/acceptance/stable-inventory-100.toml`.
- **experimental:** live transports — import from `hedron.experimental`
  (`SseResponse`, `job_status_sse_response`, `sse_response`,
  `StreamingComponentResponse`, `stream_*`, `accept_page_session_channel`,
  `send_region_update`, `ALLOW_MISSING_ORIGIN`, navigation preload helpers).
  Prefer polling (0.24 Accepted `polling_only`). Root attribute access remains as a compat shim.
- Lazy optional surfaces (`hedron[data]`, `hedron[charts]`, `hedron[auth]`, content helpers) inherit
  the optional package level and are **not** part of the root stable facade.

### `hedron-core` (Stable)

- **stable:** symbols in the minimal stable tier; plus `JobBackend` / `JobStatus` /
  `JobHandle` / `JobState` / `set_job_backend` / `get_job_backend` (`hedron_core.jobs`);
  form/security types re-exported into the expanded 0.23 facade (`CsrfField`, `Form`, `Hx`,
  `SecurityPolicy`, strategies, beginner chrome as applicable).
- **beta:** component catalog, themes, diagnostics, registry, Celery/RQ job bridges, plugin loader,
  portable adapter capability types, `DashboardBinding` / `InteractionGraph` / `TriggerContext`,
  `PropertyPatch` / `CollectionPatch`, 0.43 `Patch` / `PatchSet` / `RefreshIntent` / `FragmentHost`
  (`hedron_core.updates` / `hedron_core.hosts`; not RFC-0041 property patches), shell builtins (`HtmxLink`/`NavLink`, `OobHost`/`AttrHost`,
  `AppShell`/`MainPanel`), Dialog/Tabs/Pagination/Lazy markup asserts, `InferenceInterface` /
  `ModelDemo` / `ExampleSet` / `PredictionFeedback`, presentation builtins, `InferencePolicy`,
  `InferenceWorkflow`, and `hedron_core.a11y` (`AccessibilityContract`, profile, scenarios,
  governance helpers, surface validators).
- Concrete HTML serializer node classes remain **internal**.

### `hedron-data` (Stable package) — `stable` API

- `DataTable` / `DataEditor`, columns, bounded source/query/result contracts, and normalization:
  **stable**
- Dask/Snowflake sources, AG Grid Community host, spreadsheet I/O, and collaboration helpers:
  **experimental**

### `hedron-charts` (Stable distribution; `>=1.0.0,<2.0` for coordinated 1.0 artifacts)

- `Chart` / `ChartSpec` / `ChartPlan`, compiler, and deterministic exports: **stable**.
- `MatplotlibChart` / static SVG: **stable** for the declared static scope.
- `PlotlyChart` / `AltairChart`: **experimental**.
- `LineChart` / `AreaChart` / `BarChart` / `ScatterChart`: **stable**.
- Optional vendor adapters + offline runtime pins: **experimental**.

Schema acceptance is broader than specialized host painting in the `hedron-charts 1.0.x` line; see the
[Chart API coverage matrix](CHART.md#compiler-contract-versus-current-host-coverage).

### `hedron-maps` (Stable package) — `stable` API

The bounded `MapSpec` / `MapPlan` grammar, first-party `Map` component, declared sources and
overlays, semantic fallback, exact-origin policy, deterministic compiler, and offline inventory
are stable. Leaflet/OpenLayers, arbitrary providers and projections, drawing, terrain, globe,
routing, geocoding, and offline-region download remain excluded rather than implicitly stable.

### `edron` (Stable package) — `stable` API

The root authoring surface (`App`, `Page`, `Container`, `Action`, `Fragment`, `Interaction`,
`Outcome`, and the documented decorators/helpers) is stable. Native internals, migration
helpers, operational backends, and optional adapter-specific surfaces remain non-stable.

### `hedron-posit` (Beta satellite) — `beta` Posit adapter

Install `hedron[posit]` / `hedron-posit>=1.0.2,<2.0`. Supported:
`HedronPosit`, pre-import Workbench launcher and resolved-state handoff,
`HEDRON_ROOT_PATH` export, wrap-once `workbenchify`, automatic URL and safe
response-header adaptation, Hedron-owned request-time cookie repair,
browser/durable URL separation, explicit-mount routing, topology diagnostics,
and ordinary local Uvicorn/generic-root-path parity. Posit Connect trusted-header
behavior remains Experimental. The generic implementation is provided by the
independent `fastapi-workbench>=1.0.2` package. The removed
`hedron-workbench` distribution and `hedron[workbench]` extra are not supported.

See [Posit Workbench](../guides/posit-workbench.md) and the
[current release](../guides/current-release.md).

### `hedron-flask` / `hedron-django` (Beta packages) — `beta` Supported adapters

Live helpers are **experimental** (polling remains Supported fallback).

### `hedron-explorer` (Beta package) — `beta` for `explorer_router`; panel internals **internal**

### `hedron-sample-kit` (Beta tooling-grade; `>=0.2.3,<0.3`) — `beta`

### `hedron-jinja` / HDJ (Beta package) — `beta` API; HDJ format v1 frozen

### `hedron-conformance` (Beta package) — `beta` API

Language-neutral fixture kit and runner. Cross-language runtimes that consume the kit remain
**experimental** until separately labeled Supported.

### `hedron-extras` (Beta package) — `beta` composition/workbenches; specialty **experimental**

Optional curated toolkit (`hedron[extras]`). Composition UI, DataExplorer, JSONEditor,
image tools, calendar/signature/typeahead, and display recipes are **beta**.
CodeEditor and the browser-Python sandbox are **experimental** (align with
[What’s ready](../guides/whats-ready.md) and the extras package page).
`TerminalView`, joystick, and device-bridge surfaces are **experimental** and fail closed without
explicit policy (RFC-0038). Native desktop shell is packaging documentation only.

### `hedron-notebook` (Beta tooling-grade — introduced in phase 0.17)

Optional server-side notebook preview helper ([RFC-0042](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0042-NOTEBOOK-PREVIEW.md)).
Distinct from the 0.16 browser-Python sandbox. D-015 separate distribution; package maturity
Beta and API `beta` for the localhost-only Supported tooling scope. It is not a Supported
production server.

### `hedron-mcp` (Beta — phase 0.32 Supported inventory)

Optional deny-by-default MCP Streamable HTTP projection
([RFC-0043](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0043-MCP-PROJECTION.md)
product contract; [RFC-0065](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0065-PRODUCTION-GRADE-MCP.md)
graduation). D-015 separate distribution; maturity Beta / API `beta` for the declared Supported
inventory. The coordinated 1.0 artifact is `hedron-mcp>=0.2.4,<0.3`. Disabled and empty by
default. Mutating tools remain
Experimental (`allow_mutations=True`).

### `hedron-gradio` (Beta — phase 0.34 Supported inventory)

Optional Gradio client interoperability
([RFC-0049](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0049-GRADIO-ADAPTER.md)
product contract; RFC-0067 graduation). D-015 / D-049 separate distribution; maturity Beta /
API `beta` for declared allowlisted client interoperability. The coordinated 1.0 artifact is
`hedron-gradio>=0.2.3,<0.3`. Discover is empty while disabled;
absence adds no core cost. Vendor extensions and UI auto-composition remain Experimental, and
the package does not embed Gradio's UI runtime.

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

### Phase 0.55 workflow surfaces (`beta`)

| Contract | Package | Level | Notes |
|---|---|---|---|
| `MasterDetail` | `hedron-core` | `beta` | LAYOUT-055 |
| `Capability` / `CapabilityProvider` / `enforce_capability` | `hedron` | `beta` | CAP-055; FastAPI action enforcement |
| `IdempotencyPolicy` / `MemoryReplayStore` | `hedron` | `beta` | REPLAY-055; FastAPI action enforcement |
| `UploadField` / `UploadHandle` / `materialize_upload` | `hedron` | `beta` | UPLOAD-055; buffered |
| `NonceContext` / `compose_csp` / `ingest_csp_report` | `hedron` | `beta` | CSP-055 helpers (opt-in) |
| `WorkflowManifest` / `hedron upgrade-report` | `hedron` | `beta` | CONTRACT/UPGRADE-055 |

### `hedron-native` (Beta, versioned independently as `0.1.x`) — Supported optional accel

Optional Rust HTML-escape acceleration with pure-Python fallback. Absence never changes public
semantics (D-048 / D-056). Runtime disable: `HEDRON_NATIVE_DISABLE`.

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

## Live transports (0.10+) — experimental; polling Supported (`polling_only`)

| Item | Decision | Notes |
|---|---|---|
| HTMX SSE live observation | D-037 / D-044 | **experimental**; polling Supported fallback |
| Navigation preload | D-044 | **experimental**; opt-in |
| Focused streaming / page-session WebSocket | D-044 | **experimental** on FastAPI |
| Dialog / ChatMessage / ChatInput | D-045 | **beta** (history application-owned) |

Phase **0.24** Accepted disposition **`polling_only`** (D-053 /
[RFC-0056](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0056-PRODUCTION-QUALITY.md)):
polling is the Supported production story; live helpers remain experimental.
`prove_ops` was not chosen. Contract: [LIVE_DISPOSITION.md](LIVE_DISPOSITION.md).
Prefer polling in production.

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
