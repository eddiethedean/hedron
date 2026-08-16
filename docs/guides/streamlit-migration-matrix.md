# Streamlit → Hedron migration matrix

Use this page to find the closest Hedron path for a Streamlit API. It is a migration aid,
not a claim of call-for-call compatibility. The execution model, state ownership, and
deployment model still change.

Start with the [migration overview](streamlit-migration.md), especially if you have not
yet decided whether Hedron fits the app. For callbacks, reruns, state, and caches, read
[Execution and state](streamlit-execution-state.md) rather than relying on a one-line map.

## How to read the matrix

| Label | Meaning |
|---|---|
| **Direct** | A first-party Hedron component handles substantially the same UI job. |
| **Equivalent** | The user outcome is supported through explicit routes, forms, HTTP, or host-framework services. |
| **Partial** | A narrower path exists or the 0.27 packaging/maturity boundary matters. Test before committing. |
| **No parity** | Hedron deliberately does not reproduce the mechanism. Redesign around explicit requests and state. |

The audit baseline is Streamlit's official 1.60.0 documentation. Check the maintained
[feature cross-check](https://github.com/eddiethedean/hedron/blob/main/docs/STREAMLIT_FEATURE_CROSSCHECK.md)
for exhaustive research and the
[streamlit-extras cross-check](https://github.com/eddiethedean/hedron/blob/main/docs/STREAMLIT_EXTRAS_FEATURE_CROSSCHECK.md)
for community packages.

## Text, layout, and navigation

| Streamlit | Closest Hedron path | Fit | Migration note |
|---|---|---|---|
| `st.title`, `st.header`, `st.subheader` | `Heading` | **Direct** | Choose the explicit heading level; preserve one logical page `h1`. |
| `st.write`, magic | `Auto`, `Text`, `Markdown`, or a typed component | **Equivalent** | Return components; Hedron does not emit UI as a global side effect. |
| `st.markdown` | `Markdown` | **Direct** | Use trusted HTML only at an explicit trust boundary. |
| `st.code`, `st.json` | `CodeBlock`/`CodeViewer`, `JSONViewer` | **Direct** | Keep size and secret-redaction limits explicit. |
| `st.sidebar` | `Sidebar` | **Direct** | Compose it into the page; there is no implicit global sidebar slot. |
| `st.columns`, `st.container` | `Grid`, `Inline`, `Stack`, `Container` | **Direct** | Components are children, not mutable column handles. |
| `st.tabs`, `st.expander`, `st.popover` | `Tabs`, `Expander`, `Popover` | **Direct** | Check keyboard/focus behavior after fragment updates. |
| `st.empty`, placeholders | Declared region + fragment/OOB update | **Equivalent** | Replace a stable region; do not mutate a global placeholder object. |
| `st.Page`, `st.navigation`, `pages/` | `@app.page` routes + navigation components | **Equivalent** | Declare stable paths and enforce authorization in route dependencies. |
| `st.page_link`, `st.switch_page` | `Link`/navigation + redirect response | **Equivalent** | Validate redirect targets; use 303 after successful POST. |
| `st.set_page_config` | `Hedron(...)`, `Page(..., title=...)`, theme/config | **Equivalent** | App-wide and page-specific metadata are explicit. |

## Inputs and forms

| Streamlit | Closest Hedron path | Fit | Migration note |
|---|---|---|---|
| `st.button` | `SubmitButton`/button inside `Form` + `@app.action` | **Equivalent** | Put side effects in POST handlers, not page rendering. |
| `st.form`, `st.form_submit_button` | `Form`, `FormField`, `SubmitButton` | **Direct** | Use GET for safe filters and POST for writes; CSRF applies to unsafe methods. |
| `st.text_input`, `st.text_area` | `TextInput`, `TextArea` | **Direct** | Bind submitted values to typed route/form models. |
| `st.number_input` | `NumberInput` | **Direct** | Repeat bounds in server-side validation. |
| `st.slider` | `RangeInput` | **Direct** | A submitted control; add HTMX if immediate refresh is valuable. |
| `st.select_slider` | `SelectSlider` | **Direct** | Values arrive through a request rather than a widget return value. |
| `st.selectbox`, `st.multiselect` | `Select`, `MultiSelect` | **Direct** | Persist selected options in query/form/session state deliberately. |
| `st.checkbox`, `st.toggle` | `Checkbox`, `ToggleSwitch` | **Direct** | Treat mutations as POST even if the control looks lightweight. |
| `st.radio`, `st.segmented_control`, `st.pills` | `RadioGroup`, `SegmentedControl`, `Pills` | **Direct** | Preserve labels and keyboard semantics. |
| `st.date_input`, `st.time_input` | `DateInput`, `TimeInput`, `DateTimeInput` | **Direct** | Validate timezone and range assumptions on the server. |
| `st.color_picker`, `st.feedback` | `ColorInput`, `RatingInput` | **Direct** | Never rely on color alone to convey meaning. |
| `st.file_uploader` | `FileUpload`, `DirectoryUpload` | **Equivalent** | Process in an explicit upload action with size, type, and authorization policy. |
| `st.camera_input`, `st.audio_input` | `CameraCapture`, `MicrophoneCapture` | **Partial** | Define permission-denial, retention, format, and upload limits. |

## Data, charts, and media

| Streamlit | Closest Hedron path | Fit | Migration note |
|---|---|---|---|
| `st.metric` | `Metric` | **Direct** | Pass label, formatted value, and optional delta. |
| `st.dataframe` | `DataTable` from `hedron[data]`; `Table` for small static data | **Direct** | Declare a row `Model` when stable types matter. |
| `st.data_editor` | `DataEditor` from `hedron[data]` | **Partial** | Wire persistence, authorization, validation, and concurrency explicitly. |
| `st.column_config` | Hedron data field/column configuration | **Partial** | Verify each specialized column type; do not assume complete Streamlit parity. |
| `st.line_chart`, `st.area_chart`, `st.bar_chart`, `st.scatter_chart` | Hedron chart components | **Partial** | Install `hedron[charts]>=0.45.0,<0.46`; provide accessible titles/descriptions/fallbacks. |
| `st.plotly_chart`, `st.altair_chart`, `st.pyplot` | `PlotlyChart`, `AltairChart`, `MatplotlibChart` | **Partial** | Matplotlib/static is the conservative default; Plotly/Altair remain experimental. |
| `st.map`, `st.pydeck_chart` | `Map`, `GeoJSONLayer`, marker/layer specs | **Partial** | Supply a table/text alternative and bound payloads. |
| `st.image`, `st.audio`, `st.video` | `Image`, `Gallery`, `Audio`, `Video` | **Direct** | Use safe sources, alt text, captions/transcripts, and media budgets. |
| `st.download_button` | `DownloadButton` + download response helpers | **Equivalent** | Authorize the response; do not expose arbitrary filesystem paths. |
| `st.graphviz_chart`, Mermaid | Optional chart/diagram adapters or pre-rendered safe media | **Partial** | Check package availability and CSP before migration. |

!!! note "Hedron 0.27 chart floor"

    Use `hedron[charts]>=0.45.0,<0.46`, which enforces
    `hedron-charts>=0.2.0,<0.3`. See
    [Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).

## Status, chat, and long-running work

| Streamlit | Closest Hedron path | Fit | Migration note |
|---|---|---|---|
| `st.success`, `st.info`, `st.warning`, `st.error` | `Alert`, status/error components | **Direct** | Return the state from the request that produced it. |
| `st.spinner`, `st.status` | `Loading`, `Status`, `Skeleton` | **Equivalent** | For long work, create a job and poll rather than holding the request open. |
| `st.progress` | `Progress`/`CircularProgress` + `Poll` | **Equivalent** | Store progress outside the component and bound polling frequency. |
| `st.toast` | `Toast` / `swap(..., toast=...)` | **Direct** | Important outcomes also need persistent, accessible content. |
| `st.chat_message`, `st.chat_input` | `ChatMessage`, `ChatInput` | **Partial** | Transcript storage, auth, model calls, and rate limits remain application-owned. |
| `st.write_stream` | Polling-first job/log/token output; experimental live helpers | **Partial** | Prefer polling; SSE/WebSocket/streaming remain experimental on FastAPI. |
| `st.balloons`, `st.snow` | Application CSS/plugin if justified | **No parity** | Decorative motion is deliberately outside core and must honor reduced motion. |

## Execution, state, caching, and services

| Streamlit | Closest Hedron path | Fit | Migration note |
|---|---|---|---|
| Default widget rerun | GET page/fragment or POST action | **Equivalent** | Translate the user's intent, not the rerun mechanism. |
| `st.fragment` | `app.region`, `@app.fragment`, `swap(...)` | **Equivalent** | A distinct HTTP request returns HTML for an allowlisted target. |
| `st.dialog` | `Dialog` + explicit fragment/action | **Equivalent** | Preserve focus, close behavior, and no-JS outcome where critical. |
| `st.rerun` | Fragment response or POST→303 redirect | **No parity** | Do not add a hidden rerun loop. |
| `st.stop` | Validation/early return/HTTP exception | **No parity** | Make the response state explicit. |
| Widget `on_change` / `on_click` | GET fragment/page or POST action | **Equivalent** | Choose method based on whether it is safe or mutating. |
| `st.session_state` | Query params, `SessionState[T]`, database, cache, or browser preference | **Equivalent** | Classify every key; do not copy the dictionary wholesale. |
| `st.query_params` | Typed FastAPI path/query parameters | **Direct** | Inputs become addressable and validated. |
| `st.cache_data` | `cache_data` | **Equivalent** | Re-evaluate TTL, scope, copy/mutation assumptions, keys, and invalidation. |
| `st.cache_resource` | FastAPI lifespan + dependency injection | **Equivalent** | Long-lived clients/models need concurrency-safe lifecycle management. |
| `st.connection` | Host DI/lifespan or typed connection registry | **Equivalent** | No implicit global service locator. |
| `st.secrets` | Environment variables / platform secret manager | **Equivalent** | Never commit or bake secrets into an image. |
| `st.context` | FastAPI `Request` + typed browser context | **Equivalent** | Treat browser-reported values as spoofable input. |

## Authentication, extensions, testing, and deployment

| Streamlit | Closest Hedron path | Fit | Migration note |
|---|---|---|---|
| `st.login`, `st.logout`, `st.user` | OIDC/session helpers + host auth dependencies | **Equivalent** | Hedron is not an identity provider; authorization stays app-owned. |
| Streamlit custom component | Web Component/browser module, Hedron component package, or plugin | **Partial** | Review assets, CSP, events, teardown, accessibility, and server trust. |
| `streamlit-extras` | Core composition, `hedron-extras`, recipe, or plugin | **Partial** | Check the [extras audit](https://github.com/eddiethedean/hedron/blob/main/docs/STREAMLIT_EXTRAS_FEATURE_CROSSCHECK.md) entry by entry. |
| `st.testing.v1.AppTest` | `TestClient`, render helpers, `AppScenario`, HTMX assertions | **Equivalent** | Test HTTP contracts; use browser tests only where needed. |
| `streamlit run app.py` | `uvicorn app:app` | **Equivalent** | The entrypoint is an ASGI application object. |
| Streamlit Community Cloud | Your ASGI/container platform | **No parity** | Hedron has no managed hosting product; plan secrets, TLS, health, workers, logs, and rollback. |

## Recommended migration order

1. Extract calculations, data access, and mutations from `st.*` calls.
2. Port the read-only page and compare outputs against fixed fixtures.
3. Move shareable filters to typed GET parameters and a GET form.
4. Move writes to authorized, CSRF-protected POST actions.
5. Assign former Session State keys to URL, request, session, database, cache, or browser storage.
6. Replace tables and only then evaluate chart/package constraints.
7. Add HTMX fragments for the regions that benefit from independent refresh.
8. Convert `AppTest` outcomes into unit, HTTP, scenario, and minimal browser tests.
9. Follow the [production cutover checklist](streamlit-cutover.md).
