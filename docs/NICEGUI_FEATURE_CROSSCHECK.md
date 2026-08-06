# NiceGUI feature cross-check

**Audit date:** 2026-08-05<br>
**NiceGUI baseline:** 3.15.0 (PyPI) and current documentation / element catalog<br>
**Purpose:** identify useful capability gaps, not reproduce NiceGUI's Vue/Quasar client,
WebSocket outbox, or imperative element-mutation runtime

NiceGUI is a valuable comparison because it shares a FastAPI/Starlette host and optimizes for
backend-first Python UIs aimed at dashboards, tools, robotics, and IoT. Hedron targets overlapping
audiences (CRUD, admin, data apps, dashboards) with a different contract: typed components,
HTMX fragments, ordinary HTTP, fail-closed region authorization, and multi-worker-safe hosts.
This audit therefore compares user-visible outcomes and operational guarantees rather than
element-for-element API compatibility.

## Official source baseline

- [NiceGUI repository](https://github.com/zauberzeug/nicegui)
- [NiceGUI documentation](https://nicegui.io/documentation)
- [NiceGUI 3.15.0 package metadata](https://pypi.org/project/nicegui/3.15.0/)
- Element modules under `nicegui/elements/` and the documentation `ui.*` map
- First-party examples under `examples/` (chat, maps, calendars, terminals, robotics, auth, …)
- Architecture notes in the NiceGUI README (Vue/Quasar frontend, socket.io, outbox, single worker)

Community projects and Quasar/Vue ecosystem widgets are treated as demand signals, not automatic
first-party Hedron commitments.

## Disposition rules

- **Covered/equivalent:** Hedron already supplies the outcome through typed components, routes,
  actions, polling/SSE, jobs, or a different mechanism.
- **Expanded existing phase:** the audit found a concrete omission in a coherent phase already on
  the roadmap (primarily 0.15–0.17).
- **Recipe/plugin / specialty extra:** public composition or an optional `hedron-extras` feature can
  provide it without expanding core runtime contracts.
- **DX/docs only:** documentation, scaffolding, or packaging improvements that do not require a
  capability phase.
- **Deliberate non-parity:** the NiceGUI mechanism conflicts with Hedron's HTMX/HTML boundary,
  authorization model, multi-worker deployment, accessibility, or no-arbitrary-JavaScript posture.
  A safer Hedron equivalent may still cover the useful outcome.

## Executive result

| NiceGUI capability family | Hedron result |
|---|---|
| Standard controls, layout, cards, dialogs, tabs, menus, notifications | Mostly covered; remaining typed controls and popover/docks owned by **0.15**. |
| Media players, upload, capture, clipboard, geolocation | Covered/planned in **0.15** with stricter permission, range, retention, and trust contracts. |
| Storage tiers (tab/client/user/browser/general) | Partially covered; **0.15** completes `BrowserStorage` and clarifies SessionState / named connections versus NiceGUI's file-backed tiers. |
| Timer, binding, refreshable UI, high-frequency client updates | Useful outcome accepted as inspectable **0.17** bindings + Supported polling / experimental live transports — not Vue outbox mutation. |
| Tree, stepper, splitter, FAB, keyboard shortcuts, interactive image | Owned by **0.16** extras; NiceGUI validates demand. |
| JSON editor, log console, 3D models, charts (Plotly/Matplotlib/ECharts/Altair) | Charts exist; editors/logs/3D owned by **0.12/0.16**. |
| Leaflet / maps | Genuine gap; **expanded 0.15** as a policy-bounded Map/GeoJSON adapter (exit gate already cites maps). |
| Carousel, lightbox, timeline, context menu, chip input, progress variants | Underspecified beside Gallery/Progress; **expanded 0.15**. |
| Authenticated download helpers and ranged media serving | Needed for Audio/Video/PDF; **expanded 0.15**. |
| CodeMirror / editable code | Distinct from `CodeBlock`/`JSONEditor`; **expanded 0.16** as `CodeEditor`. |
| Signature pad, FullCalendar, typeahead/combobox | Demand from NiceGUI examples; **0.16** extras or recipes. |
| XTerm, joystick, deep Three.js scene, WebSerial/ROS2 | Specialty audience; optional extras only with strict policy — not beachhead. |
| Native desktop window (`ui.run(native=…)`) | Optional ops/recipe shell over uvicorn; not a second UI runtime. |
| Vue/Quasar + socket.io outbox, `run_javascript`, client DOM query mutation | **Deliberate non-parity.** |
| Imperative data binding / refreshable containers / SPA `sub_pages` | **Deliberate non-parity**; HTMX panel-swap and explicit routes cover the useful outcome. |
| pytest `user` / `screen` fixtures, ElementFilter marks | Testing harness owned by **0.15**; borrow mark/filter ergonomics. |
| `llms.md` / Docker one-command demos | **DX/docs**; ship anytime without a capability phase. |

## Controls and forms

| NiceGUI surface | Hedron disposition |
|---|---|
| `ui.button`, checkbox, switch, radio, select, input, textarea, number, slider, range | **Covered/planned 0.15:** core controls exist; remaining typed families (number/range/date/time/color/rating/toggle/segmented/menu button) are already scoped. |
| `ui.date`, `ui.time`, `ui.date_input`, `ui.time_input`, `ui.color_input`, `ui.color_picker`, `ui.rating` | **Planned 0.15.** |
| `ui.input_chips`, `ui.chip` | **Expanded 0.15:** typed chip/tag input and display chips with native fallback (multiselect-adjacent). |
| `ui.toggle`, `ui.knob`, circular/linear progress | **Expanded 0.15:** progress variants (linear already exists; circular/determinate-indeterminate completeness); knob remains recipe/extra unless a11y evidence is strong. |
| `ui.upload`, `ui.upload_files` | **Covered/planned:** uploads exist; directory upload and capture complete in 0.15. |
| `ui.editor` (Quasar rich text) | **Recipe/plugin:** prefer Markdown/`TrustedHtml` or a bounded extras editor; do not adopt Quasar as a core dependency. |

## Media, maps, and capture

| NiceGUI surface | Hedron disposition |
|---|---|
| `ui.audio`, `ui.video`, image | **Planned 0.15** with captions, range requests, autoplay policy, and accessible alternatives. |
| `ui.interactive_image` | **Planned 0.16** crop/region tools; **expanded 0.16** annotation/overlay events as optional extras when demand holds. |
| Microphone / camera examples | **Planned 0.15** capture inputs with permission denial and retention policy. |
| `ui.leaflet` | **Expanded 0.15:** first-party `Map` / GeoJSON adapter with pinned assets, CSP, attribution, tile/source policy, and keyboard/static alternatives. |
| `app.add_media_files` ranged streaming | **Expanded 0.15:** authorized media/download responses with Range support for players and PDF. |
| `ui.download` | **Expanded 0.15:** typed download helpers (`Content-Disposition`, authz, size limits) composing existing file responses. |

## Layout, chrome, and navigation

| NiceGUI surface | Hedron disposition |
|---|---|
| row/column/grid/card/tabs/expansion/dialog/menu/tooltip | **Covered/planned:** layout primitives, Expander, Tabs, Dialog (0.10), Popover/docks/tooltip (0.15). |
| header/footer/drawer/page_sticky/page_scroller | **Covered/expanded:** landmarks and Sidebar exist; sticky docks are 0.15; drawer-as-sidebar recipe remains composition. |
| `ui.carousel`, lightbox-style galleries | **Expanded 0.15:** `Carousel` and lightbox selection beside responsive `Gallery`. |
| `ui.timeline` | **Expanded 0.15:** semantic `Timeline` / timeline entry composition. |
| `ui.context_menu` | **Expanded 0.15:** accessible context menu with keyboard and non-pointer alternatives. |
| `ui.stepper` / steps | **Planned 0.16** `Steps`. |
| `ui.splitter` | **Planned 0.16** split panes. |
| `ui.tree` | **Planned 0.16** `TreeView`. |
| `ui.fab` | **Planned 0.16** floating action placement. |
| `ui.sub_pages` client routing | **Deliberate non-parity:** explicit routes + HTMX panel-swap / progressive enhancement (0.10/0.19). |
| `ui.teleport` | **Covered equivalently** by OOB updates and addressable regions; no DOM teleport API. |
| `ui.parallax` | **Recipe/plugin:** decorative; not a first-party accessibility obligation. |
| `ui.skeleton`, spinner, separator, space, skip_link | **Covered** (`Skeleton`, Loading/Progress, Divider, spacing in 0.15); skip-link patterns reinforce **0.19**. |

## Data, charts, editors, and specialized views

| NiceGUI surface | Hedron disposition |
|---|---|
| `ui.table`, AG Grid examples | **Covered** via `DataTable` / `DataEditor` and 0.12 scale work. |
| Plotly, Matplotlib, Altair, ECharts, Highcharts, Mermaid | **Covered/partial:** first-party chart adapters exist; Highcharts remains third-party/recipe (licensing). |
| `ui.json_editor` | **Planned 0.16** schema-aware `JSONEditor`. |
| `ui.codemirror` / code editing | **Expanded 0.16:** `CodeEditor` distinct from `CodeBlock`/`CodeViewer`, with CSP, no eval, and language allowlists. |
| `ui.log`, `ui.xterm` | **Planned 0.16** job/log consoles; **specialty extra** for full PTY/`TerminalView` with command-injection policy. |
| `ui.scene` (Three.js) | **Planned 0.16** 3D model adapters; deep scene graphs remain specialty extras. |
| `ui.joystick` | **Specialty extra / recipe** for robotics/IoT; not core beachhead. |
| FullCalendar / signature pad / typeahead examples | **Expanded 0.16** as optional extras or documented recipes over actions + fragments. |

## State, binding, timers, and live updates

| NiceGUI surface | Hedron disposition |
|---|---|
| `app.storage.tab/client/user/general/browser` | **Covered/planned 0.15:** SessionState, host sessions, `BrowserStorage`, named connections. NiceGUI's multi-tier glossary informs migration docs; file-backed global app storage is not reproduced as a framework singleton. |
| Element binding / observables | **Deliberate non-parity** for implicit two-way binding. **0.17** `DashboardBinding` / `InteractionGraph` covers cohesive dashboards with inspectable edges. |
| `ui.refreshable` | **Deliberate non-parity** for magic refresh scopes; addressable fragments + actions are the equivalent. |
| `ui.timer` (including very short intervals) | **Covered with constraints:** polling helpers exist; Supported intervals remain conservative. Sub-100ms timers are not a Supported production promise. |
| WebSocket outbox batching | **Deliberate non-parity** as the primary UI update path. Experimental SSE/WS remain optional; polling is Supported. |
| Lifecycle `on_connect` / `on_disconnect` | **Covered equivalently** by host lifespan, session middleware, and live-transport lifecycle (0.10/0.13) without tying UI correctness to a single worker. |

## App hosting, native mode, and JavaScript escape hatches

| NiceGUI surface | Hedron disposition |
|---|---|
| `ui.run` / `ui.run_with(FastAPI)` | **Covered:** `Hedron(FastAPI)`, uvicorn, adapters; scaffold via CLI. |
| Native desktop window | **Specialty recipe:** optional pywebview (or similar) shell over the ASGI app; not a second renderer. |
| `ui.run_javascript`, client `query` mutation, computed client props | **Deliberate non-parity.** Registered browser modules, typed events, and `TrustedHtml` remain the escape hatches. |
| Tailwind/Quasar `.classes` / `.props` fluency | **Covered differently:** themes, CSS contracts, and explicit class props; Quasar is not a core dependency. |
| Jupyter / interactive mode hosting | **Covered/planned:** 0.16 browser-Python sandbox and 0.17 server-side notebook preview solve adjacent problems without NiceGUI's process model. |

## Testing and developer experience

| NiceGUI surface | Hedron disposition |
|---|---|
| pytest `user` fixture (fast simulated interaction) | **Planned 0.15** `AppScenario` over real HTTP + production renderer. |
| pytest `screen` fixture (Playwright) | **Covered** by browser tests; keep for focus/permission/playback. |
| `ElementFilter` / `.mark()` | **Expanded 0.15:** scenario helpers to mark/query stable component identities and assert markup without inventing a parallel DOM simulator. |
| `llms.md` / `llms.txt` | **DX/docs:** ship an AI-oriented package docs index anytime. |
| Official Docker image / live docs-as-app | **DX/docs:** strengthen Codespaces/Dev Container and optional demo image; docs site remains MkDocs. |

## Deliberate non-parity

The following are not missing planned features:

1. **Vue/Quasar frontend and socket.io outbox as the primary UI protocol.** Hedron remains
   server-rendered HTML with HTMX fragments and ordinary HTTP.
2. **Imperative element trees mutated from Python over a persistent client connection.** Hedron
   returns component trees from handlers; updates are pages, fragments, OOB regions, or declared
   live patches — not a client-side element store.
3. **`ui.run_javascript` and unrestricted client DOM query/mutation.** Trust and CSP boundaries stay
   explicit; registered browser modules replace ad-hoc script injection.
4. **Implicit data binding and refreshable containers.** Declared actions, fragments, and 0.17
   interaction graphs provide inspectable equivalents.
5. **SPA-style `sub_pages` client routing.** Multipage routes and progressive-enhancement panel
   swaps remain the Supported model.
6. **Single-worker assumptions required for correctness.** Hedron targets multi-worker and
   multi-host deployments; UI state that only works in one process is rejected.
7. **Highcharts or other commercially licensed chart runtimes as first-party defaults.**

## Accepted gaps by phase

### Expanded in 0.15

Owning drafts: [RFC-0033](rfcs/RFC-0033-MAP-GEOJSON.md) (maps),
[RFC-0034](rfcs/RFC-0034-MEDIA-DOWNLOAD-RANGE.md) (downloads/Range),
[RFC-0035](rfcs/RFC-0035-SURFACE-CHROME.md) (carousel/timeline/context menu/chips/progress),
[RFC-0036](rfcs/RFC-0036-SCENARIO-MARKS.md) (scenario marks).

- Policy-bounded `Map` / GeoJSON adapter (tiles/sources, attribution, CSP, static/keyboard
  alternatives).
- `Carousel` and lightbox patterns composing with `Gallery`.
- Semantic `Timeline`, accessible `ContextMenu`, chip/tag input, and Progress variants
  (e.g. circular).
- Typed download helpers and authorized Range/streaming media responses for players and PDF.
- Scenario mark/filter ergonomics inspired by NiceGUI `ElementFilter` / `.mark()`.
- NiceGUI migration glossary for storage tiers and control families (alongside the Streamlit
  matrix).

### Expanded in 0.16

Owning drafts: [RFC-0037](rfcs/RFC-0037-CODE-EDITOR-EXTRAS.md) (CodeEditor, calendar/signature/
typeahead, annotation overlays),
[RFC-0038](rfcs/RFC-0038-SPECIALTY-EXTRAS.md) (TerminalView, robotics/IoT, native shell).

- `CodeEditor` (CodeMirror-class) with CSP and no arbitrary eval.
- Signature pad, calendar, and typeahead/combobox as extras or recipes.
- Optional interactive-image annotation overlays beyond crop/region selection.
- Optional `TerminalView` / PTY extra only behind explicit command, authz, audit, and a11y policy.
- Specialty robotics/IoT extras (joystick, deep scene, serial bridges) only if that audience is
  intentional — default disposition remains recipe/plugin.

### Reinterpreted in 0.17

- NiceGUI binding/timer/refreshable ergonomics → finite `DashboardBinding` / `InteractionGraph`
  with polling/SSE fallbacks and Explorer inspectability.
- Maintained NiceGUI migration notes beside the Dash matrix (deliberate non-parity called out).

### DX anytime (no phase gate)

- Package `llms.txt` / AI docs index.
- Optional published demo Docker image complementary to Codespaces/Dev Container.

## Maintenance rule

Refresh this matrix before closing phases **0.15** and **0.16**, and whenever Hedron claims NiceGUI
migration coverage. A newly documented NiceGUI API is classified as covered, equivalent, accepted
gap, specialty extra, DX-only, or deliberate non-parity. Accepted gaps require a phase owner,
security and accessibility boundaries, and an evidence-bearing exit gate before they appear as
Supported.
