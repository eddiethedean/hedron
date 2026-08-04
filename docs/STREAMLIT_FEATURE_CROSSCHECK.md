# Streamlit feature cross-check

**Audit date:** 2026-08-04<br>
**Streamlit documentation:** 1.60.0 API surface<br>
**Purpose:** identify capability gaps, not promise call-for-call API compatibility

Hedron uses Streamlit as an ergonomics reference for Python data applications. It does not use
Streamlit's whole-script rerun runtime. This audit compares user-visible capability families and
assigns worthwhile gaps to Hedron roadmap phases while retaining explicit routes, actions, state
scopes, authorization, and ordinary HTTP fallbacks.

## Official source baseline

The inventory was built from Streamlit's official documentation:

- [API reference](https://docs.streamlit.io/develop/api-reference)
- [Text elements](https://docs.streamlit.io/develop/api-reference/text)
- [Data elements](https://docs.streamlit.io/develop/api-reference/data)
- [Chart elements](https://docs.streamlit.io/develop/api-reference/charts)
- [Input widgets](https://docs.streamlit.io/develop/api-reference/widgets)
- [Media elements](https://docs.streamlit.io/develop/api-reference/media)
- [Layouts and containers](https://docs.streamlit.io/develop/api-reference/layout)
- [Chat elements](https://docs.streamlit.io/develop/api-reference/chat)
- [Status elements](https://docs.streamlit.io/develop/api-reference/status)
- [Navigation and pages](https://docs.streamlit.io/develop/api-reference/navigation)
- [Caching and state](https://docs.streamlit.io/develop/api-reference/caching-and-state)
- [Connections and databases](https://docs.streamlit.io/develop/api-reference/connections)
- [Authentication](https://docs.streamlit.io/develop/concepts/connections/authentication)
- [Custom Components](https://docs.streamlit.io/develop/api-reference/custom-components)
- [App testing](https://docs.streamlit.io/develop/concepts/app-testing)

Community components and Streamlit Community Cloud are not treated as framework APIs. A named
third-party component is evidence of demand, not an automatic first-party Hedron commitment.
The separately maintained
[streamlit-extras feature cross-check](STREAMLIT_EXTRAS_FEATURE_CROSSCHECK.md) audits that official
community catalog entry by entry and assigns accepted specialized tools to phase 0.16.

## Result summary

| Streamlit capability family | Hedron disposition | Coverage or owner |
|---|---|---|
| Write, text, HTML | Mostly covered | `Auto`, typed content, `Markdown`, code, trusted HTML; math/help/iframe added to 0.15 |
| Data display and editing | Covered, with depth scheduled | `DataTable`, `DataEditor`, `Metric`, `JSONViewer`; rich column catalog added to 0.12 |
| Charts and maps | Partial | Line/Matplotlib/Plotly/Altair exist; missing beginner charts and adapters added to 0.12 |
| Input widgets | Partial | Core forms and model-derived controls exist; remaining typed controls added to 0.15 |
| Media and capture | Partial | Image processing and file upload exist; players/PDF/capture added to 0.15 |
| Layout and containers | Mostly covered | Semantic layout, sidebar, tabs, expander exist; dialog added to 0.10 and popover/docks to 0.15 |
| Chat and streaming | Missing but architecturally adjacent | Chat transcript/input and bounded token streams added to 0.10 |
| Status | Covered | `Alert`, `Progress`, `Loading`, `Status`, `Skeleton`, `Toast`; decorative celebrations excluded |
| App server | Covered with broader control | `Hedron` is FastAPI/Starlette-based; Flask and Django adapters also exist |
| Authentication | Low-level coverage only | Authlib helpers exist; OIDC login/logout/claims conveniences added to 0.15 |
| Navigation and pages | Covered | Explicit routes, `Page`, navigation components, safe links, redirects, history and fragments |
| Execution flow | Equivalent, not identical | Forms, fragments, polling/jobs, and 0.10 live interaction; rerun/stop deliberately excluded |
| Caching and state | Mostly covered | Typed session/query/request/cache scopes; browser context completed in 0.15 |
| Connections and secrets | Partial/equivalent | SQLAlchemy source and host secrets/DI exist; named connection ergonomics added to 0.15 |
| Custom components | Covered with different trust model | Web Components, browser modules, package assets, typed events, plugins, lifecycle cleanup |
| Configuration and theming | Covered | Versioned project config, constructor/env precedence, themes, dark/light preference, page metadata |
| Testing and CLI | Covered | Render/fragment/browser/a11y helpers, Explorer, snapshots, diagnostics, scaffold/dev/build/check CLI |

## Detailed cross-check

### Write and text

| Streamlit APIs | Hedron equivalent | Disposition |
|---|---|---|
| `st.write`, magic | Explicit `Auto(value)` or a typed component returned from a route | Covered; side-effect emission and magic are deliberately excluded |
| Markdown, title/header/subheader, badge, caption, text, divider | `Markdown`, `Heading`, `Badge`, `Text`, `Divider` | Covered |
| Code, echo | `CodeBlock`, `CodeViewer`, Explorer source/examples | Covered by composition; no execute-while-echoing context manager |
| HTML | `html` namespace and `html.raw(TrustedHtml)` | Covered with a stronger trust boundary |
| LaTeX | No dedicated component | Added to 0.15 as `Math` / LaTeX |
| Object help | Explorer and Python introspection, but no bounded in-app viewer | Added to 0.15 |
| Iframe | Native escape hatch exists, but no policy-rich component | Added to 0.15 as sandboxed `IFrame` |

### Dataframes, editors, and metrics

`DataTable`, `DataEditor`, typed changes, pagination, sorting, filtering, virtualization,
validation, optimistic concurrency, Pandas/Polars/PyArrow normalization, `Metric`, and
`JSONViewer` already cover the principal data APIs.

Streamlit's `st.column_config` exposes a broader catalog of display/editor types than Hedron's
current `Field` and editor-column surface. Phase 0.12 now owns a shared typed column catalog for
number, text, checkbox, list/select, date/time, link, image, progress, and compact chart columns.
Display configuration never grants write authorization.

### Charts, diagrams, maps, and events

| Streamlit APIs | Hedron status before audit | Roadmap disposition |
|---|---|---|
| Line chart | `LineChart` | Covered |
| Area, bar, scatter | No first-party beginner component | Added to 0.12 |
| Matplotlib, Plotly, Altair | Adapters exist | Covered; offline runtime hardening remains required |
| Direct Vega-Lite | Altair adapter only | Added to 0.12 |
| Map / PyDeck | Geospatial work planned, PyDeck not named | PyDeck/deck.gl explicitly added to 0.12 |
| GraphViz, Mermaid | Not planned | Added to 0.12 |
| Selection/click events | No stable chart event boundary | Typed, authorized event contract added to 0.12 |

ECharts, Datashader, MapLibre, Folium, Bokeh, HoloViews/hvPlot, Pygal, Plotly resampling, and
advanced Vega transforms were already assigned to 0.12.

### Input controls

Hedron already has buttons, link/icon/refresh/submit buttons, text input, text area, select,
checkbox, radio group, file upload, data editor, pagination, automatic model forms, and native HTML
escape hatches. Phase 0.15 now owns ergonomic typed controls for:

- number, slider, range, select-slider, date, datetime, and time input;
- multiselect, toggle/switch, segmented control, and pill selection;
- color input and rating/feedback;
- menu-button behavior.

These are submitted controls tied to URL/form/action inputs. They do not return a value from a
long-lived widget actor or trigger an application-wide rerun.

`st.chat_input`, microphone input, and camera input require interaction/media policy beyond ordinary
forms and are assigned separately to 0.10 and 0.15.

### Media and capture

Hedron already has `Image`, optional Pillow processing, `FileUpload`, `DownloadButton`, trusted SVG
and icon registries, and a fingerprinted local asset pipeline. Phase 0.15 adds:

- audio and video players;
- a PDF viewer with download fallback;
- application logo/page-icon helpers; and
- microphone and camera capture inputs.

Unlike a convenience-only wrapper, these contracts must define range requests, size and format
limits, autoplay, captions/transcripts, device permission denial, retention, upload authorization,
CSP, and accessible alternatives.

### Layout, chat, and status

`Container`, `Stack`, `Inline`, `Grid`, semantic landmarks, `Sidebar`, `Expander`, `Tabs`, cards,
loading/error states, `Alert`, `Progress`, `Status`, `Skeleton`, and `Toast` are present.

Phase 0.10 now includes modal `Dialog`, `ChatMessage`, `ChatInput`, optional attachments, and bounded
generator/token-stream output using explicit actions and polling/SSE fallbacks. Phase 0.15 adds
popover, sticky/bottom dock, and spacing primitives. Focus restoration, virtual-keyboard behavior,
safe-area insets, and fragment lifecycle are part of the contracts.

`st.empty` is a mutable delta-generator primitive tied to Streamlit's execution model. Hedron uses
addressable fragment targets, out-of-band updates, and typed interaction results instead. Balloons
and snow are decorative effects and remain application CSS/Web Component/plugin territory.

### App, identity, navigation, execution, and state

- `Hedron()` already provides a FastAPI/Starlette application with middleware, lifecycle, custom
  routes, OpenAPI, async I/O, security policy, and standard deployment. Streamlit's experimental
  ASGI app surface does not reveal a Hedron gap.
- Explicit page routes, `Page`, `Nav`, safe links, redirects, route reversal, history, and HTMX
  fragments cover multipage navigation without filesystem-driven hidden routing.
- Forms, fragment endpoints, lazy resources, polling, jobs, redirects, and live transports cover
  the useful outcomes of Streamlit dialogs/fragments. `st.rerun`, `st.stop`, widget callbacks, and
  whole-script reruns are deliberately not reproduced.
- URL/query state, typed form/action state, `SessionState`, cache scopes, browser-local Web
  Component state, and application databases cover Streamlit query/session state with clearer
  ownership boundaries.
- FastAPI/Flask/Django request objects already expose headers, cookies, URL, and client information.
  Phase 0.15 adds a portable `BrowserContext` for browser-reported locale, timezone, color mode,
  embed state, and related hints while treating them as spoofable, privacy-sensitive inputs.
- The existing Authlib helpers are deliberately low-level. Phase 0.15 adds secure OIDC
  login/logout/user-claims conveniences, but authorization and identity storage remain application
  responsibilities.

### Caching, connections, secrets, components, and tools

- `cache_data` and `cache_component` provide scoped keys, invalidation, single flight, external
  backends, private authenticated defaults, and diagnostics. Long-lived models and clients belong
  to host dependency injection and lifespan rather than a copy of `st.cache_resource`.
- SQLAlchemy/SQLModel sources exist and the data-source protocols are extensible. Phase 0.15 adds a
  named typed resource/connection registry over host DI/lifespan, external secret-manager hooks,
  reset/health semantics, and optional SQLAlchemy/Snowflake providers. It may not become a global
  service locator, ORM, transaction owner, or secret singleton.
- Hedron's Web Components, browser modules, typed custom events, Shadow/light DOM policy, package
  assets, plugins, HTMX lifecycle cleanup, and conformance tests cover the capability of Streamlit
  custom components while preserving Hedron's stricter executable-code and CSP boundaries.
- Versioned configuration, themes, page metadata, CLI/Explorer inspection, pytest helpers,
  snapshots, Playwright hooks, and accessibility/visual checks already cover Streamlit's
  configuration and app-testing families.

## Deliberate non-parity

The following are not missing planned features:

1. **Whole-script reruns, `st.rerun`, and `st.stop`.** Hedron uses an HTTP request/action/fragment
   boundary. Reproducing reruns would introduce a second, conflicting runtime.
2. **Magic and global side-effect emission.** Hedron returns explicit component trees; `Auto` is the
   intentional low-friction renderer.
3. **Implicit widget/session coupling.** Submitted values and state scopes stay explicit and typed.
4. **A global secret singleton or opaque connection cache.** Host secret managers, dependency
   injection, lifespan, and scoped resources remain authoritative.
5. **Decorative balloons/snow.** Applications and plugins can implement them without expanding the
   first-party accessibility and motion surface.
6. **Streamlit Community Cloud and Snowflake-hosted runtime behavior.** These are vendor deployment
   products, not portable framework features. Portable Snowflake data access is in scope.

## Maintenance rule

Refresh this matrix before closing phases 0.10, 0.12, and 0.15 and whenever Hedron claims broader
Streamlit migration coverage. A newly documented Streamlit API is classified as covered,
equivalent, accepted gap, or deliberate non-parity. Accepted gaps require a phase owner, security
and accessibility boundaries, and an evidence-bearing exit gate before they appear as Supported.
Refresh the separate streamlit-extras matrix before closing phase 0.16.
