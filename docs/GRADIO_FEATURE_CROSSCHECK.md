# Gradio feature cross-check

**Audit date:** 2026-08-06<br>
**Gradio baseline:** 6.22.0 (reconfirmed against PyPI; still current stable)<br>
**Scope:** Gradio core, Python and JavaScript clients, Server mode, MCP support, Workflow,
and the current official documentation<br>
**Purpose:** identify useful capability gaps, not reproduce Gradio's component/event runtime or
Hugging Face hosting services

## Phase 0.18 RFC ownership

Accepted gaps for phase 0.18 map to owning RFCs as follows:

| Gradio / Hedron outcome | Owning RFC |
|---|---|
| `Interface` / callable-to-demo → `InferenceInterface` / `ModelDemo` | [RFC-0045](rfcs/RFC-0045-INFERENCE-INTERFACE.md) |
| Examples, feedback, labels, parameter viewer, dialogue, galleries | [RFC-0046](rfcs/RFC-0046-MODEL-DEMO-PRESENTATION.md) |
| Queue / admission / batch / concurrency → `InferencePolicy` over `JobBackend` | [RFC-0047](rfcs/RFC-0047-INFERENCE-POLICY.md) |
| API / interaction recorder (redacted public endpoints) | [RFC-0048](rfcs/RFC-0048-INTERACTION-RECORDER.md) |
| Gradio protocol adapter + migration inventory (`hedron-gradio`) | [RFC-0049](rfcs/RFC-0049-GRADIO-ADAPTER.md) |
| `Workflow` → versioned permissioned inference workflow | [RFC-0050](rfcs/RFC-0050-INFERENCE-WORKFLOW.md) |

Gradio is a valuable comparison for Hedron because it optimizes for turning a model or Python
function into a shareable demo with very little code. Hedron is a general component and
request/action framework with explicit routes, authorization, rendering, state, and deployment
ownership. This audit therefore compares user outcomes and operational guarantees rather than
requiring class-for-class compatibility.

## Official source baseline

The audit uses Gradio's first-party documentation, package metadata, and repository:

- [Gradio 6.22.0 package and release metadata](https://pypi.org/project/gradio/6.22.0/)
- [Gradio documentation](https://www.gradio.app/docs)
- [Gradio source repository](https://github.com/gradio-app/gradio)
- [Gradio changelog](https://www.gradio.app/changelog)
- [Gradio 6 migration guide](https://www.gradio.app/guides/gradio-6-migration-guide)
- [`Interface`](https://www.gradio.app/docs/gradio/interface),
  [`ChatInterface`](https://www.gradio.app/docs/gradio/chatinterface),
  [`Blocks`](https://www.gradio.app/docs/gradio/blocks), and
  [`Workflow`](https://www.gradio.app/guides/workflows)
- [Queuing](https://www.gradio.app/guides/queuing),
  [batch functions](https://www.gradio.app/guides/batch-functions),
  [streaming outputs](https://www.gradio.app/guides/streaming-outputs), and
  [streaming inputs](https://www.gradio.app/guides/streaming-inputs)
- [State](https://www.gradio.app/guides/state-in-blocks),
  [examples](https://www.gradio.app/docs/gradio/examples), and
  [flagging](https://www.gradio.app/guides/using-flagging)
- [Python client](https://www.gradio.app/docs/python-client/introduction),
  [JavaScript client](https://www.gradio.app/guides/getting-started-with-the-js-client), and
  [View API page](https://www.gradio.app/guides/view-api-page)
- [Server mode](https://www.gradio.app/guides/server-mode),
  [MCP server](https://www.gradio.app/guides/building-mcp-server-with-gradio), and
  [mounting in FastAPI](https://www.gradio.app/docs/gradio/mount_gradio_app)
- [Authentication](https://www.gradio.app/guides/sharing-your-app#authentication),
  [file access](https://www.gradio.app/guides/file-access), and
  [sharing and hosting](https://www.gradio.app/guides/sharing-your-app)
- [Custom components](https://www.gradio.app/guides/custom-components-in-five-minutes),
  [custom HTML components](https://www.gradio.app/guides/custom-HTML-components), and
  [custom CSS and JavaScript](https://www.gradio.app/guides/custom-CSS-and-JS)

The baseline is the latest stable release available on the audit date. Hugging Face Spaces,
ZeroGPU, model/dataset hosting, share-tunnel infrastructure, analytics, and Hub publishing are
vendor services rather than portable framework features. Their useful integration points are
still assessed.

## Disposition rules

- **Covered/equivalent:** Hedron already supplies the outcome, sometimes through normal HTML,
  explicit routes/actions, or a different framework mechanism.
- **Expanded existing phase:** the audit found a concrete omission in a coherent phase already on
  the roadmap.
- **Planned 0.18:** the capability belongs to the new model-demo and inference-workflow packet.
- **Recipe/plugin:** public Hedron composition or an optional vendor adapter can provide it without
  a first-party core runtime API.
- **Deliberate non-parity:** the Gradio mechanism conflicts with Hedron's explicit exposure,
  authorization, state, security, accessibility, or no-arbitrary-JavaScript boundary. The useful
  outcome may still be covered by a safer Hedron mechanism.

## Executive result

| Gradio capability family | Hedron result |
|---|---|
| `Blocks`, layouts, ordinary controls, content, forms, themes | Covered across 0.1–0.6 and 0.15–0.16; Hedron retains semantic HTML and ordinary request/action fallbacks. |
| `Interface` callable-to-demo composition | Genuine ergonomic gap; accepted in 0.18 as an explicit typed `InferenceInterface`, not automatic publication of an arbitrary callable. |
| `ChatInterface`, multimodal chat, streamed messages | Mostly covered by 0.10 and 0.15; 0.18 adds model-demo evaluation composition rather than a second chat runtime. |
| Examples, sample datasets, cached example outputs | Accepted in 0.18 as versioned `ExampleSet`/`ModelDemo` contracts with provenance and cache invalidation. |
| Flagging, like/dislike, and correction capture | Basic feedback control exists; accepted in 0.18 as explicit-consent `PredictionFeedback` sinks with retention, redaction, and tenant policy. |
| Queue, concurrency groups, batch functions, progress, cancellation, generator output | General jobs and streams are covered; model-aware admission, queue position/ETA, batch windows, and resource pools are accepted in 0.18 over `JobBackend`. |
| Camera/microphone input and chunked audio/video output | Capture is planned in 0.15; timed media input/output sessions and backpressure are made explicit in 0.10. |
| Gallery, ranked prediction labels, parameter viewer, dialogue transcripts | Useful ML-demo presentation gaps; assigned to 0.18, with a general responsive media gallery added to 0.15. |
| Python/JavaScript clients, API docs, OpenAPI, API recorder | FastAPI/OpenAPI already cover the protocol; 0.18 adds interaction recording and optional Gradio remote interoperability. |
| `Server`, FastAPI mounting, authentication | Covered by Hedron's FastAPI/adapters and OIDC. Coexistence and migration guidance belong to 0.18. |
| MCP tools/resources/prompts | Already planned in 0.17 with a stronger disabled-and-empty, explicit-opt-in security boundary. |
| `Workflow` visual AI pipeline builder | Genuine gap; accepted in 0.18 as a typed, versioned, permissioned inference DAG over explicit actions and adapters. |
| Custom components | Covered by package/plugin/Web Component contracts; Gradio's Node/Svelte toolchain is not required by Hedron core. |
| Raw HTML/JavaScript and browser-side Python snippets | Deliberate non-parity for arbitrary code. Use `TrustedHtml`, HDJ, registered browser modules, components, or the isolated 0.16 browser-Python sandbox. |
| Share links, Space duplication, Hub OAuth buttons, ZeroGPU | Vendor/infrastructure integrations, not portable first-party parity targets. |
| Vibe mode that can edit files and run host code | Deliberate non-parity in the application runtime. Reviewable code-generation tooling may exist outside a deployed app. |

## App builders and composition

| Gradio surface | Hedron disposition |
|---|---|
| `Interface(fn, inputs, outputs)` | **Planned 0.18:** `InferenceInterface` derives a reviewable form/result demo from an explicitly registered typed action or callable adapter. Input/output schemas, preprocessing, postprocessing, side effects, authorization, rate/resource policy, and HTTP/MCP exposure remain explicit. |
| Live/reactive `Interface` | **Covered with constraints:** 0.17 bindings can debounce an idempotent declared action. Arbitrary execution on each keystroke is not inferred and must have rate, cancellation, stale-result, and resource policy. |
| Multiple inputs and outputs | **Covered:** typed models, forms, actions, multi-region results, artifacts, and 0.17 bindings already provide this. |
| `ChatInterface` | **Covered/0.18 composition:** 0.10 owns chat messages, attachments, streamed output, cancellation, and transport fallback. 0.18 adds examples, feedback, model metadata, and inference scheduling around the same components. |
| Multimodal chat | **Covered/planned:** files and images exist; audio/video/camera/microphone complete in 0.15. Content-type, size, retention, authorization, and model preprocessing are explicit. |
| Editable/retry/undo chat history | **Covered/0.17:** explicit transcript actions and stable message identity can edit, retry, undo, copy, or branch. Application-owned history avoids hidden provider state. |
| `TabbedInterface` | **Covered:** accessible tabs, panels, pages, and composition. App-wide shared state is not inferred from tab membership. |
| `Blocks` | **Covered by a different model:** typed components, slots/fragments, layout primitives, actions, browser components, HDJ, and plugins provide low-level composition without serializing a universal client callback tree. |
| `@gr.render` dynamic layouts and keyed preservation | **Covered/0.17 equivalent:** explicit fragments, structured dynamic collections, stable identity, and declared preservation own the outcome. Hedron does not rerun a layout function as a hidden application scope. |
| `Workflow` | **Planned 0.18:** an optional visual inference workflow composes typed action/model/remote/dataset nodes with versioned ports and graph artifacts. Published and editable graphs have separate authorization. |
| `Server` | **Covered:** FastAPI endpoints, async/generators, OpenAPI, jobs, SSE, middleware, DI, and 0.17 MCP projection already provide the portable server outcome. |

## Complete component cross-check

Gradio 6.22.0 documents 46 core components in its component catalog. Layouts and helpers are
assessed separately.

| Gradio component | Hedron disposition |
|---|---|
| `AnnotatedImage` | **Covered/planned 0.12/0.16:** image overlays, typed annotations, and bounded region selections. |
| `Audio` | **Planned 0.15; expanded 0.10:** playback/upload/capture plus bounded chunked streams, codecs, timing, backpressure, and fallback. |
| `BarPlot` | **Planned 0.12:** beginner chart and visualization-adapter contracts. |
| `Button` | **Covered:** semantic button/link/submit/action variants. |
| `Chatbot` | **Planned 0.10:** typed transcript, messages, tool/status content, attachments, retry/edit/copy actions, and streamed output. |
| `Checkbox` | **Covered:** typed form field with server validation. |
| `CheckboxGroup` | **Covered/0.15:** typed multi-choice controls and richer choice presentation. |
| `ClearButton` | **Covered:** explicit form/reset/clear action with browser and server semantics. |
| `Code` | **Covered:** escaped code viewer, highlighting adapter, copy, download, and bounded editing where explicitly enabled. |
| `ColorPicker` | **Planned 0.15:** native color input with validation and fallback. |
| `Dataframe` | **Covered:** `DataTable`/`DataEditor`, data-source adapters, typed columns, editing, selection, import/export, and bounds. |
| `Dataset` | **Planned 0.18:** `ExampleSet` provides gallery/table samples, selection, pagination, partial inputs, and provenance. General datasets remain data sources, not UI-global mutable objects. |
| `DateTime` | **Planned 0.15:** typed date/time/datetime controls with locale and validation. |
| `Dialogue` | **Planned 0.18:** editable/display-only multi-speaker transcript with typed speaker identity, tags, timestamps, diarization metadata, accessible color-independent labeling, and text export. |
| `DownloadButton` | **Covered:** authorized, typed download responses with content type, filename, streaming, and size policy. |
| `Dropdown` | **Covered/0.15:** select, multiselect, search, clearability, typed options, and fallback. |
| `DuplicateButton` | **Recipe/plugin:** duplicating a Hugging Face Space is a Hub operation, not a portable UI primitive. |
| `File` | **Covered:** bounded uploads, temporary ownership, content validation, authorization, cleanup, and safe download responses. |
| `FileExplorer` | **Covered by composition/0.16:** tree/list views can browse an explicitly virtualized application source. Arbitrary host-filesystem browsing is prohibited. |
| `Gallery` | **Expanded 0.15:** responsive image/video gallery with captions, preview, selection, authorized upload/download, download-all budgets, lazy loading, and accessible list fallback. |
| `HighlightedText` | **Planned 0.16:** token/weighted/annotated text adapter. |
| `HTML` | **Covered with a stronger boundary:** escaped native nodes are normal; `TrustedHtml` and HDJ are explicit trusted-author boundaries. Raw user-derived HTML/JS is not accepted. |
| `Image` | **Covered/planned 0.15:** display/upload plus camera capture, metadata, limits, orientation, and accessible alternative. |
| `ImageEditor` | **Planned 0.16:** crop/selection tools; a full layer editor remains an optional specialized component with decode, memory, and export limits. |
| `ImageSlider` | **Planned 0.16:** accessible before/after image comparison. |
| `JSON` | **Covered/0.16:** bounded viewer plus schema-aware editor. |
| `Label` | **Planned 0.18:** ranked prediction labels/scores with stable class identity, precision, threshold/calibration metadata, and an accessible table representation. |
| `LinePlot` | **Covered/planned 0.6/0.12:** visualization adapter and beginner charts. |
| `LoginButton` | **Covered/recipe:** 0.15 OIDC helpers provide portable login/logout; a Hugging Face-specific button belongs in an optional provider package. |
| `Markdown` | **Covered:** sanitized Markdown adapter with local assets and an explicit trust policy. |
| `Model3D` | **Planned 0.12:** Three.js/model-viewer adapter with format, URL, payload, camera, and accessible fallback policy. |
| `MultimodalTextbox` | **Covered/planned 0.10/0.15:** chat input composes text and bounded attachments/capture. |
| `Navbar` | **Covered:** `Page`, `Nav`, links, routes, responsive layout, and accessible disclosure patterns. |
| `Number` | **Planned 0.15:** typed numeric input with bounds, step, validation, and native fallback. |
| `ParamViewer` | **Planned 0.18:** model/action parameter documentation is generated from typed schemas with defaults, descriptions, anchors, secret redaction, and language-neutral examples. |
| `Plot` | **Covered:** visualization adapters for Matplotlib, Plotly, Altair, and later optional libraries. |
| `Radio` | **Covered:** semantic radio group; richer card/segmented variants preserve submitted values. |
| `ScatterPlot` | **Planned 0.12:** beginner chart with typed selection/event boundary. |
| `Sidebar` | **Covered:** semantic layout/navigation container with responsive behavior. |
| `SimpleImage` | **Covered:** ordinary image upload/display can choose a lightweight conversion adapter without a distinct public runtime primitive. |
| `Slider` | **Planned 0.15:** typed slider/range control with marks, keyboard behavior, validation, and native fallback. |
| `State` | **Covered with different scopes:** request, URL/form, session, cache, database, jobs, and browser storage have explicit owners. No implicit mutable global state is introduced. |
| `Textbox` | **Covered:** input/textarea, validation, forms, actions, and accessible errors. |
| `Timer` | **Covered:** polling/lazy refresh plus SSE/WebSocket alternatives when evidence justifies them. |
| `UploadButton` | **Covered:** file input/action composition with the same upload security contract as `File`. |
| `Video` | **Planned 0.15; expanded 0.10:** playback/upload/capture plus bounded chunked output, range requests, codecs, captions, backpressure, and fallback. |

### Layout components

`Row`, `Column`, `Group`, `Accordion`, `Tab`, and `Sidebar` are covered by Hedron layout,
disclosure, tabs, slots, fragments, and scoped style contracts. Gradio's `Walkthrough` maps to the
0.16 `Steps` composition with explicit navigation actions, resumable state, and accessibility.
Dynamic `render` behavior maps to 0.17 structured collections rather than whole-function reruns.

## Events, dependencies, and updates

Gradio's documented component events include change/input/submit/click, focus/blur/key-up,
select/double-click, upload/download/copy, play/pause/end, record/stream lifecycle, preview and
expand/collapse lifecycle, and chat feedback/edit/retry/undo events.

| Gradio event capability | Hedron disposition |
|---|---|
| Per-component listener methods | **Covered differently:** semantic browser events feed explicit typed actions. The server contract is action-first rather than a method on every component. |
| Typed `SelectData`, `LikeData`, `RetryData`, `UndoData`, `EditData`, and related event objects | **Covered/expanded 0.10/0.17:** typed payloads carry stable component/item identity, changed fields, pointer/keyboard source where useful, correlation, and authorized action context. |
| Multiple inputs and outputs | **Covered:** typed action inputs and `InteractionResult`/multi-region responses. |
| `.then()`, `.success()`, `.failure()` | **Covered/0.17:** explicit finite interaction graphs and success/error follow-up actions with cycle, side-effect, and duplicate-writer diagnostics. |
| `trigger_mode` once/multiple/always-last | **Covered/0.17:** concurrency, debounce/coalescing, latest-wins, stale-result rejection, and cancellation policies are declared and traceable. |
| `cancels`, time limits, progress target | **Covered:** cancellation/timeouts, jobs, progress/status, and target-specific loading regions. |
| Preprocess/postprocess switches | **Planned 0.18:** typed media/model adapters declare transformations; raw transport bypasses require explicit trusted schemas and limits. |
| `batch` and `max_batch_size` | **Planned 0.18:** inference batching uses bounded windows and resource-aware scheduling over durable job contracts. |
| `concurrency_id` and limit | **Planned 0.18 equivalent:** named resource/concurrency groups are capacity-owned, observable, fair, and usable across workers. |
| Property update return values | **Planned 0.17:** bounded, schema/version-checked patches for declared targets with full-fragment fallback. |
| Event `api_name` and default public API visibility | **Deliberate difference:** a UI action is not remotely published by default. HTTP and MCP exposure are separately registered, authenticated, authorized, rate-limited, and documented. |
| Inline `js` callbacks | **Deliberate non-parity:** registered browser modules, Web Components, and typed custom events replace raw JavaScript strings. |

## State and persistence

| Gradio state scope | Hedron disposition |
|---|---|
| Global Python variables | **Deliberate non-parity as application state:** Hedron documents external resources/caches/databases and lifespan ownership. Mutable process globals are neither durable, tenant-safe, nor multi-worker coherent. |
| Session `State` | **Covered:** typed `SessionState` adapter with explicit serialization, expiry, size, tenant, and host-session ownership. |
| Browser `BrowserState` / local storage | **Planned 0.15:** non-secret namespaced `BrowserStorage` with schemas, quotas, expiry, consent, unavailable-storage behavior, and no authority/durability claim. |
| URL/query state | **Covered:** typed routes, query models, redirects, history, and saved-view policy. |
| Callable component defaults and periodic recomputation | **Covered:** lazy resources/polling and explicit dependencies. Cache, side effects, authorization, and load timing remain visible. |

Hedron intentionally does not recommend browser storage for passwords or tokens and does not make
state persistence an incidental side effect of component identity.

## Queue, batching, progress, and streaming

Gradio automatically queues listeners, defaults resource-heavy event concurrency to one, supports
named concurrency groups, can batch queued inputs, exposes queue rank/size/ETA through its clients,
and streams generator values. Hedron's general `JobBackend`, action lifecycle, SSE/WebSocket work,
and progress/status components cover much of the outcome, but an ML workload needs a more specific
admission contract.

Phase 0.18 therefore adds an inference execution policy over `JobBackend`:

- queue admission, capacity, priority/fairness, queue position and bounded ETA semantics;
- named model/resource/GPU concurrency groups that remain correct across workers;
- bounded batch windows, maximum batch size, compatible-shape grouping, partial failure, and
  per-item correlation;
- generator and async-generator outputs, progress, disconnect/cancellation, timeout, retry, and
  artifact cleanup;
- durable backend adapters and overload behavior instead of an in-process production queue; and
- Explorer visibility for queue time, execution time, resource group, batch membership, streaming
  cadence, cancellation, and redacted inputs/outputs.

The 0.10 live phase is expanded for timed camera/microphone image/audio chunks and chunked
audio/video output. It requires permission, duration/frequency, codec, bandwidth, backpressure,
origin, reconnect, teardown, and accessible non-streaming fallback policy. Low-latency WebRTC may
be an optional transport adapter; it is not a correctness dependency or an automatic peer/public
network exposure.

## Examples, evaluation, and feedback

Gradio's `Examples`/`Dataset` can render sample inputs, use partial examples, paginate them, and
eagerly or lazily cache outputs. Its flagging system can capture inputs, outputs, files, labels,
and user corrections. These are useful model-demo outcomes but also create sensitive-data and
provenance risks if treated as an automatic UI side effect.

Phase 0.18 adds:

- `ExampleSet` with typed inputs, sample labels, provenance, model/action/schema version, partial
  values, pagination, authorization, and deterministic selection;
- cached example results keyed by implementation/model/version and preprocessing policy, with
  explicit eager/lazy generation, invalidation, storage, cost, and artifact retention;
- `PredictionLabel`, `ParameterViewer`, multi-speaker `Dialogue`, and demo-oriented media/artifact
  gallery presentation; and
- `PredictionFeedback` plus pluggable sinks for rating, label, reason, correction, and selected
  input/output references, requiring explicit collection notice/consent, redaction, tenant scope,
  retention/deletion, abuse controls, authorization, export, and audit policy.

Feedback is never silently enabled, never doubles as ground truth, and never stores secrets or
uploaded files merely because a component participated in an inference.

## API, clients, Server mode, and MCP

Gradio generates callable endpoints and API documentation for UI events, provides Python and
JavaScript clients with synchronous predictions and job submission/status/cancellation/iteration,
publishes OpenAPI, and includes an API recorder that turns UI interactions into client code.
`gradio.Server` exposes the same queue/SSE/MCP engine on a FastAPI subclass.

Hedron already has FastAPI-native routes, OpenAPI, operation IDs, jobs, streaming responses,
Explorer request simulation, and generated-client compatibility. Phase 0.18 adds the useful
remaining outcomes:

- an interaction recorder that emits redacted, reviewable Python/HTTP client examples for
  explicitly public endpoints, with file fixtures and session dependencies called out;
- an optional Gradio remote adapter using the official client protocol for endpoint discovery,
  typed files/artifacts, authentication, session state, job status/cancel, and streamed results;
- coexistence guidance for mounting a Gradio app beside Hedron where FastAPI ownership permits it;
  and
- migration diagnostics for `Interface`, `ChatInterface`, `Blocks`, components, events, state,
  queue/batch settings, API exposure, raw JS/HTML, file paths, and share links.

Hedron does not adopt Gradio's default in which registering a UI listener normally creates a public
client endpoint. HTTP and MCP remain independent projections of explicit domain actions. The
optional `hedron-mcp` package planned in 0.17 already covers tools, resources, and prompts with a
disabled-and-empty default, principal-preserving authorization, rate/payload limits, redaction,
audit, and prompt-injection diagnostics.

## Visual inference workflows

Gradio 6.17 introduced `Workflow`, a canvas that composes references, Hugging Face models, Spaces,
datasets, and bound Python functions through typed ports; it persists a versioned JSON graph and
can expose connected subgraphs through the Gradio API. This is a meaningful gap, not merely a
different layout API.

Phase 0.18 accepts an optional Hedron inference workflow with:

- typed reference/input, action/model/remote/dataset operator, and artifact/output nodes;
- versioned JSON schema, stable identities, typed ports, validation, cycle detection, required
  inputs, fan-out/fan-in, deterministic scheduling, partial failure, cancellation, and provenance;
- parallel execution where dependencies allow it, using the same inference/job resource policies
  as non-visual demos;
- separate read/run/edit/publish permissions, tenant scope, optimistic conflict handling, immutable
  published revisions, secret references, audit history, and rollback;
- reviewable mapping from each node to an explicitly registered action or optional provider; no
  arbitrary Python expression, package installation, or host-file execution from graph JSON;
- explicit API/MCP exposure per published subgraph rather than automatic publication; and
- Explorer/workbench diagnostics for schemas, costs, resource groups, timing, artifacts, failures,
  remote calls, and redacted data lineage.

Hugging Face model, dataset, Space, OAuth, and ZeroGPU nodes belong in optional vendor adapters.
The portable graph contract must also work with local actions, ordinary HTTP/OpenAPI services, and
application-owned model providers.

## Authentication, files, sharing, and deployment

| Gradio behavior | Hedron disposition |
|---|---|
| Username/password launch auth | **Covered by host auth, with stronger guidance:** applications use framework sessions, dependencies, or OIDC rather than an app-wide demo password as authorization architecture. |
| Hugging Face OAuth and `LoginButton` | **Covered/recipe:** portable OIDC is planned in 0.15; provider UI/claims are an optional integration. |
| Mount in FastAPI | **Covered:** Hedron is FastAPI-native and supports normal router/application ownership. A coexistence recipe handles a mounted Gradio sub-app. |
| Allowed/blocked/static paths and output-file cache | **Covered with a stronger boundary:** assets/uploads/downloads use explicit roots, safe paths, response ownership, authorization, retention, and cleanup. The current working directory is never an implicit public output root. |
| Temporary public share link | **Recipe/infrastructure:** document compatible development tunnels with prominent public-exposure warnings. Hedron does not run a first-party public proxy or imply deployment readiness. |
| Embed/PWA/SSR | **Covered by ordinary web composition:** iframes are policy-bounded; installability and SSR are application/deployment concerns. Hedron's server-rendered HTML does not require a Node SSR sidecar. |
| Spaces/Hub deploy and `DuplicateButton` | **Vendor integration:** deployment docs or plugin only; not a core portability contract. |
| Analytics/telemetry | **Deliberate constraint:** framework telemetry must be documented, opt-in, minimized, redacted, and independently disableable. |

## Customization and extension

Gradio themes and component styling map to Hedron tokens, themes, scoped styles, assets, inspect/eject,
HDJ, and application CSS. Python-packaged custom Gradio components map to Hedron component packages,
plugins, Web Components, typed events, and browser capability manifests. Hedron does not require
Node or Svelte to use core components, though an optional package may use any audited build tool
and ship compiled, pinned assets.

The following remain deliberate non-parity:

- raw JavaScript strings attached to server events;
- raw HTML templates interpolated with untrusted values;
- arbitrary DOM selectors as stable component or authorization identities;
- browser Python that can access server process/session state;
- deployed vibe-edit mode that can modify files or execute host code; and
- community component installation without package provenance, compatibility, capabilities,
  browser-asset, security, and accessibility review.

## Phase assignments from this audit

| Accepted capability | Owner |
|---|---:|
| Timed camera/microphone chunk inputs and chunked audio/video generator outputs | 0.10 transport; 0.15 capture/media |
| Responsive media gallery with preview, selection, upload/download, download-all bounds, and accessible fallback | 0.15 |
| Typed demo/interface generation from explicitly registered actions | 0.18 |
| Examples, cached example results, prediction labels, parameter viewer, multi-speaker dialogue, and feedback sinks | 0.18 |
| Inference admission, queue position/ETA, resource concurrency groups, batching, generator streaming, and durable backend adapters | 0.18 |
| API interaction recorder and optional Gradio remote/coexistence/migration package | 0.18 |
| Versioned, typed, permissioned visual inference workflow | 0.18 |
| Gradio HTTP endpoints projected to MCP | Already owned by optional explicit 0.17 MCP projection; no default-public shortcut |

## Deliberate non-parity summary

Hedron will not adopt:

- automatic public API or MCP exposure merely because a UI event exists;
- global mutable process variables as a supported application-state abstraction;
- arbitrary raw JavaScript/HTML or server-host code execution from component configuration;
- browser local storage for credentials, authority, or durable data;
- current-directory or broad host-path exposure as an output-file convenience;
- an in-process queue as the production durability/scaling promise;
- a public share tunnel, Hub duplication, ZeroGPU, or vendor hosting as core framework behavior;
- editable workflow URLs without explicit identity, authorization, revision, and audit policy; or
- deployed AI editing mode with permission to change files and run arbitrary host code.

These are architectural constraints, not untracked omissions.

## Refresh procedure

For each future audit:

1. Record the latest stable Gradio version from PyPI and the official changelog.
2. Re-enumerate app builders, layouts, components, helpers, event types, routes, Server/MCP APIs,
   clients, and Workflow schema from the current documentation.
3. Review the major-version migration guide and all releases since the previous baseline.
4. Recheck authentication, file access, sharing, telemetry, custom-code, and vendor-service
   boundaries rather than treating them as incidental launch flags.
5. Map new outcomes to an existing Hedron contract, expand a coherent phase, create an accepted
   later packet, or record deliberate non-parity with rationale and evidence.
6. Update this ledger, both roadmap mirrors, README phase summary, and documentation navigation in
   the same change.
