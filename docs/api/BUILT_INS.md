---
status: shipped
---

# Built-in component baseline

**Status:** Accepted

This is the minimum built-in set for phase 0.1 (`v0.1.0`) and the secure CRUD slice in phase 0.2 (`v0.2.0`). It is deliberately smaller than the full 1.0 component catalog.

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

## Later catalogs

Phase 0.6 (`v0.6.0`) adds chart components and trusted icon/SVG registry integrations.

## Naming rule

Hedron component names use PascalCase. Native elements use lowercase `hedron.html` attributes and tags. Python keyword collisions use a trailing underscore such as `class_`; rendered HTML always uses the canonical attribute name.
