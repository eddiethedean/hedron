---
status: verified
---

# Edron 0.1 capability inventories

**Status:** Historical 0.1 design inventory, verified against published Edron `1.0.0`<br>
**Current release:** Edron `1.0.0`; Hedron `>=1.0.0,<1.1`; published on PyPI<br>
**Historical 0.1 target metadata:** Edron `0.1.0`; compatible Hedron train and release phase unassigned<br>
**Roadmap:** [Edron `0.x` release roadmap](../EDRON_ROADMAP.md)<br>
**Public API:** [Edron 0.1 public API](../api/EDRON.md)<br>
**State and interaction:** [Edron 0.1 state and interaction](../api/EDRON_STATE_INTERACTION.md)<br>
**Packaging:** [Edron 0.1 packaging](../api/EDRON_PACKAGING.md)<br>
**Implementation:** [Edron 0.1 implementation specification](EDRON_001.md)<br>
**Acceptance:** [Edron 0.1 acceptance packet](../acceptance/EDRON_001.md)<br>
**Architecture:** [RFC-0094](../rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md)<br>
**Fixtures:** [Edron golden applications](EDRON_GOLDEN_APPS.md)

These inventories record the original Edron 0.1 capability set used to authorize and trace the
implemented facade. They answer five separate questions that a flat feature checklist would conflate:

1. What does a beginner get from plain `pip install edron`?
2. What Edron vocabulary is planned, and what exact native authority does it lower to?
3. What optional third-party integrations activate from installed compatible dependencies?
4. What full-power Hedron paths remain directly available without an Edron wrapper?
5. Which promises are blocked on reusable upstream Hedron work or deliberately deferred?

This document is a traceability inventory, not a second API, package, or maturity authority. The
normative signatures and behavior live in the companion contracts. If an inventory row and a
contract disagree, release stops until both are reconciled.

## Inventory language

### Disposition

| Tag | Meaning |
|---|---|
| `Facade` | Edron-owned authoring vocabulary/buffering/source mapping over native behavior |
| `Native` | Exact native Hedron object/protocol is used directly or by identity |
| `Package` | Installation, capability detection, diagnostics, or tooling composition owned by Edron packaging |
| `Upstream` | A reusable Hedron contract must be identified, refined, or added before the Edron surface ships |
| `Application` | The application supplies domain/service/backend/security behavior; Edron must not infer it |
| `Deferred` | Intentionally absent from the Edron 0.1 beginner surface |

Several tags may apply to one row. `Facade + Native`, for example, means Edron owns only the small
Python spelling while the exact output/route/interaction authority is native.

### Native readiness

| Status | Meaning |
|---|---|
| `Ready` | A documented public native authority is identified; release still requires conformance evidence |
| `Verify` | The baseline appears to contain the building blocks, but exact signature/lifecycle/parity evidence is not frozen |
| `Enable` | A separate Hedron enablement item is required; the Edron capability is blocked |
| `N/A` | Packaging or pure facade behavior has no missing native primitive |
| `Deferred` | No 0.1 implementation is planned |

The original disposition records remain historical traceability. Current implementation and
maturity are governed by the 0.9 public API, roadmap, package metadata, and acceptance packet;
`Ready` in this inventory never promotes a native Experimental object to Supported.

### Installation class

| Class | Meaning |
|---|---|
| `Base` | Available after plain `pip install edron` |
| `Optional` | Requires compatible directly installed third-party distributions; an Edron extra may be a shortcut |
| `Native base` | Owning Hedron distribution is installed by Edron, but the advanced API is imported from its native package |
| `Application` | Supplied/configured by the application or deployment |
| `Tooling` | Development/static tooling shipped in base; trusted-import behavior is explicit |

## Inventory 0: beginner root exports

This table accounts for the complete root inventory frozen by the public API. It records ownership;
the detailed behavior is expanded in the capability inventories below.

| Public exports | Kind | Install | Disposition / detailed rows |
|---|---|---|---|
| `App` | facade/ASGI class | Base | Facade + Native; `APP-001`–`APP-010` |
| `Page` | request-scoped controller base | Base | Facade; `OUT-001` and all Page capability families |
| `Container`, `FilterScope` | request-local values | Base | Facade + Native; `OUT-002`–`OUT-004`, `FILTER-004` |
| `fragment`, `Fragment`, `BoundFragment` | decorator/descriptors | Base | Facade + Upstream; `FRAG-001`–`FRAG-004` |
| `action`, `Action`, `BoundAction` | decorator/descriptors | Base | Facade + Upstream; `ACT-001`–`ACT-006` |
| `Outcome`, `success`, `refresh` | native result alias/factories | Base | Native + Facade; `RESULT-001`–`RESULT-003` |
| `dependency`, `Dependency` | request dependency descriptor | Base | Facade + Upstream; `DEP-001`, `DEP-002` |
| `cache_data`, `CachedFunction` | cache decorator/protocol | Base | Facade + Native; `CACHE-001` |
| `Confirm` | immutable confirmation request | Base | Facade + Upstream; `CONTROL-002` |
| `download`, `Download` | opaque download factory/value | Base | Facade + Native + Application; `DL-001`, `DL-002` |
| `JobFlow` | job composition facade | Base + Application | Facade + Upstream; `JOB-001`–`JOB-003` |
| `JobBackend`, `JobScope` | identity re-exports | Base | Native; `hedron_core.jobs.JobBackend` and `hedron.JobScope` |
| `theme` | native design-system constructor facade | Base | Facade + Native + Upstream; `STYLE-002` |
| `Color`, `DesignSystem`, `StyleRecipe` | identity re-exports | Base | Native; `STYLE-003`, `STYLE-005` |
| `EdronError` | Edron diagnostic base exception | Base | Facade diagnostic only; `DIAG-001` |
| `RegistrationError`, `PhaseError`, `BindingError` | facade contract exceptions | Base | Facade diagnostic only; `DIAG-001` |
| `CapabilityError`, `MissingCapabilityError`, `IncompatibleCapabilityError`, `BrokenCapabilityError` | optional capability exceptions | Base | Package; `DIAG-003` and optional inventory |

No other native symbol becomes a promised root re-export merely because its owning distribution is
installed. `EdronDiagnostic` and `SourceLocation` remain public from `edron.diagnostics`, not the
beginner root.

## Inventory A: application and composition

| ID | Capability / public surface | Install | Disposition | Native authority | Readiness |
|---|---|---|---|---|---|
| `APP-001` | `App(...)` creates one ASGI-callable application with explicit session/production/build inputs | Base | Facade + Native | `hedron.Hedron`, FastAPI/Starlette ASGI/lifespan/security | Ready; production evidence required |
| `APP-002` | `App.from_hedron(...)` attaches to one unsealed native app | Base | Facade + Native | native app/registry seal lifecycle | Verify |
| `APP-003` | `app.hedron` exposes the exact underlying app | Base | Native | object identity | Ready |
| `APP-004` | `@app.page(...)` registers a direct `Page` subclass | Base | Facade + Upstream | screen/router plus fresh-instance class compiler | Enable `UP-001`, `UP-004` |
| `APP-005` | page title/name/show-title and route dependencies | Base | Facade + Native | screen metadata, router, native/FastAPI DI | Verify |
| `APP-006` | `App.include(...)` accepts `FeatureProvider`/`FeatureBundle`/`JobFlow` | Base | Native + Facade | native feature bundle/catalog | Ready except `JobFlow` |
| `APP-007` | `app.native(surface)` returns the exact native handle | Base | Upstream | source/binding-to-registry lookup | Enable `UP-007` |
| `APP-008` | `app.styles(...)` delegates once and returns native metadata | Base | Native | application stylesheet/asset registry | Verify |
| `APP-009` | native routers, middleware, dependencies, pages, features, and OpenAPI coexist | Base | Native | `app.hedron` public APIs | Ready |
| `APP-010` | one Edron/native registry, renderer, route graph, and interaction catalog | Base | Native | Hedron application authorities | Ready; differential evidence required |

## Inventory B: page, output, and layout

| ID | Capability / exact Edron vocabulary | Install | Disposition | Native lowering | Readiness |
|---|---|---|---|---|---|
| `OUT-001` | fresh request-local `Page` controller and output buffer | Base | Facade | native render plan/context and response compiler | Verify |
| `OUT-002` | `Container` output delegation and context-manager scoping | Base | Facade + Native | nested native semantic nodes | Ready |
| `OUT-003` | `sidebar` | Base | Facade + Native | native page-region/layout owner | Verify |
| `OUT-004` | `container`, `card`, `columns`, `tabs`, `expander` | Base | Facade + Native | native layout/disclosure/tab/surface components | Ready |
| `OUT-005` | `include(NodeLike)` body escape hatch | Base | Native | exact `NodeLike`/`__hedron_node__` conversion | Ready |
| `OUT-006` | output methods append once and return `None` | Base | Facade | request-local lowering into native nodes | N/A; Edron contract tests |
| `OUT-007` | partial buffered output discarded on author error | Base | Facade + Native | native error/response boundary | Verify |

### Text and feedback inventory

| ID | Exact Edron methods | Native family | Install | Readiness |
|---|---|---|---|---|
| `TEXT-001` | `heading`, `subheader`, `text`, `caption`, `divider` | semantic text/heading/separator components | Base | Ready |
| `TEXT-002` | `success`, `info`, `warning`, `error`, `empty` | semantic feedback/empty-state components | Base | Ready |
| `TEXT-003` | `markdown` | native Markdown plus sanitizer/trust policy | Base | Verify package/policy evidence |
| `TEXT-004` | `code` | native code component and asset policy | Base | Ready |
| `TEXT-005` | trusted/raw HTML | native explicit trust type only; no Edron shortcut | Native base | Ready native; Deferred Edron convenience |

### Data, chart, and map inventory

| ID | Capability / exact Edron methods | Install | Disposition | Native owner | Readiness |
|---|---|---|---|---|---|
| `DATA-001` | `metric` | Base | Facade + Native | Hedron metric component | Ready |
| `DATA-002` | bounded static `table` | Base | Facade + Native | semantic table / `hedron-data` adapters | Verify data coercion matrix |
| `DATA-003` | read-only `dataframe` | Base | Facade + Native | `hedron-data` data view/table | Verify source/type matrix |
| `DATA-004` | Supported native data editor/workspace | Native base | Native + Application | `hedron-data` explicit schema/source/action policy | Ready native; no Edron 0.1 editor method |
| `CHART-001` | `line_chart`, `area_chart`, `bar_chart`, `scatter_chart` | Base | Facade + Native | first-party `hedron-charts` components/assets | Verify accessible fallback and theme evidence |
| `MAP-001` | `map` | Base | Facade + Native | `hedron-maps` geometry/component/asset policy | Verify simple-data adapter and accessible fallback |
| `DATA-005` | dataframe/table/chart coercion for Python sequences/mappings | Base | Facade + Native | owning package coercion protocols | Verify; no magic arbitrary-object dispatcher |

`DATA-004` is intentionally split from `DATA-003`: the base installation includes native editing
power, but the public API contract does not currently define `self.data_editor(...)`. Adding that
name requires a typed model, action, revision, authorization, optimistic-disposition, and fallback
contract; installation alone cannot imply those semantics.

## Inventory C: safe inputs and query filters

| ID | Capability / exact Edron vocabulary | Install | Disposition | Native authority | Readiness |
|---|---|---|---|---|---|
| `INPUT-001` | `text_input` | Base | Facade + Native | typed query control/string codec | Ready |
| `INPUT-002` | `number_input`, `slider` | Base | Facade + Native | typed numeric query controls/codecs | Ready |
| `INPUT-003` | `selectbox`, `multiselect` | Base | Facade + Native | finite-option codec/validation | Verify canonical generic option evidence |
| `INPUT-004` | `checkbox` | Base | Facade + Native | typed Boolean query control | Ready |
| `INPUT-005` | `date_input` | Base | Facade + Native | date query codec/control | Ready |
| `FILTER-001` | explicit stable `name=` identity and typed current-request value | Base | Facade + Native | query binding and native validation | Verify |
| `FILTER-002` | `updates=` connects controls to one/more bound fragments | Base | Facade + Upstream | coherent bounded GET filter plan | Enable `UP-002` |
| `FILTER-003` | automatic connected filter group | Base | Facade + Upstream | complete-query GET form and target plan | Enable `UP-002` |
| `FILTER-004` | explicit `filters(name=..., updates=...)` / `FilterScope` | Base | Facade + Upstream | named non-nested native filter plan | Enable `UP-002` |
| `FILTER-005` | canonical URL, history, latest generation, HTMX/full fallback | Base | Native + Upstream | router/HTMX/history/interaction policies | Verify plus `UP-002` |

Safe controls own URL/query state only. They are not mutation widgets, session fields, callbacks, or
whole-page rerun triggers.

## Inventory D: fragments, actions, forms, and outcomes

| ID | Capability / public surface | Install | Disposition | Native authority | Readiness |
|---|---|---|---|---|---|
| `FRAG-001` | `@ed.fragment` descriptor and direct page member | Base | Facade + Upstream | native `FragmentHandle`, safe GET route, fresh instance | Enable `UP-001` |
| `FRAG-002` | fragment call mounts/materializes initial content once | Base | Facade + Native | fragment host/response compiler | Verify |
| `FRAG-003` | `.bind(...)` and `BoundFragment` | Base | Facade + Native | native structural bound fragment/reference | Verify |
| `FRAG-004` | fragment refresh/history/target/fallback | Base | Native | Hedron HTMX/HTTP fragment policy | Ready |
| `ACT-001` | `@ed.action` and direct page member | Base | Facade + Upstream | native `ActionHandle`, unsafe route, fresh instance | Enable `UP-001` |
| `ACT-002` | `.bind(...)` and `BoundAction` | Base | Facade + Native | native structural binding; values remain untrusted | Verify |
| `ACT-003` | POST default; explicit PUT/PATCH/DELETE; CSRF/auth dependencies | Base | Native | action/security/response compiler | Ready |
| `ACT-004` | owning-page ordinary fallback | Base | Upstream | registered screen fallback/PRG policy | Enable `UP-004` |
| `ACT-005` | `updates=` registered refresh effect plan | Base | Facade + Native | action effects and refresh handles | Verify |
| `ACT-006` | `idempotency="required"` and generated submission key | Base | Native + Application | native policy/store plus application atomic boundary | Verify |
| `CONTROL-001` | `button(..., action=...)` | Base | Facade + Native | native action control | Ready |
| `CONTROL-002` | `confirm=` / `Confirm` | Base | Facade + Upstream | accessible unsafe confirmation flow | Enable `UP-005` |
| `FORM-001` | `form(Model, action=...)` | Base | Facade + Native | Pydantic/native form compiler and errors | Verify |
| `FORM-002` | `controls=` typed overrides, safe retention, redaction | Base | Facade + Native | native schema/control registry | Verify |
| `FORM-003` | HTMX and ordinary HTTP parity | Base | Native | response/error/PRG compiler | Ready; differential evidence required |
| `RESULT-001` | `Outcome` native result union | Base | Native | `InteractionResult`, `RefreshIntent`, `Patch`, `PatchSet`, `Response` | Ready |
| `RESULT-002` | `refresh(...)` | Base | Facade + Native | exact native `RefreshIntent` | Ready |
| `RESULT-003` | `success(...)` and ordinary fallback meaning | Base | Facade + Upstream | native result presentation/HTTP parity | Enable `UP-006` |

## Inventory E: dependencies, state, cache, jobs, and downloads

| ID | Capability / public surface | Install | Disposition | Native/application authority | Readiness |
|---|---|---|---|---|---|
| `DEP-001` | `dependency(...)` / `Dependency` page descriptor | Base | Facade + Upstream | native/FastAPI DI descriptor | Enable `UP-003` |
| `DEP-002` | native `Depends` identity, per-request cache, overrides, cleanup | Base | Native + Upstream | FastAPI/Hedron DI | Enable `UP-003` for class placement |
| `CACHE-001` | `cache_data(...)`, `CachedFunction.invalidate(...)`, `invalidate_all()` | Base | Facade + Native | native bounded cache | Verify scopes/key/redaction evidence |
| `STATE-001` | typed user session | Native base + Application | Native | Hedron `SessionState` dependency/host adapter | Ready native; no global Edron dictionary |
| `STATE-002` | durable domain state | Application | Application | repository/database/service | N/A |
| `STATE-003` | browser presentation preferences | Native base | Native | Hedron component/preference owner | Ready native |
| `JOB-001` | `JobFlow(...)`, `App.include(flow)`, `Page.job(...)` | Base + Application | Facade + Upstream + Application | native `TaskFlow`/`JobBackend`/`JobScope` | Enable `UP-008` |
| `JOB-002` | polling, terminal state, no-JS status, cancellation | Base + Application | Native + Upstream | native job flow/interaction policy | Enable `UP-008` |
| `JOB-003` | production worker/scheduler/backend | Application | Application | deployment/job system | N/A; never supplied by Edron |
| `DL-001` | `download(identifier)` opaque reference | Base + Application | Facade + Native + Application | authorized native download provider | Verify |
| `DL-002` | `download_button(bytes | Download, ...)` | Base | Facade + Native | native download response/control policy | Verify |

The authoritative ownership/lifetime rules are frozen in the
[state and interaction contract](../api/EDRON_STATE_INTERACTION.md). This inventory records
availability; it does not turn caches, sessions, browser state, or job status into Edron-owned
persistence.

## Inventory F: styling

| ID | Capability / public surface | Install | Disposition | Native authority | Readiness |
|---|---|---|---|---|---|
| `STYLE-001` | built-in theme name passed to `App` | Base | Facade + Native | native theme registry | Ready |
| `STYLE-002` | `theme(...)` brand constructor returns `DesignSystem` | Base | Facade + Native + Upstream | native brand compiler/shared package tokens | Enable `UP-010` for cross-package promise |
| `STYLE-003` | `Color`, `DesignSystem`, `StyleRecipe` identity re-exports | Base | Native | exact native classes | Ready |
| `STYLE-004` | finite `variant=` aliases | Base | Facade + Upstream | native recipe-family registry metadata | Enable `UP-009` |
| `STYLE-005` | explicit native `recipe=` | Base | Native | native recipe registry/resolution | Ready |
| `STYLE-006` | `style_scope(theme/color_mode/density/context)` | Base | Facade + Native | native `StyleScope`/`StyleContext` | Verify |
| `STYLE-007` | `app.styles(...)` local CSS | Base | Native | application style/asset/CSP/cascade authority | Verify |
| `STYLE-008` | styling first-party tables/charts/maps | Base | Native + Upstream | shared semantic tokens/package adapters | Enable `UP-010` for complete guarantee |
| `STYLE-009` | source-mapped style explanation/diff | Tooling | Facade + Upstream | native style report with facade provenance | Enable `UP-011` |
| `STYLE-010` | native themes/recipes/scopes/CSS full-power path | Native base | Native | owning Hedron APIs | Ready |

Styling maturity never changes semantic, security, interaction, or accessibility maturity. A
third-party chart that cannot consume the complete native theme declares that limitation instead of
receiving a false Edron theme guarantee.

## Inventory G: packaging and optional adapters

### Base distribution inventory

| ID | Installed responsibility | Distribution owner | Edron exposure |
|---|---|---|---|
| `PKG-BASE-001` | ASGI/components/forms/HTMX/styling/security | `hedron` (+ transitive `hedron-core`) | root façade and `app.hedron` |
| `PKG-BASE-002` | tables/data views/native data editing | `hedron-data` | `table`, `dataframe`, native imports |
| `PKG-BASE-003` | first-party charts and assets | `hedron-charts` | generic chart methods, native imports |
| `PKG-BASE-004` | first-party maps and assets | `hedron-maps` | `map`, native imports |
| `PKG-BASE-005` | safe Markdown | selected parser/sanitizer + Hedron policy | `markdown` |
| `PKG-BASE-006` | development server/reload | selected server dependencies | `edron run` |

The exact accepted requirements live only in the packaging manifest. This table inventories
responsibility and must not become a divergent version list.

### Optional adapter inventory

| Capability ID | Edron/native entry | Direct requirements | Shortcut | Owner | Maturity |
|---|---|---|---|---|---|
| `data.pandas` | object input to `table`/`dataframe`/charts where supported | `pandas`, `narwhals` | `edron[pandas]` | `hedron-data` adapters | beta candidate |
| `data.polars` | object input to `table`/`dataframe`/charts where supported | `polars`, `narwhals` | `edron[polars]` | `hedron-data` adapters | beta candidate |
| `data.pyarrow` | object input to `table`/`dataframe`/charts where supported | `pyarrow`, `narwhals` | `edron[pyarrow]` | `hedron-data` adapters | beta candidate |
| `chart.plotly` | `plotly_chart` | `plotly` | `edron[plotly]` | `hedron-charts` adapter | experimental |
| `chart.altair` | `altair_chart` | `altair`, `vl-convert-python` | `edron[altair]` | `hedron-charts` adapter | experimental |
| `chart.matplotlib` | `matplotlib_chart` | `matplotlib` | `edron[matplotlib]` | `hedron-charts` adapter | beta/static Supported scope |
| `data.sqlalchemy` | native `hedron-data` source through `App.include`/native composition | `sqlalchemy` | `edron[sqlalchemy]` | `hedron-data` source adapter | beta candidate; no magic Edron query API |

Version specifiers, markers, and diagnostic commands are normative in the
[packaging contract](../api/EDRON_PACKAGING.md), not duplicated here. Every optional entry is always
discoverable/type-checkable at its documented Edron surface, activates from compatible direct
installation, and fails precisely as missing/incompatible/broken. The extra is not a runtime flag.

### Installed native capabilities not promoted into Edron 0.1

The base/owning packages may expose more public APIs than Edron wraps. Examples include native data
workspaces/editors/sources, advanced chart interactions, advanced map layers/providers, theme
builders, component refs, patches, catalog inspection, and package feature bundles. They remain
usable through native imports and `app.hedron`/`App.include`.

Optional adapters present in an owning Hedron package but absent from the curated Edron registry—
including PyDeck, Folium, Graphviz, Great Tables, NetworkX, Bokeh, HoloViews, Pygal, and Datashader
in the current chart package—are native-only/deferred for Edron 0.1. Installing one does not create
an undocumented Edron method or shortcut. Promotion requires a public surface, capability ID,
dependency range, maturity, accessibility/security limitations, diagnostics, and tests.

## Inventory H: native full-power escape hatches

| ID | Full-power path retained | Edron bridge | Authority |
|---|---|---|---|
| `NATIVE-001` | any public body `NodeLike`/compatible component | `Page.include(...)` | native renderer/component |
| `NATIVE-002` | native pages, routes, middleware, dependencies, exception handlers, OpenAPI | `app.hedron` | native app/FastAPI |
| `NATIVE-003` | native feature providers/bundles | `App.include(...)` | native feature catalog |
| `NATIVE-004` | native `FragmentHandle` as update target | `updates=`, `refresh(...)` | native interaction registry |
| `NATIVE-005` | native `ActionHandle` as control action | `button`/`form` action positions | native action registry |
| `NATIVE-006` | native outcomes/patches/responses | action `Outcome` return | native response compiler |
| `NATIVE-007` | native themes/design systems/recipes/style contexts | `App`, `recipe=`, `style_scope`, identity re-exports | native styling registry |
| `NATIVE-008` | typed sessions, auth/security, cache, jobs, downloads | dependency/native imports | owning native/application contract |
| `NATIVE-009` | package-native data/chart/map advanced APIs | native imports + `include`/feature bundles | owning `hedron-*` package |
| `NATIVE-010` | exact generated handle inspection/composition | `app.native(...)` | native registry; blocked on `UP-007` |

These paths are not “ejection.” Edron and native surfaces may be mixed within one app, page, and
interaction graph where the public protocols allow it. Edron does not promise root re-exports for
all native symbols because direct owning-package imports are the clearer powerful interface.

## Inventory I: CLI and diagnostics

| ID | Command/capability | Install | Imports trusted app? | Native/Edron authority | Readiness |
|---|---|---|---|---|---|
| `TOOL-001` | `edron run APP` | Tooling/base | Yes | server + exact ASGI app | Verify packaging/server lane |
| `TOOL-002` | `edron check APP` | Tooling/base | No | Edron static source model + native diagnostic schema | N/A/Verify schema |
| `TOOL-003` | `edron check APP --register` | Tooling/base | Yes | native registration/seal plus source projection | Verify |
| `TOOL-004` | `edron explain APP` | Tooling/base | Yes | native sealed registries/reports + Edron source map | Enable source-provenance items |
| `TOOL-005` | `edron doctor [APP]` | Tooling/base | Only when `APP` supplied and disclosed | packaging manifest + bounded import probes | N/A |
| `TOOL-006` | `edron style check` | Tooling/base | As documented by mode | native style diagnostics | Verify |
| `TOOL-007` | `edron style preview` | Tooling/base | No application callbacks/data | fixed synthetic content + native renderer | Verify |
| `TOOL-008` | `edron style explain` / `style diff` | Tooling/base | Trusted registry/report inputs | native reports + facade provenance | Enable `UP-011` |
| `DIAG-001` | Edron codes/source locations | Base | N/A | Edron facade validation projected through native schema | N/A |
| `DIAG-002` | native `HED-*` failures retain identity/cause | Base | N/A | native diagnostic authority | Ready |
| `DIAG-003` | optional capability missing/incompatible/broken | Base | Bounded hard-coded probes only | packaging contract | N/A |

Static tooling never executes page renderers, fragments, actions, dependencies, jobs, data loaders,
or network services. Trusted import modes cannot be disguised as static analysis.

## Inventory J: cross-cutting behavior

| Family | Ordinary HTTP/no-JS | State owner | Security authority | Accessibility requirement |
|---|---|---|---|---|
| Static output/layout | full semantic page | request-local output only | native escaping/trust/CSP | semantic component, reflow, keyboard where interactive |
| Safe input/filter | GET page/form with canonical query | URL/current request | typed binding; query is untrusted/public | label, errors, keyboard, focus/history |
| Fragment | direct safe GET/full fallback | current binding/generation | target allowlist/auth dependencies | stable host, busy/focus/announcement |
| Action/button | unsafe form/PRG | one operation + domain service | method, CSRF, authz, idempotency/revision | accessible control/status/confirmation |
| Pydantic form | semantic 422/form page | one submission | body limits, CSRF, validation, authz, redaction | field errors, summary, focus, retention rules |
| Cache | same response semantics | native bounded derived cache | explicit private/tenant/public scope | cache cannot alter meaning |
| Session | ordinary request dependency | native typed session | host signing/storage/expiry | continuity cannot hide required labels/errors |
| Job flow | submit/status/manual refresh/result | backend + authoritative `JobScope` | authz on every operation/result | status semantics, bounded announcements, no-JS refresh |
| Download | authorized ordinary response | provider/domain | opaque ID, authz, headers/ranges | labeled control and meaningful filename/type |
| First-party chart/map | semantic fallback/page | request/domain data | native asset/CSP/data-provider policy | description/data alternative for Supported claim |
| Optional adapter | same as owning native adapter | never package metadata | explicit backend, no silent fallback | native maturity/limitations remain visible |
| Styling | same content without styling/JS | native preference/presentation only | CSS cannot change behavior/auth | contrast, modes, motion, zoom/reflow/RTL/print |

Detailed lifecycle/concurrency/error rules remain in the
[state and interaction contract](../api/EDRON_STATE_INTERACTION.md).

## Inventory K: required upstream Hedron enablement

Every item below begins `Unresolved`. Stage 0 must either cite existing public Hedron evidence and
change it to `Existing`, or approve/implement a native Hedron contract and change it to `Shipped`.
Edron cannot satisfy an item privately.

| ID | Workstream | Native enablement question | Edron capabilities blocked | Proposed native owner | Stage 0 state |
|---|---|---|---|---|---|
| `UP-001` | `HEDRON-WS-CLASS` | Fresh-instance class compiler for direct page members, inspected signatures, async, and exact handles | `APP-004`, `FRAG-001`, `ACT-001` | Hedron application/interaction compiler | Unresolved |
| `UP-002` | `HEDRON-WS-INTERACTIONS` | Bounded coherent typed GET filter plan across named controls and refresh targets | `FILTER-002`–`FILTER-005` | Hedron router/forms/interaction plan | Unresolved |
| `UP-003` | `HEDRON-WS-CLASS` | Public class dependency descriptor with cleanup, override, static explanation, and shadow protection | `DEP-001`, `DEP-002` | Hedron/FastAPI dependency integration | Unresolved |
| `UP-004` | `HEDRON-WS-INTERACTIONS` | Safe owning-screen fallback derivation preserving unsafe method, CSRF, validation, and redirect policy | `APP-004`, `ACT-004` | Hedron action/response compiler | Unresolved |
| `UP-005` | `HEDRON-WS-INTERACTIONS` | Accessible destructive confirmation with keyboard/focus/cancel and unsafe no-JS submission | `CONTROL-002` | Hedron component/interaction layer | Unresolved |
| `UP-006` | `HEDRON-WS-INTERACTIONS` | Native success outcome presentation with equivalent HTMX/ordinary HTTP meaning | `RESULT-003` | Hedron interaction response compiler | Unresolved |
| `UP-007` | `HEDRON-WS-PROVENANCE` | Stable lookup from facade source surface/binding to exact native handle/reference | `APP-007`, `NATIVE-010`, explanation | Hedron registry/catalog | Unresolved |
| `UP-008` | `HEDRON-WS-JOBS` | `TaskFlow` backend dependency, shared scope, result adapter, polling terminality, and production gate | `JOB-001`, `JOB-002` | Hedron jobs/package workflow | Unresolved |
| `UP-009` | `HEDRON-WS-STYLING` | Variant aliases projected from native recipe-family registry metadata | `STYLE-004` | Hedron styling registry | Unresolved |
| `UP-010` | `HEDRON-WS-STYLING` | Brand/theme token contract consumed consistently by core/data/charts/maps | `STYLE-002`, `STYLE-008` | Hedron styling + owning packages | Unresolved |
| `UP-011` | `HEDRON-WS-PROVENANCE` | Native style/registry reports retain external facade source provenance without another schema | `STYLE-009`, `TOOL-004`, `TOOL-008` | Hedron diagnostics/style reports | Unresolved |

For each resolved row the packet records the Hedron public symbol/schema, minimum release,
maturity, RFC/contract, conformance tests, owner, and rollback story. “Similar internal code exists”
is not sufficient evidence.

## Inventory L: deliberately deferred or native-only

| ID | Capability/name | 0.1 disposition | Reason / supported path |
|---|---|---|---|
| `DEF-001` | `write` or magic arbitrary-object dispatcher | Deferred | obscures typing/lowering; use explicit methods or `include` |
| `DEF-002` | `unsafe_allow_html` / raw HTML shortcut | Native-only | keep explicit native trust boundary |
| `DEF-003` | `import edron as st` compatibility | Rejected | Edron is not a Streamlit alias or rerun runtime |
| `DEF-004` | Boolean-returning buttons / `if button` mutation | Rejected | actions are registered unsafe boundaries |
| `DEF-005` | module-global output, whole-script reruns, persistent page instances, lifecycle hooks | Rejected | conflicts with request/HTMX lifecycle |
| `DEF-006` | global `session_state` dictionary | Rejected | use URL/form/native typed session/durable/cache owners |
| `DEF-007` | `cache_resource` | Deferred | resources use dependency lifecycle/cleanup |
| `DEF-008` | custom `Page.__init__` / constructor injection | Deferred | use the inherited constructor and `dependency` descriptor |
| `DEF-009` | inherited exposed decorated fragments/actions | Deferred | redeclare explicitly to preserve source/identity |
| `DEF-010` | arbitrary callback args | Rejected | use typed descriptors and `.bind(...)` |
| `DEF-011` | Edron `data_editor` | Deferred | native editor available; simplified schema/action/conflict API not frozen |
| `DEF-012` | arbitrary style dictionaries/inline CSS/utility DSL/runtime injection | Rejected | variants, recipes, scopes, registered CSS |
| `DEF-013` | automatic optional backend fallback | Rejected | explicit backend either works or diagnoses precisely |
| `DEF-014` | `edron[all]`, runtime install, install button | Rejected | reproducibility/security; direct deps and curated shortcuts only |
| `DEF-015` | production worker/scheduler/database/ORM/auth provider/deployment platform | Application-owned | configure native/application services |
| `DEF-016` | required SSE/WebSocket job observation | Deferred | polling + no-JS status is 0.1 contract |
| `DEF-017` | Flask/Django page-class parity | Deferred | ASGI/FastAPI-native 0.1; native bridges remain separate |
| `DEF-018` | automatic wrapping/re-export of every `hedron-*` capability | Rejected | use native imports/composition and deliberate promotions |

Deferred is a design boundary, not an invitation for implementation-only convenience. Promotion
requires updating the public contract, packaging/install disposition, state/interaction behavior,
native authority, maturity, tests, and migration analysis.

## Golden and acceptance coverage inventory

| Fixture/evidence | Directly exercises | Important capabilities not proved by that fixture |
|---|---|---|
| Golden 1: hello page | app/page, text, basic theme, server/base install | interactions, optional adapters, mixed native composition |
| Golden 2: sales dashboard | layout, metric, dataframe, first-party chart, filters, fragment, cache | mutation, jobs, maps, native data editor |
| Golden 3: customer CRUD | dependency, Pydantic form, actions/binding, confirmation, idempotency, refresh | multi-worker job/session/cache backends |
| Golden 4: report job | `JobFlow`, backend/scope, polling, cancellation/result/download | optional adapters, native mixed registration |
| Golden 5: Plotly | optional detection, direct/shortcut equivalence, explicit failure | other optional capability matrices |
| Golden 6: styling | theme, variants, recipes, scopes, local CSS, native package styling | all browser/a11y/platform matrices by itself |

The six golden applications are necessary but not sufficient. The acceptance packet additionally
requires focused fixtures for:

- first-party `map` geometry/asset/network/accessibility behavior;
- native `hedron-data` editing availability and the absence of an Edron editor claim;
- pandas, Polars, PyArrow, Altair, Matplotlib, and SQLAlchemy capability matrices;
- native component/fragment/action/feature/style composition and exact object identity;
- typed native sessions, cache scopes/restart, downloads/ranges, and multi-worker job scope;
- every CLI trusted/static boundary and structured report format;
- wheel/sdist clean installs, artifact assets, invalid native trains, upgrades, and rollback; and
- browser/no-JS/security/accessibility/performance matrices from the companion contracts.

## Completeness and drift rules

Before an Edron public capability is added or changed, the same review updates:

1. its inventory row/ID and 0.1/deferred disposition;
2. the public signature or explicit native-only path;
3. installation class and owning distribution/capability manifest;
4. native lowering/identity and any upstream enablement item;
5. HTTP/HTMX/no-JS and state ownership behavior where interactive;
6. security, accessibility, performance, maturity, and limitation claims;
7. golden or focused acceptance coverage; and
8. documentation, diagnostics, compatibility, and migration evidence.

CI eventually derives/checks the machine-readable capability subset used by packaging and doctor,
but this human inventory remains review-oriented. Runtime does not load this Markdown as a feature
registry.

No row may be marked implementable when its `Enable` item remains unresolved. No optional row may
be marked available because an extra name was requested. No native-only row may be described as an
Edron root export. No Supported claim may be inherited without the owning native evidence.

## Acceptance criteria

- **EDR-INV-COMPLETE-001:** Every public root symbol, `App`/`Page`/`Container` method family, CLI,
  base battery, optional capability, native escape hatch, and explicit deferral has one inventory
  disposition.
- **EDR-INV-OWNER-001:** Every non-facade behavior identifies exactly one native, package, or
  application authority; Edron introduces no duplicate runtime authority.
- **EDR-INV-INSTALL-001:** Every capability is classified as Base, Optional, Native base,
  Application, Tooling, or Deferred consistently with built package metadata.
- **EDR-INV-UPSTREAM-001:** Every `Enable` row has an accepted existing/shipped Hedron evidence
  record before its Edron capability is implemented or released.
- **EDR-INV-INTEROP-001:** Native-only and mixed-composition inventories prove that Edron retains
  full public Hedron access and exact object/registry/asset identity.
- **EDR-INV-OPTIONAL-001:** Optional adapter entry points, owner, maturity, dependency manifest,
  direct/shortcut equivalence, failure states, and explicit-backend behavior match all contracts.
- **EDR-INV-CROSSCUT-001:** Every interactive/visual family has ordinary fallback, state,
  security, accessibility, asset, and maturity dispositions with acceptance evidence.
- **EDR-INV-COVERAGE-001:** Golden and focused fixtures cover every non-deferred inventory row;
  absence of golden coverage cannot be mistaken for acceptance evidence.
- **EDR-INV-DRIFT-001:** Public API, state/interaction, packaging, RFC, native contracts,
  capability manifest, inventories, fixtures, and generated diagnostics fail CI when inconsistent.

## See also

- [Edron 0.1 public API](../api/EDRON.md)
- [Edron state and interaction](../api/EDRON_STATE_INTERACTION.md)
- [Edron packaging](../api/EDRON_PACKAGING.md)
- [Edron implementation specification](EDRON_001.md)
- [Edron acceptance packet](../acceptance/EDRON_001.md)
- [RFC-0094](../rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md)
- [Edron golden applications](EDRON_GOLDEN_APPS.md)
- [Hedron API](../api/HEDRON.md)
- [Package-native workflows](../api/PACKAGE_WORKFLOWS.md)
- [Refreshable views/actions](../api/REFRESHABLE_VIEWS.md)
- [State](../api/STATE.md)
- [Jobs](../api/JOBS.md)
- [Application styling](../api/APPLICATION_STYLING_065.md)
