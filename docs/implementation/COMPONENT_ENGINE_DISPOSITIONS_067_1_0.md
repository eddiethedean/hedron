# Component engine dispositions for Hedron 0.67 and 1.0

**Status:** Proposed planning contract  
**Decisions:** D-070 / D-113 / D-114 / D-115 / D-116  
**Targets:** Hedron `v0.67.0` migration bridge and `v1.0.0` canonical surface  
**Machine inventory:**
[component-engine-dispositions-067.toml](../acceptance/component-engine-dispositions-067.toml)  
**Interaction boundary:**
[HTMX_ALPINE_BOUNDARY_1_0](../api/HTMX_ALPINE_BOUNDARY_1_0.md)

## Outcome

Hedron 1.0 retains Web Components as a first-class browser capability, but does not use them as the
default wrapper for ordinary UI. Each component family receives one explicit engine disposition:

- **native** when the web platform already supplies the required semantics and behavior;
- **Alpine-enhanced** when server-rendered semantic HTML needs disposable local behavior;
- **Web Component** when the feature is a specialist, independently reusable browser subsystem;
- **external/provider-owned Web Component** when a third-party package owns the implementation;
  or
- **conformance fixture** when a tag exists to prove the public element ABI rather than solve an
  application task.

The audit is bidirectional. Existing Web Components may move to native HTML plus Alpine when their
custom-element boundary adds lifecycle and authoring cost without meaningful encapsulation.
Existing scripts or Alpine-backed behavior may move into a Web Component when independent reuse,
resource ownership, typed properties/events, or a complex long-lived browser engine makes the
element boundary materially better.

One Python component/task keeps one canonical name regardless of its selected browser engine.
Engine choice is a lowering detail visible in inspect/Explorer, not a new `AlpineDialog` versus
`WebDialog` developer choice. This is the **one canonical engine** rule: a task may compose with
other engines at an ownership boundary, but it does not expose parallel ordinary implementations.

## Selection ladder

Every first-party family is evaluated in this order:

1. **Can semantic HTML and CSS satisfy the Supported behavior?** Use native HTML.
2. **Is the missing behavior disposable, document-local enhancement over server HTML?** Use
   Alpine.
3. **Does the feature own a substantial browser subsystem with independent lifecycle, resources,
   properties/events, or cross-framework packaging value?** Use a Web Component.
4. **Is the feature actually a third-party/client application rather than a bounded Hedron
   component?** Keep it provider-owned, Experimental, or declare it not a fit.

The decision is based on the full component capability, not line count alone. A small element may
still justify a Web Component when its standards boundary is the product; a large Alpine module is
not preferred merely to avoid a custom tag.

## Selection criteria

| Evidence | Favors native + Alpine | Favors Web Component |
|---|---|---|
| Markup | Existing semantic/native element is the real control | A custom element is the meaningful portable host |
| State | Disposable open/selected/filter/focus/geometry state | Complex local model, draft, viewport, selection, or adapter state |
| Lifecycle | Reinitialize cleanly after HTMX replacement | Own workers, canvas, object URLs, observers, editor/grid/map instances, or costly setup |
| Packaging | Used only through Hedron's server-rendered component | Independently useful across Hedron, plain HTML, or other frameworks |
| API | Normal attributes/events and `Interaction` are sufficient | Typed imperative properties/methods/events form a real standards API |
| DOM ownership | Server remains the natural owner of most markup | The browser subsystem needs a clearly owned internal DOM/resource region |
| Styling | Hedron theme hooks on light DOM are sufficient | Stronger encapsulation/parts/slots or vendor-host isolation is valuable |
| HTMX use | Frequent whole-root replacement is expected | Stable host with explicitly declared server-owned regions is valuable |
| Dependency | Alpine core/plugin already serves common UI | Vendor engine/WASM/worker/module assets need isolated demand and cleanup |
| Failure | Native markup already provides the complete fallback | A substantial fallback plus isolated upgrade failure is required |

A Web Component is not selected merely because a component is interactive, reusable in Python, or
needs JavaScript. Alpine is not selected merely because it is the new 0.67 dependency.

## Preliminary dispositions of existing first-party tags

These are the W0 freeze recommendations. `ENGINE-067` may change a recommendation only through
recorded evidence before W1; after the freeze, a change requires a superseding decision.

| Current surface | 1.0 disposition | Canonical 1.0 behavior |
|---|---|---|
| `hedron-example` | **Keep Web Component as conformance fixture** | Continues proving the public ABI, fallback, author kit, and third-party interoperability; not an ordinary application widget |
| `hedron-disclosure` and legacy `hedron-disclose` | **Migrate to native + Alpine** | One `Disclosure` component uses `<details>` where adequate and registered Alpine behavior for richer controlled presentation |
| `hedron-dialog` | **Migrate to native + Alpine** | One `Dialog` component uses native `<dialog>`/top-layer semantics plus Alpine/Focus behavior and HTMX-safe lifecycle |
| `hedron-field-text` | **Migrate to native + Alpine** | Native input/textarea owns value and form submission; Alpine adds masks, counts, reveal/hints, and disposable presentation |
| `hedron-field-choice` | **Split by real task, remove wrapper tag** | Native checkbox/radio/select remain native; richer listbox/combobox/radio-group behavior uses the same Hedron control family with Alpine |
| `hedron-field-file` | **Migrate ordinary path to native + Alpine** | Native file input owns files/submission; Alpine may add bounded preview/count/drop presentation. A distinct advanced uploader is a Web Component candidate, not a compatibility wrapper |
| `hedron-action-async` | **Migrate to unified interaction lowering** | Hedron operation identity owns lifecycle; Alpine projects local presentation when present and the HTMX extension provides the request-only DOM fallback |
| `hedron-chart` | **Keep Web Component** | A framework-neutral, lifecycle-safe visualization host owns SVG/canvas rendering, selection events, resize observers, exports, and adapter resources |
| `hedron-map` | **Keep Web Component** | A provider-owned map host owns MapLibre/viewport/layer/observer resources and typed map events while preserving semantic fallback |
| `hedron-data-editor` | **Keep Web Component** | The grid/editor host owns complex selection, draft, viewport, adapter, conflict, and resource lifecycle behind the existing typed server contract |
| Registered `hedron-extras` host tags | **Keep provider-owned Web Components where the host is substantive** | Each provider must pass the same engine audit; trivial common-widget wrappers migrate to Alpine or native HTML |
| Third-party tags using the Hedron element ABI | **Keep supported Advanced capability** | The public ABI, author kit, registry, asset plan, lifecycle, fallback, and security contracts remain available in 1.0 |

The accepted Web Component ABI is not deprecated wholesale. Only inventoried first-party tags that
duplicate the common component catalog are migration candidates. Public 0.67 direct-tag and Python
paths selected for removal receive `HedronFutureWarning` or the equivalent target-1.0 static
finding before 1.0.

## Candidates to promote to Web Components

The audit must also look for current script/Alpine/native hosts that should move in the other
direction. Promotion is evidence-gated, not automatic.

| Candidate | Preliminary direction | Admission evidence |
|---|---|---|
| Full code editor beyond the current `CodeEditor` host stub | **Web Component candidate** | Exact editor engine/assets/license; worker/model/selection lifecycle; typed value/change API; form/server fallback; CSP/a11y/performance evidence |
| Terminal emulator beyond `TerminalView` placeholder behavior | **Web Component candidate** | Explicit transport boundary, terminal resource cleanup, keyboard/screen-reader policy, bounded history, CSP and package ownership |
| Advanced uploader with chunking, directory traversal, previews, object URLs, or resumable state | **Web Component candidate** | Native ordinary upload fallback, File/object-URL cleanup, bounded queues, server-owned acceptance, retry/conflict/security evidence |
| Advanced camera/microphone streaming or recording session | **Web Component candidate** | Permission lifecycle, stream/track cleanup, device changes, recording bounds, form/upload fallback, privacy and accessibility evidence |
| Additional grid, diagram, canvas, WebGL/WebGPU, or WASM host | **Web Component candidate** | Independent package value, typed properties/events, resource teardown, semantic fallback, budgets, and no hidden request/domain authority |

Basic file, camera, microphone, audio, and video controls remain native. A candidate becomes a Web
Component only for a distinct advanced capability; it does not turn the basic control into a second
implementation choice.

## Alpine and Web Component composition

Selected Web Components and Alpine may appear in the same page or interaction, but do not share
internal ownership.

- Alpine may set a documented element attribute/property and listen for a documented typed event
  through the normalized Hedron adapter. It must not traverse or rewrite element-owned DOM.
- A first-party Web Component must not boot a private Alpine application, mutate an enclosing
  Alpine store, or use Alpine as an undocumented internal dependency.
- A Web Component emits intent. It does not call `fetch()`, `htmx.ajax()`, mutate domain state, or
  treat a client event as authorization.
- HTMX may replace the entire element or only a declared `data-hedron-server-region`; it must not
  replace element-owned DOM in place.
- The lifecycle coordinator cleans and reconnects the selected engine exactly once. It does not
  mirror Alpine state into element state or vice versa without a typed transfer contract.
- One property/state token still has one writer. An Alpine wrapper and a Web Component cannot both
  own selection, value, busy state, focus, or announcement for the same interaction.

When a common Alpine component controls a specialist element—for example, tabs containing a chart—
the tab owns only visibility/selection and the chart owns only its rendering/viewport/selection
events. Visibility changes use the documented resize/activation notification; Alpine does not
redraw the chart.

## Migration rules

### Web Component to Alpine/native

1. Preserve the public Python component name and server semantics.
2. Add behavior-parity fixtures for the existing tag before changing lowering.
3. Ship the new native/Alpine lowering in 0.67.
4. Mark direct old tags, package classes, activation flags, assets, and element-only events as
   compatibility paths with structured warnings and one replacement.
5. Prove native form, HTMX, no-JavaScript, focus, and accessibility parity.
6. Remove the duplicate tag/module in 1.0; do not retain a shadow custom-element alias.

### Script/Alpine/native host to Web Component

1. Keep the same public Python component/task name.
2. Prove the Web Component criteria and an independently useful typed host contract.
3. Register the tag, ABI, properties/events, assets, ownership, fallback, lifecycle, and security
   metadata in the existing element registry.
4. Move resource ownership into the element; do not embed an Alpine root or private HTMX request
   layer.
5. Preserve semantic SSR/no-JavaScript content and ordinary server action fallback.
6. Remove the prior private controller after 0.67 behavior and migration evidence passes.

## Required evidence

`ENGINE-067` requires:

- a complete inventory of first-party tags, custom-element registrations, delegated controllers,
  registered Alpine modules, provider hosts, and third-party ABI consumers;
- one disposition and one canonical Python task/component name for every row;
- measured complexity, assets, lifecycle resources, DOM ownership, fallback, portability, CSP,
  accessibility, HTMX, and performance evidence rather than preference alone;
- behavior-parity and migration fixtures for every engine change;
- three-engine init/cleanup/swap/OOB/history/failure tests for retained and migrated elements;
- static rejection of multiple canonical engines for one task;
- complete 0.67 warning coverage for every public path removed in 1.0; and
- confirmation that the public Web Component ABI and third-party authoring capability remain
  supported even when selected first-party tags migrate to Alpine.

The release may keep a family on its existing engine when evidence does not justify a switch. What
it may not do is expose Alpine and Web Component versions as parallel ordinary choices or switch an
engine without fallback, lifecycle, compatibility, and migration proof.
