---
status: shipped
---

# Built-in component baseline

[Browse all built-in component demos](../components/index.md){ .md-button .md-button--primary }

Every public component listed below has a dedicated guide with a usable semantic preview,
constructor and parameter reference, composition and backend behavior, accessibility and
security guidance, common mistakes, and testing advice. HTMX-dependent previews use a
clearly labelled in-browser simulation; production authorization, validation, persistence,
and fragment rendering remain server responsibilities.


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted

This is the minimum built-in set for phase 0.1 (`v0.1.0`) and the secure CRUD slice in phase 0.2 (`v0.2.0`). Later capability phases extend it through their own acceptance gates.

## Phase 0.1 core (`v0.1.0`)

- Document and composition: `Page`, `Fragment`, `Head`, `Title`.
- Landmarks: `Header`, `Main`, `Nav`, `Aside`, `Footer`, `Section`.
- Layout: `Container`, `Stack`, `Inline`, `Grid`, `Divider`.
- Content: `Heading`, `Text`, `Link`, `Image`, `CodeBlock`, `List`, `DescriptionList`, static `Table`.
- Surfaces and status: `Card`, `Badge`, `Alert`, `Skeleton`.
- Controls: `Button`, `LinkButton`, `IconButton`.
- Forms: `Form`, `FormField`, `Label`, `TextInput`, `TextArea`, `Select`, `Checkbox`, `RadioGroup`, `SubmitButton`, `FormErrors`.
- Escape hatch: the `hedron.html` namespace for native HTML tags and validated native attributes.

Built-ins use native semantic HTML, expose documented slots and variants, and satisfy their accessibility contract without JavaScript. `Grid` is explicit composition; it does not return mutable positional column handles.

### Native HTML primitives

`html.<tag>(*children, **attributes) -> ComponentNode` exposes known lowercase HTML elements without exposing private serializer nodes. Python keyword aliases include `class_` and `for_`; `data={...}` and `aria={...}` are explicit mappings to normalized `data-*` and `aria-*` attributes. Boolean attributes accept booleans, absent values use `None`, event-handler attributes are rejected, and URL-bearing attributes (`href`, `src`, `action`, `srcset`, `ping`, HTMX URL attrs including `hx-push-url` / `hx-replace-url`, …) receive `SafeUrl` policy checks. Unknown tags or attributes fail with a diagnostic. Raw markup is available only as `html.raw(TrustedHtml)`.

## Phase 0.2 FastAPI interaction additions (`v0.2.0`)

- `AutoForm`, `RefreshButton`, `Lazy`, `Poll`, `InfiniteScroll`, `Pagination`, `Loading`, and retryable `ErrorState`.
- `action_attrs(ref, *, include_csrf=..., csrf_token=...)` and `oob_swap(id, content)` helpers.
- Typed action bindings and validation-fragment helpers.
- Page layout and HTMX navigation helpers (`approved_headers`, history-restore PAGE mode).

`Lazy` and `Poll` honor `ComponentRef.hx_attrs()` (method and query params). `Pagination` emits `SafeUrl`-backed `href` / `hx-get` values. HTMX targets are validated against a safe CSS-selector subset.

## Phase 0.5 data application toolkit (`v0.5.0`)

- Intelligent rendering: `Auto` with inspectable renderer registry and bounded Data Intelligence.
- Data: `DataTable`, `DataEditor` (via `hedron-data`), typed change sets, data-source protocols.
- Cache: `cache_data`, `cache_component` with scoped keys, single-flight, and Explorer traces.
- Utilities: `Metric`, `FileUpload`, `DownloadButton`, `CodeViewer`, `JSONViewer`, `Progress`,
  `Status`, `Toast`, `Expander`, `Tabs`, `Sidebar` (layout `Grid` remains from 0.1).
- ColorMode: preference API, accessible toggle, cookie/session persistence.

## Phase 0.6 visualization and content (`v0.6.0`)

- Charts: `LineChart` and Matplotlib/Plotly/Altair adapters via `hedron-charts`
  (`pip install "hedron[charts]"`).
- Content: `Markdown`, `highlight_code`, `process_image`, `validate_email_address`.
- Trust: `TrustedHtml.nh3`, trusted icon/SVG registry.
- Interaction: `InteractionResult`, `HtmxRequest`, fragment regions, status policies.

## Phase 0.10 live interaction additions (`v0.10.0`)

- `Dialog`: native dialog structure with explicit close behavior and browser-module modal intent.
- `ChatMessage`: typed transcript items for user, assistant, system, tool, and status roles.
- `ChatInput`: labelled explicit-submit chat form with typed HTMX targeting and optional attachments.

Applications remain responsible for dialog triggers and focus restoration, chat history and
ordering, authentication, CSRF, rate limits, persistence, attachment validation, and bounded
streaming. The hosted component pages simulate these browser and server boundaries locally.

## Phase 0.18 presentation (`v0.18.0`)

Model-demo presentation builtins (see [Inference API](INFERENCE.md) and component pages):

- `PredictionLabel` — ranked class scores with accessible table representation.
- `ParameterViewer` — schema-aware parameter documentation with secret redaction.
- `Dialogue` — multi-speaker transcript presentation with typed speaker identity.

Non-UI contracts (`ModelDemo`, `ExampleSet`, `PredictionFeedback`, `InferenceWorkflow`) are
documented on [INFERENCE.md](INFERENCE.md), not as components.

## Naming rule

Hedron component names use PascalCase. Native elements use lowercase `hedron.html` attributes and tags. Python keyword collisions use a trailing underscore such as `class_`; rendered HTML always uses the canonical attribute name.
