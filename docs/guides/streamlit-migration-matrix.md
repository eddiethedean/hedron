# Streamlit → Hedron 0.25 migration matrix

Streamlit widgets and Hedron components solve overlapping UX jobs with different execution
models. Streamlit reruns the script when a widget changes; Hedron handles an HTTP request,
validates inputs, and returns typed server-rendered components (pages or HTMX fragments).
Use this matrix for API-family mapping; for a full rewrite walkthrough see
[Migrate a Streamlit app](streamlit-migration.md).

**Deliberate non-parity:** `st.rerun`, `st.stop`, widget callbacks, and whole-script global
mutable state have no Hedron equivalent by design. Prefer routes, `@action` / `@fragment`,
and explicit session scopes.

**Charts on 0.25:** `hedron-charts` is **source-only / Deferred for PyPI** — do not install
`hedron[charts]` with Hedron 0.25. See
[Compatibility](../COMPATIBILITY.md#current-025-packaging-limitation-charts-and-sample-kit).

| Streamlit | Hedron 0.25 | Notes |
|---|---|---|
| `st.title` / `st.header` / `st.write` | `Heading`, `Text`, `Auto` | Explicit components; no magic write |
| `st.sidebar` | `Sidebar` / layout landmarks | Compose layout; no implicit sidebar slot |
| `st.button` / `st.form_submit_button` | `Button`, `SubmitButton`, `@action` | POST + CSRF; not a script rerun |
| `st.text_input` / `st.text_area` | `TextInput`, `TextArea` | Native submitted values |
| `st.number_input` / `st.slider` | `NumberInput`, `RangeInput`, `SelectSlider` | Typed controls |
| `st.selectbox` / `st.multiselect` | `Select`, `MultiSelect` | |
| `st.checkbox` / `st.toggle` | `Checkbox`, `ToggleSwitch` | |
| `st.radio` / segmented pills | `SegmentedControl`, `Pills` | |
| `st.date_input` / `st.time_input` | `DateInput`, `TimeInput`, `DateTimeInput` | |
| `st.color_picker` | `ColorInput` | |
| `st.file_uploader` | `FileUpload`, `DirectoryUpload` | |
| `st.camera_input` / `st.audio_input` | `CameraCapture`, `MicrophoneCapture` | Permission/retention policy explicit |
| `st.audio` / `st.video` / `st.image` | `Audio`, `Video`, `Image`, `Gallery` | SafeUrl + optional Range downloads |
| `st.download_button` | `DownloadButton`, `media_file_response`, `download_all_zip` | RFC-0034 Range helpers |
| `st.dataframe` / `st.data_editor` | `DataTable` / `DataEditor` (`hedron[data]`) | |
| `st.map` / `st.pydeck_chart` | `Map`, `GeoJSONLayer`, `MarkerSpec` | Table alternative required (RFC-0033) |
| `st.metric` | `Metric` | Supported |
| `st.progress` / spinners | `CircularProgress`, `Loading`, `Poll` | Prefer polling over experimental SSE |
| `st.tabs` / `st.expander` | `Tabs`, `Expander`, `Carousel`, `Timeline` | Carousel/Timeline are 0.15 |
| `st.popover` / menus | `Popover`, `MenuButton`, `ContextMenu`, docks | RFC-0035 |
| `st.chat_input` / messages | `ChatInput`, `ChatMessage` | History is application-owned |
| `st.login` / identity | OIDC / session helpers (`hedron.oidc`, session timeout/CSRF) | Host session authoritative; not an IdP |
| `st.connection` / `st.cache_resource` | Connection registry + host DI/lifespan | No global service locator |
| `st.session_state` | `SessionState` / cookies / `BrowserStorage` | Explicit scopes; storage non-secret |
| `st.fragment` / partial updates | `app.region`, `@fragment`, `swap` | Fail-closed `HX-Target` auth |
| `st.rerun` / callbacks | — | **Non-parity** — use HTTP actions/fragments |
| Testing (`AppTest`) | `AppScenario`, HTMX asserts | Ordinary HTTP; no rerun simulation |

## Suggested migration order

1. Replace top-level layout and metrics with typed pages.
2. Move filters/forms to query params or POST actions (not widget callbacks).
3. Swap tables to `hedron[data]`. Charts are source-only on 0.25 — use `Table` /
   `Metric` from PyPI, or workspace `hedron-charts` (do not install from PyPI).
4. Adopt Map, media helpers, and remaining controls where custom HTML was used.
5. Cover flows with `AppScenario` instead of Streamlit `AppTest` rerun semantics.
