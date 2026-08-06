# streamlit-extras feature cross-check

**Audit date:** 2026-08-06 (refreshed for phase 0.16 entry/exit)<br>
**streamlit-extras baseline:** 1.5.0 documentation and source catalog<br>
**Inventory:** 51 active extras and 6 deprecated extras<br>
**Purpose:** identify useful capability gaps, not reproduce Streamlit's widget or rerun runtime
**0.16 disposition:** Implemented 0.16 items implemented in `hedron-extras` (or documented recipes)
with per-feature capability manifests.

`streamlit-extras` is a useful demand signal because it collects small visual recipes, composite
widgets, third-party renderers, browser bridges, and a few substantial analysis tools in one
catalog. Hedron should not copy that catalog into core. This audit classifies each extra as already
covered/equivalent, accepted into an existing roadmap phase, accepted into a curated optional
package, recipe/plugin territory, or deliberate non-parity.

## Official source baseline

The inventory and behavior descriptions come from the project's official sources:

- [streamlit-extras documentation](https://arnaudmiribel.github.io/streamlit-extras/)
- [active and deprecated extras catalog](https://arnaudmiribel.github.io/streamlit-extras/components/)
- [official source repository](https://github.com/arnaudmiribel/streamlit-extras)
- [package metadata and dependency declarations](https://github.com/arnaudmiribel/streamlit-extras/blob/main/pyproject.toml)

The documentation is the catalog authority for this audit. A feature appearing in the repository
but not in the active or deprecated documentation navigation is not counted as a supported extra.

## Disposition rules

- **Covered/equivalent:** Hedron already supplies the user outcome, sometimes through explicit
  composition or normal HTTP/framework behavior rather than one helper call.
- **Planned 0.12/0.15:** the extra exposed a gap in an existing coherent roadmap phase.
- **Implemented 0.16:** the feature is useful but specialized enough for the optional
  `hedron-extras` distribution rather than core.
- **Recipe/plugin:** ordinary Hedron composition or third-party styling can supply it; first-party
  API and long-term compatibility cost are not justified.
- **Deliberate non-parity:** the mechanism conflicts with Hedron's security, accessibility, state,
  or explicit-request architecture. The useful outcome may still have a safer equivalent.

## Active extras: complete catalog cross-check

### Identity, layout, styling, and small composites

| streamlit-extra | What it provides | Hedron disposition |
|---|---|---|
| Avatar | Circular image with label/caption and optional click | **Implemented 0.16 recipe:** compose `Image`, text, and a safe link/action; a profile recipe may standardize sizing and accessible names. |
| Badges | Social/project status badges | **Covered/equivalent:** `Badge`, `Image`, and safe links. Live remote badge services remain subject to image/CSP/privacy policy. |
| Bottom Container | Sticky container at the viewport bottom | **Planned 0.15:** sticky/bottom action and chat docks already own focus, virtual-keyboard, and safe-area behavior. |
| Buy Me a Coffee Button | Floating branded external link | **Covered/equivalent:** safe link/button plus 0.15/0.16 floating placement; provider branding belongs in a recipe. |
| Card Selector | Rich card-based single or multiple choice | **Implemented 0.16:** semantic card choices over radio/checkbox inputs with keyboard and no-JavaScript behavior. |
| Customize running | Restyles Streamlit's global running indicator | **Recipe/plugin:** Hedron already has explicit `Loading`, `Status`, and progress regions; global DOM/CSS monkey-patching is not an API. |
| Directory Tree | Collapsible filesystem tree with optional path selection | **Implemented 0.16:** generic selectable `TreeView`; filesystem enumeration and path authorization stay server-owned. |
| Floating button | Fixed-position floating action button | **Implemented 0.16:** floating action placement with safe-area, collision, focus, and semantic button/link rules. |
| Grid Layout | Round-robin grid rows with relative widths and gaps | **Covered/equivalent:** `Grid`, `Inline`, responsive layout, and HDJ/native CSS Grid. |
| Keyboard text | Keyboard-key visual styling | **Recipe/plugin:** semantic `<kbd>` markup and scoped styles; no dedicated runtime primitive. |
| Keyboard to URL | Keyboard binding that opens a URL | **Implemented 0.16:** declared shortcuts mapped to safe links/actions, with conflict, focus, user-activation, and popup-blocking policy. |
| Let emojis rain | Full-screen falling-emoji animation | **Deliberate non-parity:** decorative effect stays CSS/Web Component/plugin territory and must respect reduced motion. |
| Mentions | Inline icon-and-label links | **Covered/equivalent:** safe links, icons, badges, text, and inline composition without raw HTML generation. |
| Metric Cards | Global CSS restyling for metrics | **Covered/equivalent:** `Metric`, `Card`, scoped styles, variants, and theme tokens; no page-wide test-ID selector patch. |
| Radial Menu | Circular icon choice menu | **Recipe/plugin:** unconventional navigation has substantial keyboard, touch, zoom, and discoverability cost; stable select/menu controls remain first-party. |
| Resizable Columns | Drag-resizable columns with persisted ratios | **Implemented 0.16:** resizable split panes with min/max constraints, persistence, keyboard resizing, and responsive fallback. |
| Scroll to Element | Programmatic keyed-element scrolling | **Implemented 0.16:** declared focus/scroll requests by stable component identity, not arbitrary DOM selectors. |
| Skeleton Placeholder | Replaceable container with loading skeleton | **Covered:** `Skeleton`, addressable fragments, loading regions, and out-of-band replacement. |
| Steps | Stateful horizontal/vertical multi-step indicator | **Implemented 0.16:** `Steps` plus explicit next/previous/set actions, addressable URLs, and resumable workflow state. |
| To-do items | Checkbox-plus-content composition | **Covered/equivalent:** checkbox, layout, submitted/action state, and ordinary component composition. |
| Toggle button | `<details>` summary/content disclosure | **Covered:** `Expander` and native semantic disclosure. |

### Data, charts, media, and analysis tools

| streamlit-extra | What it provides | Hedron disposition |
|---|---|---|
| Capture | Redirects stdout, stderr, or logging output into Streamlit elements | **Implemented 0.16 outcome:** bounded live job/log console. Process-global stream redirection remains non-parity; output must have explicit producer, scope, redaction, and backpressure. |
| Chart annotations | Adds annotation overlays to Altair time-series charts | **Planned 0.12:** backend-neutral typed chart annotation/overlay contract. |
| Chart container | Chart/data tabs with CSV export and optional dataframe exploration | **Implemented 0.16:** reusable chart/data/export/explore workbench over existing `Tabs`, charts, data tables, and downloads. |
| Chart.js Chart | Direct Chart.js specifications | **Planned 0.12:** optional adapter behind the standard asset, event, payload, CSP, and fallback contracts. |
| Dataframe explorer UI | UI-authored column filters returning a filtered dataframe | **Implemented 0.16:** faceted `DataExplorer` emits a bounded typed transform plan to a `DataSource`; it never silently collects distributed data. |
| Diagrams | Renders Python `diagrams` architecture graphs | **Covered/planned 0.12:** GraphViz and Mermaid adapters plus safe image/SVG output cover the renderer; a `diagrams` convenience can be a recipe. |
| Great Tables | Theme-aware rendering of Great Tables objects | **Planned 0.12:** optional adapter with accessible table fallback and explicit theme translation. |
| Image Compare Slider | Before/after image overlay with draggable divider | **Implemented 0.16:** interactive compare with horizontal/vertical operation, labels, position events, touch/keyboard access, and static fallback. |
| Image Crop | Adjustable normalized crop bounds, aspect ratio, circular mask, guides | **Implemented 0.16:** typed crop selection; server-side decoding and transformation remain explicit. |
| Image Selector | Box or lasso region selection over an image | **Implemented 0.16:** normalized image-region events with source, payload, keyboard/touch, and accessible-alternative policy. |
| JSON Editor | Collapsible editable JSON tree | **Implemented 0.16:** schema-aware `JSONEditor` with typed change events, validation, authorization, depth/size limits, and read-only mode. |
| Sigma Graph | WebGL network graph with NetworkX input, layouts, and selection | **Planned 0.12:** optional Sigma.js/NetworkX adapter using typed authorized selection events. |
| Three.js 3D Viewer | Orbit viewer for GLTF/GLB, OBJ, STL, PLY, and FBX | **Planned 0.12:** optional model-viewer adapter with format/source allowlists, size budgets, teardown, and accessible description/fallback. |
| Word importances | Colors tokens by signed importance score | **Implemented 0.16 recipe/adapter:** semantic token-weight display with legend, non-color encoding, bounds validation, and no raw HTML. |

### Browser, execution, state, and workflow helpers

| streamlit-extra | What it provides | Hedron disposition |
|---|---|---|
| Concurrency limiter | Decorator limiting simultaneous calls | **Covered/planned 0.13:** application/server limits exist; adaptive bounded preparation/concurrency owns richer behavior. |
| Cookie Manager | Dict-like JavaScript cookie access | **Covered/equivalent with deliberate boundary:** request cookies and typed response cookie mutation use host HTTP APIs. Hedron will not expose all origin cookies to arbitrary component JavaScript. |
| Echo Expander | Executes a block and displays its source in an expander | **Covered by composition:** `CodeViewer` plus `Expander` and Explorer examples; execute-while-rendering magic is non-parity. |
| Eval JavaScript | Evaluates arbitrary JavaScript and returns the result to Python | **Deliberate non-parity:** use typed Web Components/events and `BrowserContext`; arbitrary eval defeats CSP, capability inspection, and event validation. |
| Exception Handler | Replaces Streamlit's internal uncaught exception handler | **Covered/equivalent:** framework exception handlers, typed error regions, logging, and diagnostics; no monkey-patch of private runtime internals. |
| Function explorer | Generates a UI from a Python function's type hints | **Implemented 0.16:** typed callable-to-action form adapter, limited to supported annotations and explicitly exposed authorized actions. |
| Jupyterlite | Embeds the public JupyterLite demo in an iframe | **Implemented 0.16:** optional pinned, locally auditable browser-Python/notebook sandbox bridge with explicit isolation and budgets. |
| Local Storage Manager | Namespaced dict-like browser localStorage with JSON and expiry | **Planned 0.15:** typed `BrowserStorage` for non-secret preferences with quotas, consent, expiry, and unavailable-storage behavior. |
| Mandatory Date Range Picker | Guarantees a complete start/end tuple | **Planned 0.15:** typed date-range control plus form/action validation; incomplete input returns a validation error rather than halting the app. |
| Pagination | Numbered previous/next page selector | **Covered:** pagination helpers and bounded `DataSource` paging with accessible links/forms. |
| Redirect | Validated internal/external same-tab or new-tab redirect | **Covered:** safe redirects, links, history policy, and typed interaction results. |
| Stlite Sandbox | Executes untrusted Streamlit/Python code in the browser | **Implemented 0.16 outcome:** isolated browser-Python sandbox, never server-side arbitrary execution; not a promise to embed Streamlit itself. |
| Specialized Inputs | Phone, email, URL, money, search, and password fields | **Planned 0.15:** typed control families, validation, adornments/help/errors, debounce where enhanced, and native submitted-value fallback. |
| Read-only Star Rating | Displays half-step ratings | **Planned 0.15:** rating/feedback controls include read-only presentation and non-color text equivalents. |
| Stateful Button | Button persisted as a toggle | **Planned 0.15 equivalent:** explicit toggle/switch input and scoped form/URL/session state, not hidden rerun state. |
| Stateful Chat | Chat container that persists transcript across reruns | **Planned 0.10 equivalent:** chat transcript/input, explicit storage owner, attachments, and bounded streams without whole-script reruns. |

## Deprecated extras

Deprecated entries remain in the audit so removed or superseded ideas do not silently reappear as
future gaps.

| Deprecated extra | Hedron disposition |
|---|---|
| Add Vertical Space | **Planned 0.15:** semantic spacing primitives; ordinary layout gap/margin remains preferred. |
| App logo | **Planned 0.15:** application logo and page-icon helpers. |
| Color ya Headers | **Covered:** headings, theme tokens, variants, and scoped styles. |
| Row Layout | **Covered:** `Inline`, `Grid`, responsive layout, and native CSS. |
| Styleable Container | **Covered:** `Container`, scoped CSS, variants, and application override layers. |
| Tags | **Covered/planned 0.15:** `Badge` for display and pills/multiselect for interactive selection. |

## Roadmap changes produced by the audit

### Phase 0.12: data and visualization scale

- Add a typed backend-neutral annotation/overlay contract.
- Name optional Chart.js, Great Tables, Sigma.js/NetworkX, and Three.js adapters.
- Apply the existing local-asset, CSP, payload, lifecycle, selection-event, and accessible-fallback
  requirements to every adapter.

### Phase 0.15: data-app surface completeness

- Add typed namespaced `BrowserStorage` for local/session preferences.
- Keep browser storage outside authentication, authorization, secrets, and server durability.
- Existing controls, rating, date range, specialized inputs, bottom docks, logo helpers, and chat
  plans cover the corresponding extras without a second widget runtime.

### Phase 0.16: curated extras and interactive analysis tools

- Add the optional `hedron-extras` distribution rather than burdening `hedron-core`.
- Own card choice, tree, steps, resizable panes, floating actions, shortcuts/focus/scroll, data and
  chart workbenches, JSON editing, callable action forms, interactive image tools, specialized
  presentation recipes, bounded live logs, and an isolated browser-Python sandbox bridge.
- Require each feature to declare dependencies/assets and pass independent conformance, security,
  accessibility, payload, lifecycle, and fallback evidence.

## Deliberate non-parity and architectural boundaries

1. **No arbitrary browser `eval`.** Typed browser context and declared component events cover
   legitimate data flow without bypassing CSP and capability review.
2. **No process-global stdout/stderr capture as UI state.** Live output is tied to an explicit job
   or producer with redaction, bounds, cancellation, and backpressure.
3. **No DOM-wide CSS selectors or private-runtime monkey-patches as framework APIs.** Theme tokens,
   scoped styles, variants, loading/error regions, and host exception handlers are stable contracts.
4. **No implicit rerun/session widgets.** Toggles, steps, chat, and other stateful interactions use
   typed forms/actions and explicit URL, session, cache, browser, or database ownership.
5. **No filesystem authority from a tree widget.** A `TreeView` displays application-supplied nodes;
   the server authorizes any directory listing or file action.
6. **No server execution of untrusted Python.** Optional browser runtimes are isolated, bounded,
   version-pinned, and unable to access application secrets or server/session state.
7. **No decorative animation commitment in core or the curated package.** Applications and plugins
   may add effects while honoring reduced-motion and interruption requirements.

## Maintenance rule

Refresh this matrix before closing phases 0.12, 0.15, and 0.16, and whenever Hedron claims broader
Streamlit ecosystem migration coverage. Every new or renamed catalog entry must be classified as
covered/equivalent, accepted into a phase, recipe/plugin territory, or deliberate non-parity.
Accepted gaps require a phase owner, dependency and asset boundary, security and accessibility
contracts, and evidence-bearing exit gate before they may be called Supported.
