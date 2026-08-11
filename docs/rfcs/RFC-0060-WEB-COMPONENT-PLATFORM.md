# RFC-0060: Web Component platform program

**Status:** Draft

**Target phases:** 0.33–0.38

**Tracking:** [#92](https://github.com/eddiethedean/hedron/issues/92)–[#97](https://github.com/eddiethedean/hedron/issues/97)
(one enhancement issue per phase). Close each issue when its owning release-gate rows are
Verified; do not begin implementation until this RFC is Accepted.

## Summary

Hedron will make standards-based Web Components the preferred browser boundary for interactive
first-party UI. Python components and server-rendered HTML remain canonical; HTMX remains the
request, fragment, and navigation layer. Custom elements add browser-local behavior without a
virtual DOM, hydration protocol, synthetic event system, global client store, or application-owned
Node.js build.

The program introduces a versioned element ABI, lifecycle rules for HTMX swaps, form-associated
controls, common rich-widget contracts, an authoring and interoperability kit, typed browser
composition, and a final production-grade graduation. Static content does not need a custom-element
wrapper merely to conform to this direction.

Five explicit interaction contracts make the React-to-HTMX transition complete for server-backed
applications: `ElementStateOwnership`, `InteractionState`, `OptimisticMutation`,
`GestureOverlayCatalog`, and `ReactMigrationMatrix`.

This RFC refines RFC-0021 and RFC-0025. Their standards-first and explicit-lifecycle boundaries
remain in force.

## Motivation and background

Hedron already uses browser modules and custom elements for selected data, chart, disclosure, and
specialty surfaces. Those implementations do not yet share one public ABI for definition,
structured input, typed events, DOM ownership, teardown, accessible fallback, theming, diagnostics,
or version skew. Adding more interactive components without that foundation would multiply
one-off browser protocols and make HTMX lifecycle behavior difficult to audit.

Web Components are a strong fit because they:

- are a browser standard and work with server-rendered markup;
- upgrade incrementally after useful HTML is already present;
- isolate complex local behavior without taking ownership of routing or application state;
- can be consumed from Python, HDJ, Flask, Django, and non-Python conformance hosts; and
- let Hedron publish local, fingerprinted modules while keeping Node.js optional for applications.

The goal is not to move the application into the browser. The server continues to own business
state, authorization, validation, routes, and durable work. Elements own bounded interaction that
must happen locally between requests.

## Proposed design

### 1. Package and protocol boundary

A new `hedron-elements` Python distribution will contain the shared Python authoring surface,
element metadata, and locally served browser modules. It depends on `hedron-core`, not on a host
framework. FastAPI, Flask, and Django integrations consume the same assets and metadata through the
existing registry and manifest contracts.

The distribution begins as Alpha in phase 0.33. Selected beginner-facing elements may be
re-exported from `hedron`; host adapters do not fork their browser implementations. Phase 0.36 may
publish the same browser modules as `@hedron/elements` for non-Python authors, but Python consumers
never need npm or an application bundler.

The browser ABI is versioned independently from Python import paths. Server markup, registry
metadata, and modules declare compatible ABI versions. An incompatible module/markup combination
fails visibly with a `HED-ELEMENT-*` diagnostic and leaves the server-rendered fallback usable.

### 2. Definition and naming

First-party tag names use the reserved `hedron-` prefix. Every definition declares:

- tag name and element ABI version;
- module and asset IDs;
- observed scalar attributes;
- structured input schemas and size limits;
- public properties and methods, if any;
- emitted event schemas and event flags;
- light- or Shadow-DOM policy;
- owned and server-owned DOM regions;
- form, accessibility, focus, and fallback behavior; and
- cleanup, worker, timer, observer, and external-adapter obligations.

Registration is idempotent for the same compatible definition. A conflicting definition for an
existing tag fails before use; Hedron never silently keeps whichever module loaded first.

### 3. Server-rendered fallback and upgrade

Every Supported first-party element starts from meaningful server-rendered content. Before module
load, after module failure, with JavaScript disabled, and during an ABI mismatch, the user can still
understand the content and complete the documented fallback workflow.

Scalar configuration uses validated attributes. Structured initial data uses a declared,
contextually escaped inert payload or a property assignment performed by the registered loader;
it is never embedded as executable JavaScript. Payloads are bounded and may not contain secrets,
ambient credentials, or capabilities. Large datasets use existing source/page/job endpoints rather
than unbounded document state.

Upgrade is idempotent. An element may add behavior and presentation, but it does not discard the
fallback until it has successfully initialized and established equivalent semantics.

### 4. DOM ownership and Shadow DOM

Light DOM is the default because server semantics, forms, assistive technology, application CSS,
and HTMX descendant targeting remain visible. The server owns authored light-DOM children unless a
component contract marks a specific subtree as element-owned.

Shadow DOM is permitted only for intentionally isolated implementation surfaces such as a canvas,
editor, or third-party widget host. A Shadow-DOM element must declare slots, parts, tokens, focus
behavior, label/description relationships, printable/export fallback, and how server validation or
HTMX updates cross the boundary. Shadow DOM is not treated as a security boundary.

Elements may not rewrite arbitrary ancestor/sibling DOM or take ownership of an HTMX region they do
not declare. HTMX targets never enter a closed shadow root.

### 5. HTMX lifecycle

Custom-element platform callbacks are the primary lifecycle:

- `connectedCallback` initializes idempotently;
- `disconnectedCallback` aborts requests and releases listeners, observers, workers, timers,
  object URLs, focus traps, and third-party runtimes;
- `attributeChangedCallback` applies declared scalar changes without reconstructing unrelated
  state.

Hedron's small bridge may observe `htmx:beforeCleanupElement`, `htmx:beforeHistorySave`,
`htmx:afterSwap`, and `htmx:load` for early cancellation, canonical history snapshots,
diagnostics, and compatibility. Elements cannot rely on a global after-swap scan for correctness.

Outer swaps disconnect the old element and connect a new instance. Inner swaps are permitted only
inside declared server-owned regions. Browser-local state is disposable unless the contract
explicitly submits it, reflects it into bounded state, or participates in the phase 0.37 transfer
protocol.

### 6. Attributes, properties, methods, and events

Attributes are strings and cover serializable declarative configuration. Properties may carry
validated structured browser values after upgrade. Public methods are rare, synchronous unless
explicitly documented, and never grant authority unavailable through the server contract.

First-party events are `CustomEvent` instances with versioned detail schemas. Contracts declare
whether each event bubbles, is composed, and is cancelable. Events describe user intent or local
state; they are untrusted input when they reach an HTTP action. Event details never carry secrets,
cookies, bearer tokens, trusted HTML, arbitrary URLs, DOM nodes, or executable callbacks.

The event bridge may map an allowlisted event to an HTMX request or `InteractionGraph` trigger. It
does not evaluate strings as JavaScript or infer a public action from the tag name.

### 7. Forms and validation

Interactive controls prefer native HTML. A custom control must provide material value that native
controls cannot supply for the supported workflow. Form-associated custom elements use
`ElementInternals` where supported and provide a tested light-DOM/native fallback where required.

The contract covers name/value submission, disabled state, reset, restore, autofill expectations,
constraint validation, error association, labels, descriptions, CSRF, HTMX submission, and
server-returned validation fragments. Client validation improves feedback but never replaces
server validation or authorization.

### 8. `ElementStateOwnership`

Every mutable element field declares one ownership mode:

- `controlled`: canonical value comes from server markup/property; user changes emit intent;
- `local`: disposable browser presentation state owned by the connected element;
- `draft`: bounded user work over a versioned server base with submit/discard/conflict policy; or
- `preference`: non-secret, non-authoritative state under `BrowserStorage` policy.

Capabilities and durable server state are never element-owned. Programmatic controlled updates do
not emit user-intent events by default. A dirty draft receiving new server state must explicitly
replace, preserve, perform a proven typed rebase, or enter conflict; it cannot silently use
last-write-wins. Phase 0.37 adds bounded transfer only for eligible drafts.

### 9. `InteractionState`

Every asynchronous element interaction uses the common
`idle -> pending -> success | error | canceled` state machine. Progress is bounded metadata on
`pending`. Contracts declare operation identity, concurrency (`drop`, `replace`, bounded `queue`, or
bounded `parallel`), retry/cancel semantics, disabled scope, `aria-busy`, and status/error
announcements.

The bridge derives state from owned HTMX or registered job/polling lifecycles. HTTP `202` is not
durable-job success, and aborting a browser request is not server cancellation without
acknowledgement. Raw responses, stack traces, secrets, and user data never enter reflected state or
telemetry.

### 10. `OptimisticMutation`

Optimistic UI is explicit and deny-by-default. Each optimistic mutation declares its registered
action, base revision, typed forward patch, deterministic inverse or canonical refetch, idempotency
policy, affected region, timeout/retry/cancel behavior, and conflict resolution.

The browser distinguishes proposed/submitted from confirmed. Only a matching server response makes
the mutation canonical. Rejection rolls back or refetches; conflicts preserve an explicit resolution
path. Optimism is excluded by default for auth/permission changes, irreversible destruction,
payments, secrets, publication, cross-tenant moves, and mutations without safe replay and recovery.
Phase 0.35 first proves the contract on bounded DataEditor/collection edits.

### 11. `GestureOverlayCatalog`

Phase 0.34 locks reusable contracts for reorder/drag-drop, resize/splitter, pointer capture, keyboard
equivalence, touch/scroll/RTL/reduced-motion behavior, and cancellation. Gestures emit typed intent
with stable identities and allowlisted targets; they do not directly mutate authoritative records.

The overlay catalog covers dialog, popover/menu, combobox/listbox popup, tooltip/help, command
palette, and toast/status behavior. It prefers native top-layer APIs with feature-detected local
fallbacks and specifies focus, dismissal, nesting, inert/background, anchoring, viewport, swap,
disconnect, and server/element DOM ownership. Tooltips/toasts are never the sole source of essential
information, and command surfaces invoke registered routes/actions only.

### 12. `ReactMigrationMatrix`

Phase 0.36 publishes a coverage ledger mapping React components, props, callbacks, state, effects,
context, reducers, fetching/mutations, routing, portals, loading/error boundaries, memoization, list
identity, forms, gestures, virtualization, rich widgets, testing, styling, and deployment to Hedron,
HTMX, and element contracts.

Each dependency receives one disposition: replace with native HTML/HTMX, use an existing Hedron
surface, implement a native element, retain a temporary Experimental React island, or declare the
application not a fit. The optional migration-only island bridge has one owned root, pinned assets,
typed props/events, SSR fallback, CSP/supply inventory, deterministic unmount, and a removal ledger;
it is never a default/transitive Hedron runtime or a promise to wrap arbitrary npm packages.

The matrix includes honest non-equivalents for offline-first/client-authoritative applications,
games/canvas runtimes, arbitrary npm ecosystems, and high-frequency collaboration without an
accepted synchronization design.

The detailed state machines and fields are specified in
[the interaction-contract implementation](../implementation/WEB_COMPONENT_INTERACTION_CONTRACTS.md).

### 13. Styling and theming

Elements consume Hedron design tokens through CSS custom properties. Light-DOM elements use scoped
classes; Shadow-DOM elements expose a bounded `part` and token contract. Applications are not asked
to depend on private shadow structure. Theme changes work without redefining elements or rebuilding
application JavaScript.

### 14. Security and supply chain

Supported modules are local, pinned, fingerprinted, declared in the production manifest, and
compatible with strict CSP and Trusted Types enforcement. Inline handlers, `eval`, dynamic code
construction, remote CDN defaults, unsafe HTML sinks, and runtime package download are prohibited.

Third-party libraries run behind explicit adapters with origin, worker, asset, payload, and cleanup
inventories. Browser dependencies participate in SBOM, provenance, license, vulnerability, and
rollback policy. Custom-element events and Shadow DOM do not create a trust boundary; the server
revalidates all mutations.

### 15. Accessibility and progressive enhancement

Native semantics are preferred over ARIA reconstruction. Each element declares its accessible
name, role/state/value behavior, keyboard model, focus entry/exit/restore, live-region behavior,
zoom/reflow, forced-colors, reduced-motion, localization, and fallback obligations.

Automation covers the pre-upgrade, upgraded, failed-upgrade, validation, swap, and history states.
Representative controls and rich widgets receive human assistive-technology evaluation before the
platform is called production-grade. Hedron does not turn those results into application-level
WCAG, legal, VPAT/ACR, or certification claims.

### 16. Performance and loading

Routes load only modules required by rendered elements. Definitions are deduplicated and rich
adapters are lazy. The shared bridge target is at most 12 KiB gzip at the 0.33 cut; every exception
requires a recorded budget revision. No global mutation observer or full-document rescan is needed
for ordinary upgrade.

Acceptance includes repeated connect/disconnect leak checks, 100-element upgrade/swap scenarios,
long-task and layout-shift budgets, slow/failing-module fallback, and rich-widget worker cleanup.
Performance claims use end-to-end browser scenarios rather than bundle size alone.

### 17. Phase sequence

| Phase | Capability packet |
|---|---|
| 0.33 | Element ABI, `hedron-elements`, state ownership, registry/assets, SSR fallback, HTMX lifecycle, CSP/a11y/browser baseline |
| 0.34 | `InteractionState`, form-associated controls, gestures/overlays, and interactive semantic primitives |
| 0.35 | `OptimisticMutation` plus data, chart, map, media, and editor convergence on the shared element contract |
| 0.36 | `ReactMigrationMatrix`, third-party author kit, HDJ/plugin/Explorer integration, themes/slots/parts, npm mirror and conformance |
| 0.37 | Typed composition, browser-local state transfer, history/navigation, diagnostics, and failure isolation |
| 0.38 | Stable inventory, compatibility, independent review, human AT, performance, supply chain, and production-grade graduation |

Detailed gates live in the roadmap and the Web Component acceptance specification.

## Alternatives considered

### Continue with per-widget browser modules

Rejected as the long-term direction. It minimizes up-front design but multiplies lifecycle, event,
fallback, accessibility, and supply-chain contracts.

### Adopt React, Vue, Svelte, or another application runtime

Rejected as the framework baseline. Those tools may be used behind an explicit third-party adapter,
but Hedron will not require hydration, a virtual DOM, or an application Node build.

### Use only HTMX and native controls

Retained as the default for request/response interaction and simple controls. It is insufficient for
local editing, charts, maps, media, virtualization, and browser APIs that need persistent behavior
between requests.

### Use Shadow DOM for every component

Rejected. Universal encapsulation would make server semantics, styling, forms, assistive technology,
and HTMX targeting harder. Shadow DOM remains an explicit isolation tool.

### Wrap every Hedron component in a custom element

Rejected. Static text, layout, landmarks, and ordinary links/forms do not benefit from upgrade cost
or a second lifecycle. The platform leans heavily into elements where browser behavior exists.

## Security implications

This program creates more audited JavaScript and browser supply-chain surface. It also replaces
uncoordinated widget scripts with a bounded protocol. The security bar includes strict CSP, Trusted
Types scenarios, no executable configuration, bounded payloads, origin/asset inventories, event
revalidation, cleanup, dependency provenance, and an independent review before graduation.

## Accessibility implications

Custom elements can obscure semantics or break labeling, forms, keyboard behavior, and focus across
Shadow DOM and swaps. The program therefore requires useful pre-upgrade HTML, native semantics,
explicit form and focus contracts, automated state matrices, and human AT evidence. Components that
cannot provide an equivalent fallback remain Experimental.

## Performance implications

The shared platform adds a small browser module but should reduce duplicated loaders and listeners.
Per-route module selection, lazy rich adapters, leak tests, and end-to-end budgets are release gates.
SSR content remains visible before upgrade, so module latency does not block first content.

## Testing strategy

- pure contract tests for element metadata and manifest/version negotiation;
- state-ownership, async-interaction, optimistic-reconciliation, gesture/overlay, and React-migration
  positive/negative fixtures;
- Chromium, Firefox, and WebKit tests for pre-upgrade, upgrade, swap, history, failure, and teardown;
- native form submission plus HTMX validation/CSRF matrices;
- axe/ACT, keyboard, zoom, forced-colors, reduced-motion, and human AT scenarios;
- adversarial CSP, Trusted Types, payload, event, URL, HTML sink, and dependency tests;
- heap/listener/worker/timer leak loops and route-level loading/performance budgets; and
- portable fixtures for FastAPI, Flask, Django, HDJ, plugins, and the conformance runtimes.

## Compatibility and migration

Existing ad hoc browser modules keep working during 0.33–0.35. Each migrated component publishes a
compatibility note and retains its server-rendered fallback. Tag names and event schemas enter the
stable inventory only in 0.38; prior phases are explicitly Alpha/Beta and pinned.

The `ReactMigrationMatrix` is a migration aid, not a promise of universal React compatibility.
Temporary React islands remain Experimental, explicitly inventoried, non-transitive, and removable.

An incompatible ABI change requires either a compatibility adapter or a new tag/protocol version.
Mixed server/module versions fail visibly and preserve fallback content. Applications never need to
rewrite Python routes merely because a component's internal browser implementation migrates.

## Open questions

- Which first-party primitive is the 0.33 end-to-end reference element?
- Should `hedron-elements` align its package version with the flagship train from its first release?
- Which parts of `@hedron/elements` are supported for standalone non-Python consumption in 0.36?
- What exact browser-version floor will apply at 0.33 and at production-grade graduation?
- Which rich surfaces can graduate in 0.35, and which must remain Experimental behind the common ABI?
- Which mutation classes are safe enough for the first `OptimisticMutation` Supported inventory?
- What exact gesture/overlay entries and native-platform fallbacks form the 0.34 locked catalog?
- Does the temporary React-island bridge live in `hedron-elements`, a separate migration package,
  or documentation/reference code only?

These questions must be resolved before this RFC becomes Accepted; none changes the server-owned
state, no-hydration, progressive-enhancement, or HTMX lifecycle boundaries.

## Acceptance criteria

- The roadmap owns every phase from 0.33 through 0.38 with explicit gates and non-goals.
- The implementation specification defines package direction, ABI artifacts, DOM ownership,
  lifecycle, fallback, events, forms, assets, diagnostics, and failure behavior.
- `ElementStateOwnership`, `InteractionState`, `OptimisticMutation`, `GestureOverlayCatalog`, and
  `ReactMigrationMatrix` have explicit state/authority/failure contracts and phase-owned gates.
- The acceptance specification covers functional, security, accessibility, browser, performance,
  compatibility, documentation, packaging, and supply-chain evidence.
- RFC-0021, RFC-0025, and this RFC have no unresolved normative conflict.
- No phase claims production-grade Web Components before all 0.38 gates are Verified.
