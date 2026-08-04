# Plotly Dash feature cross-check

**Audit date:** 2026-08-04<br>
**Dash baseline:** 4.4.1<br>
**Dash AG Grid baseline:** 35.2.0, wrapping AG Grid 35.2.0<br>
**Scope:** Dash Open Source, Dash Core Components, Dash AG Grid, and the current official Dash
documentation<br>
**Purpose:** identify useful capability gaps, not reproduce Dash's React callback runtime

Dash is a particularly useful comparison for Hedron because both projects target Python-authored
data applications, but they make different runtime choices. Dash serializes a React component tree
and maintains a browser-visible callback dependency graph. Hedron renders explicit HTML and uses
HTTP actions, fragments, HTMX, and registered browser components. This audit therefore compares
user outcomes and operational guarantees rather than requiring call-for-call API parity.

## Official source baseline

The audit uses Plotly's first-party documentation and repositories:

- [Dash 4.4.1 package and release date](https://pypi.org/project/dash/4.4.1/)
- [Dash documentation](https://dash.plotly.com/)
- [Dash API reference](https://dash.plotly.com/reference)
- [Dash source repository](https://github.com/plotly/dash)
- [Dash changelog](https://github.com/plotly/dash/blob/dev/CHANGELOG.md)
- [Dash Core Components](https://dash.plotly.com/dash-core-components)
- [Dash callbacks](https://dash.plotly.com/basic-callbacks),
  [advanced callbacks](https://dash.plotly.com/advanced-callbacks), and
  [WebSocket callbacks](https://dash.plotly.com/websocket-callbacks)
- [Dash Pages and URLs](https://dash.plotly.com/urls)
- [Dash MCP](https://dash.plotly.com/dash-mcp)
- [Dash AG Grid](https://dash.plotly.com/dash-ag-grid)

The baseline is the latest stable Dash release available on the audit date. Dash Enterprise,
Design Kit, Snapshot Engine, Dashboard Toolkit, Plotly Cloud hosting, and other commercial services
are not portable framework features and are not parity targets. Open-source integration points
that those products also use are still included.

## Disposition rules

- **Covered/equivalent:** Hedron already supplies the outcome, sometimes through normal HTML,
  explicit routes/actions, or a different server framework mechanism.
- **Expanded existing phase:** the Dash audit found a concrete omission in a coherent phase already
  on the roadmap.
- **Planned 0.17:** the capability belongs to a new reactive-dashboard and agent-interface packet.
- **Recipe/plugin:** public Hedron composition can provide it without a first-party runtime API.
- **Deliberate non-parity:** the Dash mechanism conflicts with Hedron's explicit-request, security,
  determinism, accessibility, or no-arbitrary-JavaScript boundary. The useful outcome may still be
  covered by a safer Hedron mechanism.

## Executive result

| Dash capability family | Hedron result |
|---|---|
| HTML/component tree, styling, assets, metadata, multipage URLs | Covered by components, HDJ/native HTML, scoped assets/themes, `Page`, `Nav`, routes, and history policy. |
| Core inputs, loading, uploads, downloads, browser state | Mostly covered; clipboard, confirmation, geolocation, tooltip, and folder-upload details are added to 0.15. |
| Plotly figures and ordinary chart rendering | Covered in 0.6; the complete interaction-event bridge is made explicit in 0.12. |
| Reactive callbacks and cross-filter dashboards | Useful outcome accepted for 0.17 as a typed, deterministic interaction graph over explicit actions and declared regions. |
| Partial property updates and `set_props` | Accepted for 0.17 as bounded, schema-checked, versioned patches with full-fragment fallback. |
| Pattern-matching dynamic component IDs | Accepted for 0.17 as structured collection identities and map/gather/broadcast selectors, not arbitrary DOM matching. |
| Async, background, progress, cancel, errors, cache | Covered by async endpoints, `InteractionResult`, `JobBackend`, cache, status/progress, and 0.13 tracing; 0.17 unifies the dashboard-facing lifecycle. |
| WebSocket and persistent callbacks | 0.10 expanded with declared client-state reads, intermediate region updates, page-session lifecycle, and disconnect cleanup. |
| DataTable and Dash AG Grid | Hedron tables/editors and AG Grid Community adapter cover the baseline; 0.12 now names saved grid state, events, and client/infinite row-model behavior. |
| Custom React components, all-in-one components, and hooks | Covered by component packages, Web Components, plugins, browser modules, typed events, and Explorer extensions without requiring React. |
| Dev tools and testing | Covered by Explorer graphs/traces, diagnostics, snapshots, Playwright/a11y/visual hooks, and pytest helpers; 0.17 adds the dashboard graph view. |
| Jupyter display | Server-side notebook preview is a real gap and is assigned to 0.17; the 0.16 JupyterLite/Pyodide sandbox solves a different problem. |
| MCP resources and tools | Accepted for an optional deny-by-default `hedron-mcp` projection in 0.17. |

## Complete Dash Core Components cross-check

Dash 4.4.1 documents 26 Dash Core Components. The HTML component namespace is considered
separately: Hedron's built-ins, HDJ, and native HTML already cover semantic HTML elements.

| Dash Core Component | Hedron disposition |
|---|---|
| `Button` | **Covered:** button, submit, link, icon, refresh, and explicit `Action` variants. Styling is theme-owned. |
| `Checklist` | **Covered/0.15:** checkbox groups exist; richer multi-selection and pill presentation are owned by 0.15. |
| `Clipboard` | **Expanded 0.15:** typed copy button for declared text or a declared component value, with user activation, secure-context, permission, feedback, and no-JavaScript selection fallback. Arbitrary clipboard reads are excluded. |
| `ConfirmDialog` | **Expanded 0.15:** `ConfirmAction` composes the 0.10 dialog with an explicit action. Confirmation is never treated as authorization or proof of destructive intent. |
| `ConfirmDialogProvider` | **Expanded 0.15 equivalent:** confirmation wraps a declared link/button/action, not an arbitrary descendant event listener. |
| `DatePickerRange` | **Planned 0.15:** typed date range with locale, min/max, disabled dates, incomplete-range validation, and native fallback. |
| `DatePickerSingle` | **Planned 0.15:** typed date input with locale and validation. |
| `Download` | **Covered:** `DownloadButton`, explicit response ownership, authorization, filename/content-type, streaming, and size policy. |
| `Dropdown` | **Covered/0.15:** select is present; multiselect, search, clearability, and rich selection ergonomics belong to 0.15. Arbitrary executable option renderers do not. |
| `Graph` | **Covered/expanded 0.12:** Plotly figures ship through the chart adapter; typed hover, click, selection, relayout, legend, viewport, extend, and prepend events are made explicit in 0.12. |
| `Geolocation` | **Expanded 0.15:** permission-gated `GeolocationInput` returns typed coordinates, accuracy, altitude/heading/speed where available, timestamp, denial/error states, expiry, and a manual fallback. Location is never an authorization factor. |
| `Input` | **Covered/0.15:** text and common HTML inputs exist; number, range, date/time, color, and specialized input ergonomics are consolidated in 0.15. |
| `Interval` | **Covered:** polling and lazy refresh helpers provide bounded intervals; 0.10 adds SSE/WebSocket alternatives when evidence supports them. |
| `Link` | **Covered:** safe links, route reversal, boosted navigation, history policy, external-target policy, and ordinary navigation fallback. |
| `Loading` | **Covered:** loading regions, skeletons, progress/status, `aria-busy`, error/retry behavior, and action lifecycle indicators. |
| `Location` | **Covered:** explicit routes, URL/query state, redirects, history updates, page metadata, and request context. |
| `Markdown` | **Covered:** optional Markdown adapter with sanitization/trust boundary and local assets. |
| `RadioItems` | **Covered:** radio group; choice cards and segmented variants are planned later without changing submitted-value semantics. |
| `RangeSlider` | **Planned 0.15:** range input with typed bounds, step, marks, validation, and keyboard/native fallback. |
| `Slider` | **Planned 0.15:** slider/select-slider with typed bounds, marks, validation, and keyboard/native fallback. |
| `Store` | **Covered/planned 0.15:** request, URL, form, session, cache, database, and browser storage have distinct owners. `BrowserStorage` covers non-secret memory/session/local preferences with schemas, quotas, expiry, and consent. |
| `Tab` | **Covered:** accessible tabs and tab panels. Rich labels are ordinary components. |
| `Tabs` | **Covered:** accessible tabs, deep-linkable state where configured, fragment lifecycle, and no-JavaScript content fallback. |
| `Textarea` | **Covered:** typed text area with validation and form/action semantics. |
| `Tooltip` | **Expanded 0.15:** accessible tooltip/help disclosure with hover, focus, touch, escape, positioning, and non-hover equivalent. Chart-point tooltips stay within chart adapters. |
| `Upload` | **Covered/expanded 0.15:** bounded file upload exists; directory selection adds relative-path normalization, file/count/total-size caps, traversal rejection, per-file validation, and progressive fallback. |

### HTML components and layout

Dash exposes nearly every HTML tag as a React component and represents layout as a nested component
tree. Hedron already has a native node algebra, semantic built-ins, fragments, slots, standard HTML
through HDJ, and controlled trusted-content escape hatches. Dash's inline style dictionaries,
class names, arbitrary `data-*`/`aria-*` props, flexible children, and component argument order do
not expose a feature gap.

Hedron intentionally adds stronger guarantees: contextual escaping, typed URL/trust purposes,
deterministic rendering, scoped assets/styles, accessible built-in contracts, and an ordinary HTML
result before JavaScript enhancement.

## Callback and reactive behavior cross-check

| Dash callback capability | Hedron disposition |
|---|---|
| `Input`, `Output`, and `State` | **Covered/0.17 ergonomic layer:** request/action inputs and state dependencies are explicit today. 0.17 names trigger inputs versus snapshot-only state in dashboard bindings. |
| Multiple inputs and outputs | **Covered:** actions can consume typed request/form/query data and return a primary region, out-of-band regions, events, redirects/history, and status. 0.17 adds declarative multi-region binding diagnostics. |
| Chained callbacks and dependency ordering | **Planned 0.17:** finite page-local interaction graphs with cycle detection, stable topological ordering, authorization on every action edge, and no hidden application-wide execution. |
| Initial callbacks / `prevent_initial_call` | **Planned 0.17 equivalent:** initialization is opt-in per binding or explicit lazy resource; ordinary page render remains authoritative. |
| `State` without triggering | **Planned 0.17:** declared snapshot inputs are serialized only when their trigger fires. Sensitive or large state remains server-owned. |
| Callback context and changed-input detection | **Planned 0.17:** typed `TriggerContext` contains binding, event, component identity, changed fields, request/session correlation, and declared input snapshots. |
| Flexible positional, named, and grouped signatures | **Covered:** Pydantic/Hedron models and normal Python function signatures provide typed grouping; a special callback tuple grammar is unnecessary. |
| `PreventUpdate` and `no_update` | **Planned 0.17 equivalents:** explicit no-change result for all or selected declared targets, distinct from an error or empty fragment. |
| Optional inputs/outputs | **Planned 0.17:** explicit optional collection/member bindings with absent-state diagnostics. Missing required dependencies fail registration. |
| Duplicate callback outputs | **Deliberate constraint:** duplicate writers require an accepted deterministic arbitration policy. Unordered last-writer behavior is not supported. |
| `ALL`, `MATCH`, and `ALLSMALLER` pattern IDs | **Planned 0.17:** stable structured collection identities and typed map/gather/broadcast/range selectors. Arbitrary dictionaries or DOM selectors do not become authorization boundaries. |
| Dynamic component insertion/removal | **Covered/planned 0.17:** fragments already add/remove components; 0.17 validates collection registration, event teardown, focus, stale requests, and binding membership. |
| `Patch` partial property updates | **Planned 0.17:** bounded `PropertyPatch`/`CollectionPatch` operations for declared targets with schema validation, version/precondition, operation and payload caps, authorization, conflict behavior, and full-fragment fallback. |
| `set_props` updates outside declared outputs | **Deliberate constraint:** intermediate updates are useful, but targets remain declared and inspectable. Arbitrary component mutation bypassing the interaction graph is not adopted. |
| Server-side async callbacks | **Covered:** sync/async endpoints, dependencies, cancellation, timeouts, and phase 0.13 preparation/concurrency. |
| Background callbacks | **Covered:** durable `JobBackend`, 202/status/polling, cancellation requests, progress/status UI, Celery/RQ bridges, retention, and cleanup. Dash's Diskcache development/Celery production split is an implementation choice, not a new public outcome. |
| Running tuples, progress, cancel, and cache | **Covered/0.17 unified:** components and jobs exist; 0.17 defines one dashboard-facing lifecycle envelope for disabled/running/progress/cancel/error/no-change/final states. |
| Global and per-callback error handlers | **Covered:** framework handlers, action error regions, diagnostics, logging/tracing, and plugin hooks. Errors may not leak sensitive tracebacks in production. |
| No-input and no-output callbacks | **Covered equivalent:** explicit page lifecycle resources and side-effecting actions. Hidden page-load side effects are not inferred from layout. |
| Callback API endpoints | **Covered with a stronger boundary:** explicit actions and OpenAPI routes already expose typed HTTP contracts. A callback is never remotely callable merely because it updates UI. |
| Clientside callbacks, promises, and browser `fetch` | **Deliberate non-parity for arbitrary code:** use registered browser modules, Web Components, typed custom events, safe actions, and public web APIs under declared capabilities. Raw JavaScript callback strings and arbitrary eval remain prohibited. |
| Callback graph visualization | **Covered/expanded 0.17:** Explorer already owns dependency/inverse-consumer graphs and render traces; dashboard bindings add timing, payload, trigger, target, cache, and job overlays. |

### WebSocket callbacks

Dash 4.2 added per-callback WebSockets, immediate `set_props` updates, `get_prop` reads during an
execution, and persistent no-input/no-output callbacks that live for the browser session. Hedron's
0.10 transport phase already admits WebSockets only for genuinely bidirectional cases. The audit
expands the phase to include the useful, bounded outcome:

- page/session-scoped live channels with authenticated reconnect and disconnect cancellation;
- intermediate updates to declared regions and typed current-state reads from declared components;
- persistent server-push producers with explicit ownership, rate, resource, and teardown budgets;
- batching, debounce/coalescing, backpressure, origin checks, authorization, proxy/deployment
  guidance, and traceability; and
- polling or SSE/ordinary HTTP fallback whenever live transport is not a correctness requirement.

Hedron does not promise a WebSocket for every action, pin a user to a worker, or allow the server to
query arbitrary browser state.

## Plotly graphing and cross-filtering

`dcc.Graph` accepts Plotly figures and configuration and exposes hover, click/click-annotation,
selection, relayout, restyle, responsiveness, extend/prepend, animation configuration, MathJax,
and image-export configuration. Hedron's 0.6 Plotly
adapter already owns figure rendering, pinned local Plotly.js, CSP, payload caps, descriptions,
table/static fallbacks, and lifecycle cleanup.

The audit makes the following 0.12 requirements explicit:

- typed Plotly hover, click/click-annotation, box/lasso selection, relayout/viewport,
  restyle/legend, and bounded extend/prepend inputs;
- trace/point identifiers and normalized coordinates that survive reorder/filter operations;
- event debounce, coalescing, payload caps, stale-event handling, authorization, and accessible
  keyboard/table alternatives; and
- adapter-neutral chart selections that can feed 0.17 dashboard bindings and cross-filter multiple
  declared regions.

Plotly's complete trace catalog remains Plotly's responsibility. Hedron does not duplicate that
schema or guarantee every Plotly.js trace in core; the adapter records supported upstream ranges
and fails clearly for incompatible features.

## Tables and Dash AG Grid

Dash DataTable is deprecated in Dash 4 and scheduled for removal from Dash's core API in Dash 5;
Plotly recommends Dash AG Grid. Hedron should therefore compare against Dash AG Grid rather than
copy a deprecated DataTable API.

| Grid family | Hedron disposition |
|---|---|
| Column definitions, types, headers/groups, sizing, moving, pinning, spanning | **Covered/planned 0.5/0.12:** typed columns and adapter-neutral configuration; 0.12 adds saved column state and richer grid layout. |
| Client-side rows, sorting, filters, pagination, virtualization | **Covered:** DataTable/DataEditor and Tabulator baseline; AG Grid Community adapter remains available. |
| Infinite row model and server filtering/sorting | **Covered/expanded 0.12:** bounded `DataSource` paging and pushdown; explicitly test AG Grid Community infinite blocks, stable row IDs, stale requests, and selection retention. |
| Server-side and viewport row models | **License/integration boundary:** these are AG Grid Enterprise capabilities. Hedron's neutral data-source contract may support separately licensed adapters but does not advertise them as core. |
| Row/cell selection and events | **Covered/expanded 0.12:** typed selection, cell click/edit, filter/sort/column-state, viewport, drag, and pagination events with authorization and payload bounds. |
| Editing, parsers/formatters, full-row edit, undo/redo | **Covered/planned 0.5/0.12:** browser-local pending edits and typed deltas remain server-validated; executable JavaScript value functions require a registered module. |
| Cell renderers/editors, tooltips, overlays, Markdown | **Covered through adapter boundary:** approved built-ins or registered component modules; arbitrary JavaScript strings are not accepted. |
| Row drag, pinned/full-width/spanning rows, aligned grids, printing | **Expanded 0.12 where Community-supported:** backend-neutral layout/state contracts with keyboard and accessible alternatives. |
| CSV/clipboard export | **Covered/0.15:** authorized downloads and declared clipboard copy. Spreadsheet import/export beyond CSV is already 0.12. |
| Row grouping, aggregation, pivot, master/detail, integrated charts, Excel export | **0.12 outcome or licensed adapter:** Hedron-owned pivots/tree grids/export may ship independently; AG Grid Enterprise features require the user's license and cannot become an OSS parity claim. |

Hedron's application API remains backend-neutral. No AG Grid JavaScript object, callback string, or
Enterprise-only option becomes a portable Hedron guarantee.

## Pages, application shell, state, and performance

| Dash platform feature | Hedron disposition |
|---|---|
| Dash Pages, page registry, paths/templates, redirects, 404, per-page title/description/image | **Covered:** explicit routes, `Page`, `Nav`, metadata, safe redirects, error pages, route reversal, and validation. Filesystem magic is unnecessary. |
| Client navigation and URL/query/hash state | **Covered:** safe links, HTMX boost/history, explicit URL state, full-page fallback, cache variation, and redirects. |
| Flask, FastAPI, Quart, or custom server backends | **Covered in outcome:** FastAPI flagship plus Flask and Django adapters and a framework-neutral core. Quart is not required for parity because Hedron already has an async ASGI reference. |
| App lifecycle and static callback validation | **Covered differently:** deterministic registry/build checks and explicit route/component registration. Hedron does not fetch a global layout/callback graph before first render. |
| Stateless multi-worker operation | **Covered:** request state, shared cache/job/session backends, tenant isolation, proxy/multi-worker tests, and no mutable process-global application state. |
| Sharing data between callbacks | **Covered:** typed request/session/URL/browser state, cache scopes, databases, resources, and data sources have distinct ownership. Large derived data stays server-side. |
| Persistence of user-edited component values | **Planned 0.15/0.17:** namespaced `BrowserStorage`, URL/session state, and saved dashboard/grid views; persistence is explicit by field and version. |
| Memoization and serialization performance | **Covered:** cache contracts, single flight, payload budgets, external backends, serializers behind owned contracts, diagnostics, and 0.13 tracing. |
| Live updates | **Covered/planned 0.2/0.10:** polling, SSE, WebSocket, and bounded streams chosen by evidence and with fallbacks. |
| Loading states | **Covered:** region/action/job loading, progress, skeletons, status, error/retry, `aria-busy`, and reduced-motion behavior. |
| CSRF, health endpoint, compression, proxy prefixes | **Covered:** host security/operations contracts and deployment evidence. Security cannot be disabled merely to mimic an upstream backend. |
| `dash-auth` Basic Auth and Dash Enterprise authentication | **Covered with a stronger portable boundary:** host framework security, Authlib, and 0.15 OIDC/session conveniences. Hard-coded Basic Auth and vendor identity products are not first-party parity targets; application authorization remains explicit. |
| Environment/configuration and development/production modes | **Covered:** versioned typed settings, security profiles, environment overrides, diagnostics, and separate development versus production server guidance. |

## Assets, extensibility, development, and notebooks

| Dash feature | Hedron disposition |
|---|---|
| `assets/` CSS, JS, modules, images, favicon, ordering, ignore rules, external CDN path | **Covered with stricter inventory:** fingerprinted assets, component/package manifests, local/offline serving, CSP, load order, URL rewriting, external-resource policy, and application icons. Ignore rules never protect sensitive files. |
| External styles/scripts and page template override | **Covered:** explicit assets, HDJ/native document shell, metadata/head contracts, integrity/CSP policy, and trusted authoring boundary. |
| Hot reload and code reload | **Covered:** development watching and atomic rebuild/reload workflow. |
| React component packages | **Covered equivalent:** Web Components and component packages with typed props/events, assets, lifecycle, examples, tests, and docs. React may be used inside a package but is not a core runtime requirement. |
| All-in-One composite components | **Covered equivalent:** ordinary Python component composition, slots, nested identity, actions, package exports, and reusable recipes without import-time global callbacks. |
| Dash hooks/plugins | **Covered:** plugin discovery, capabilities, lifecycle, rollback, route/component/assets/diagnostic/Explorer extension points, and compatibility checks. Raw index-string mutation and automatic executable asset loading remain controlled trust boundaries. |
| Dev Tools errors, validation, callback graph, timing, hot reload | **Covered:** typed model validation, diagnostics, Explorer graphs/traces, performance panels, in-app development errors under safe profiles, and reload. Production tracebacks remain secret. |
| `dash.testing` browser fixtures | **Covered:** pytest helpers, async clients, snapshots, Playwright, browser/a11y/visual hooks, console checks, and named conformance suites. |
| Jupyter inline/external/tab display | **Planned 0.17:** a server-side `hedron-notebook` preview helper with inline iframe/link modes, proxy/root-path detection, random port/token, dimensions, error forwarding, clean shutdown, and an explicit warning for hosted/public notebooks. |
| JupyterLab extension mode | **Recipe/plugin:** first-party inline/external display is enough initially; a dedicated JupyterLab extension requires independent demand. |

The 0.16 JupyterLite/Pyodide bridge executes isolated Python in the browser. It does not replace the
0.17 notebook preview helper, which runs a normal Hedron server application from an authoring
notebook.

## MCP and agent access

Dash 4.3 can expose layout, components, pages, callbacks, clientside callbacks, and custom Python
functions to MCP clients. This reveals a useful Hedron gap, but Dash's broad default exposure is not
an acceptable default for Hedron. Phase 0.17 therefore plans an optional `hedron-mcp` distribution:

- disabled and empty by default, with per-resource and per-tool opt-in;
- resources projected from explicitly exposed pages, component metadata, data descriptions, and
  Explorer/OpenAPI schemas rather than raw process objects or source code;
- tools projected only from explicit actions or separately decorated typed functions;
- the same authentication, authorization, tenant filtering, data limits, side-effect declaration,
  confirmation policy, deadlines, cancellation, and rate limits as the underlying application;
- redacted descriptions, stable public tool names, audit records, correlation IDs, and a clear
  user-visible distinction between read-only and mutating tools;
- Streamable HTTP transport with deployment-prefix, origin, session, disconnect, and conformance
  tests; and
- diagnostics for accidental sensitive schemas, hidden-value authorization, over-broad resource
  enumeration, prompt-injection-bearing content, and tools whose declared effects disagree with
  their HTTP/action contract.

An MCP client never gains more authority than the authenticated principal. UI option filtering is
not authorization, and enabling MCP does not implicitly expose every page or action.

## Roadmap changes produced by the audit

### Expanded phase 0.10

- Intermediate WebSocket region updates, declared current-client-state reads, persistent
  page/session producers, disconnect cancellation, batching/debounce, backpressure, and fallback
  behavior are now explicit.

### Expanded phase 0.12

- Plotly hover/click/select/relayout/legend/viewport/extend events and cross-filter-ready normalized
  selection payloads are explicit.
- Grid saved views, column/filter/sort/selection state, typed grid events, stable row IDs, and AG
  Grid Community client/infinite row-model conformance are explicit.

### Expanded phase 0.15

- Typed clipboard copy, action confirmation, geolocation, accessible tooltip/help, and directory
  upload are added to the data-app surface.

### New phase 0.17 — reactive dashboards and agent interfaces

- Deterministic page-local dashboard interaction graphs.
- Versioned, bounded property and collection patches.
- Structured dynamic collection identities and selectors.
- Unified trigger/action lifecycle and cross-filter composition.
- Server-side Jupyter preview helper.
- Optional deny-by-default MCP projection.
- Dash migration inventory, coexistence guidance, and diagnostics without automatic semantic
  conversion.

## Deliberate non-parity

The following are not missing planned features:

1. **A universal client-maintained callback DAG.** Hedron keeps HTTP actions, authorization, cache,
   effects, and target regions visible. Phase 0.17 is finite and page-local, not a second app runtime.
2. **Raw clientside callback strings, arbitrary JavaScript evaluation, or unregistered browser
   functions.** Registered modules and typed events preserve CSP and inspection.
3. **Undeclared `set_props` mutation.** Intermediate updates are accepted only for registered
   targets with schema and lifecycle checks.
4. **Unordered duplicate writers.** A target cannot have ambiguous concurrent writers without an
   explicit deterministic arbitration policy.
5. **Browser props or hidden UI options as authorization.** Every action, patch, grid query, and MCP
   tool rechecks server authority.
6. **React as Hedron's required component runtime.** Web Components, HTML, HDJ, and browser modules
   remain the portable boundary; a package may internally choose React.
7. **Filesystem-driven page registration or import-time callback side effects.** Explicit routes,
   registries, and package manifests remain inspectable and deterministic.
8. **Dash Enterprise, Design Kit, Snapshot Engine, Dashboard Toolkit, or Plotly Cloud parity.**
   These are commercial products. Portable underlying outcomes are evaluated independently.
9. **Unlicensed AG Grid Enterprise features.** Hedron may integrate with a user's licensed adapter,
   but Community and Hedron-owned capabilities are the only open-source baseline claims.

## Migration guidance

| Dash concept | Hedron direction |
|---|---|
| `app.layout` | `Page`/component tree or HDJ template |
| Dash Pages | explicit Hedron routes, `Page`, and `Nav` |
| `Input` | action/event trigger or typed form/query input |
| `State` | declared request/session/URL/browser snapshot input |
| `Output` | primary or out-of-band declared region in `InteractionResult` |
| chained callback | explicit action composition today; 0.17 interaction graph where justified |
| `Patch` / `set_props` | full fragment today; typed versioned patch in 0.17 |
| `dcc.Store` | URL, form, session, cache/database, or 0.15 `BrowserStorage` according to ownership |
| `dcc.Graph` | `PlotlyChart` plus 0.12 typed chart events |
| Dash DataTable | `DataTable`/`DataEditor`; prefer backend-neutral adapters over a deprecated API |
| Dash AG Grid | AG Grid Community adapter or Tabulator through Hedron's table/editor contracts |
| background callback | `JobBackend`, status/progress/cancel, polling/SSE/WebSocket as appropriate |
| clientside callback | registered browser module or Web Component with typed event |
| Dash hook/plugin | Hedron component package or plugin |
| Dash MCP | explicit `hedron-mcp` resources/tools in 0.17 |

## Maintenance rule

Refresh this matrix before closing phases 0.10, 0.12, 0.15, and 0.17 and whenever Hedron claims
Dash migration or reactive-dashboard coverage. A newly documented Dash or Dash AG Grid capability
must be classified as covered, expanded existing phase, planned later phase, recipe/plugin, licensed
integration, or deliberate non-parity. Accepted gaps require a phase owner, security and
accessibility boundaries, and evidence-bearing exit gates before they appear as Supported.
