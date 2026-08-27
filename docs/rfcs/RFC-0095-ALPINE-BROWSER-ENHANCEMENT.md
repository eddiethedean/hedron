# RFC-0095: Alpine browser-local enhancement

**Status:** Proposed  
**Phase:** 0.67  
**Decision:** D-113, refined by D-115 / D-116  
**Planning baseline:** `v0.66.2`  
**Target:** `v0.67.0`  
**Implementation:** [ALPINE_INTEGRATION_067](../implementation/ALPINE_INTEGRATION_067.md)  
**Capability and widget audit:**
[ALPINE_CAPABILITY_AUDIT_067](../implementation/ALPINE_CAPABILITY_AUDIT_067.md)  
**Acceptance:** [RELEASE_0_67](../acceptance/RELEASE_0_67.md)  
**Contract freeze:** [contract-freeze-067.toml](../acceptance/contract-freeze-067.toml)  
**Compatibility BOM:** [compatibility-bom-067.toml](../acceptance/compatibility-bom-067.toml)  
**HTMX/Alpine boundary:**
[HTMX_ALPINE_BOUNDARY_1_0](../api/HTMX_ALPINE_BOUNDARY_1_0.md)  
**Component engine dispositions:**
[COMPONENT_ENGINE_DISPOSITIONS_067_1_0](../implementation/COMPONENT_ENGINE_DISPOSITIONS_067_1_0.md)  
**Follow-on:** [RFC-0096](RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md)

## Summary

Phase 0.67 adds Alpine.js as Hedron's opt-in browser-local enhancement layer for interactions that
do not require a server round trip. Alpine owns ephemeral presentation state, local DOM projection,
events, focus, geometry, and bounded browser preferences. Hedron and HTMX continue to own routes,
requests, server data, authorization, mutations, durable state, authoritative validation, response
HTML, targets, and swaps.

The runtime is exact-versioned, vendored, self-hosted, and absent when unused. Hedron uses Alpine's
CSP build and never adds `unsafe-eval`, a CDN dependency, a Node requirement for application
authors, hydration, a virtual DOM, or a mandatory client store. A typed Python/HDJ authoring lane,
one reviewed expression escape hatch, static checks, browser lifecycle integration, and a complete
feature-disposition inventory make the integration inspectable.

The 1.0-compatible developer contract is an entry condition for implementation, not a late product
of the runtime work. `FREEZE-067` must lock the task-to-interface graph, exact canonical return
shapes, the closed interaction/outcome model, browser-feature demand ownership, the warning
registry schema, and the cross-version compatibility BOM before W1 begins. Later probes may change
an implementation or maturity label, but cannot silently add another public calling form.

Phase 0.67 also ships an opt-in preview of the complete unified HTMX/Alpine interaction model and
canonical authoring surface intended for Hedron 1.0. The 1.0 release makes that model the default,
removes parallel compatibility paths, and may refine implementation internals, but it may not
require a public runtime capability or canonical calling form absent from 0.67. This establishes
the required compatibility direction: every Hedron 1.0 application runs on Hedron 0.67, while some
applications using legacy or explicitly transitional 0.67 interfaces will require migration to
1.0.

For common Hedron-owned interactive components, 0.67 ships the Alpine-backed canonical behavior
and retains existing delegated controllers/custom elements only as warned compatibility paths.
In 1.0, Alpine is the sole enhanced browser-local behavior engine for those widgets. Semantic
server HTML and adequate native element behavior remain the baseline, HTMX retains server
requests/swaps, and separately owned chart/map/data/editor hosts are not mechanically rewritten.

This is not a one-way Web-Component removal program. `ENGINE-067` audits every current tag and
browser controller in both directions. Lightweight common wrappers migrate to native HTML plus
Alpine when the element boundary adds no distinct value; `hedron-chart`, `hedron-map`, and
`hedron-data-editor` remain specialist Web Components; and current or future code-editor, terminal,
advanced-upload/media, canvas, or WASM hosts may be promoted to Web Components when the specialist
host criteria pass. The public Web Component ABI and third-party authoring path remain supported.

## Upstream research (reviewed 2026-08-26)

The reviewed upstream is Alpine.js `3.16.3`, released 2026-08-24 and latest at the time of research.
The
package is MIT-licensed and its `alpinejs` package uses Vue's reactivity package internally. The
release pin is provisional until Stage 0 reproduces the artifacts, digests, license packet, CSP
behavior, and browser matrix from a clean checkout.

Primary sources:

- [Alpine start and core examples](https://alpinejs.dev/start-here)
- [official directive, magic, global, and plugin inventory](https://alpinejs.dev/plugins/)
- [CSP build and expression constraints](https://alpinejs.dev/advanced/csp)
- [extension and initialization lifecycle](https://alpinejs.dev/advanced/extending)
- [Alpine `3.16.3` release](https://github.com/alpinejs/alpine/releases/tag/v3.16.3)
- [official tagged `@alpinejs/ui` source](https://github.com/alpinejs/alpine/tree/v3.16.3/packages/ui)
  and [MIT-declared package manifest](https://github.com/alpinejs/alpine/blob/v3.16.3/packages/ui/package.json)
- [Alpine license](https://github.com/alpinejs/alpine/blob/main/LICENSE.md)
- [Alpine UI Components product boundary](https://alpinejs.dev/license)
- [W3C ARIA Authoring Practices widget patterns](https://www.w3.org/WAI/ARIA/apg/patterns/)
- [HTMX scripting and Alpine integration notes](https://htmx.org/docs/#scripting)
- [HTMX extension catalog and Alpine morph disposition](https://htmx.org/extensions/)

### Capability inventory

| Upstream area | Alpine surface | 0.67 disposition |
|---|---|---|
| Local state and lifecycle | `x-data`, `x-init`, `x-effect`, `$watch`, `$nextTick`, `$data`, `$root` | Required through the CSP-safe typed/reviewed expression contract |
| Events and identity | `x-on`, `$dispatch`, `x-ref`, `$refs`, `x-id`, `$id`, `$el` | Required; long-form attributes are canonical and events remain DOM-local |
| Projection | `x-bind`, `x-text`, `x-show`, `x-if`, `x-for`, `x-model`, `x-modelable`, `x-transition`, `x-cloak` | Required through typed sinks and semantic initial HTML, except `x-cloak` is bounded to nonessential duplicate/decorative projection with an explicit failure fallback |
| DOM escape directives | `x-ignore`, `x-teleport` | Progressive; bounded targets, cleanup, focus, and HTMX ownership evidence required |
| HTML injection | `x-html` | Excluded from the canonical API; a trusted Experimental path requires exact CSP-artifact evidence and never accepts user or third-party content |
| Registered reuse | `Alpine.data()`, `Alpine.bind()`, `Alpine.store()` | Required registration path; stores are non-authoritative, bounded, and non-sensitive |
| Extension API | directives, magics, plugins, cleanup hooks | Supported only for reviewed registered local modules; no response-time registration |
| Official headless UI candidate | `@alpinejs/ui`: combobox, dialog, disclosure, listbox, menu, popover, radio, switch, tabs | Preferred widget substrate if exact tagged/published license, CSP, lifecycle, accessibility, browser, stability, and budget probes pass |
| Official plugins | Mask, Intersect, Resize, Focus, Collapse, Anchor | Required, demand-driven, exact-versioned assets |
| Persistence | Persist | Progressive; UI preferences only, namespaced/versioned, no secrets or domain truth |
| DOM morphing | Morph | Progressive candidate; ordinary replacement/reset is the Supported baseline, and Morph is admitted only if its full interoperability evidence passes |
| Sorting | Sort | Progressive local ordering; no mutation or persistence claim without an ordinary server action |

The inventory is exhaustive for the documented Alpine core and official plugin catalog. A feature
is not silently omitted: unsupported syntax or a non-admitted plugin fails static/runtime checks
with a named disposition.

The independently designed widget program covers common disclosure, overlay, menu, tabs, choice,
notification, tooltip, carousel, listbox, combobox, field-helper, and sortable needs by enhancing
existing Hedron components. It uses W3C APG and first-party Hedron behavior as design inputs. The
separately licensed Alpine UI Components product is neither source material nor a compatibility
target; its restricted source, subscriber content, and markup are excluded from development and
tests.

The migration inventory explicitly covers `hedron-ui.mjs`, `hedron-disclose.mjs`, and overlapping
common primitives in `hedron-elements`. A thin HTMX/Alpine coordinator remains necessary, but a
legacy controller and an Alpine module may not both be canonical implementations of one widget.

The public PineMix catalog adds useful breadth evidence, but its retrieved license page does not
currently state modification/redistribution terms and its examples assume Tailwind. Hedron does
not copy or vendor it without an exact permissive grant. MIT sources such as Alpine's own UI
package, Pines, and Penguin UI may be evaluated selectively with immutable provenance,
attribution, dependency removal, and Hedron's full CSP/accessibility/lifecycle review.

## Authority boundary

Alpine is appropriate for:

- disclosure, dropdown, tabs, modal visibility, and focus management;
- filtering or sorting values already present in an authorized page;
- input masking, character counts, copy controls, and presentation-only validation hints;
- transitions, viewport/size observation, anchoring, and reduced-motion-aware effects; and
- non-sensitive browser preferences such as a dismissed teaching hint or local density choice.

Alpine must not be the only authority for:

- authentication, authorization, tenancy, CSRF, or sensitive-data decisions;
- database reads, mutations, payment/destructive operations, or durable jobs;
- authoritative form validation, canonical navigation/history, or server-side filtering;
- cross-worker/session/domain state, audit records, secrets, or trusted HTML sanitization; or
- HTMX request, response, target, swap, retry, concurrency, or stale-generation policy.

When an interaction crosses that boundary, the Alpine control submits or triggers an ordinary
Hedron/HTMX form, link, fragment, or command. Its local pending presentation is disposable; the
server response remains authoritative.

## Proposed design

### Preview the unified 1.0 interaction model

0.67 must not bolt Alpine attributes beside the existing collection of HTMX helpers and leave the
integration problem for application authors. It introduces the 1.0 model as a closed interaction
value whose effect is exactly one of `local`, `request`, or `combined`. Shared event, fallback,
accessibility, reconciliation, and trace facts live around that discriminant; unrelated optional
fields cannot form invalid combinations. The declaration describes:

- the initiating DOM event and modifiers;
- local Alpine state/effects that can complete without a request;
- an optional registered Hedron view, command, form, or navigation effect;
- HTMX method, target, swap, synchronization, generation, and fallback behavior;
- pending/success/error/stale presentation and accessibility behavior;
- local-state reset, retain, or versioned reconciliation after the server response; and
- stable identity and trace facts across Python, HDJ, HTML, HTMX, and Alpine.

The compiler lowers the declaration into Alpine directives for browser-local work, HTMX attributes
for requests/swaps, and existing Hedron handles/policies for server authority. It does not invent a
third runtime. Direct `Hx`, handle helpers, raw HTMX attributes, `AlpineAttrs`, and registered
advanced expressions remain available in 0.67, but the task-oriented interaction declaration is
the 1.0-compatible path. Its final public shape is part of `FREEZE-067` and must be locked before
W1 begins. The normative role, DOM, state, lifecycle, fallback, security, and non-interference rules
are defined by the [1.0 HTMX/Alpine boundary](../api/HTMX_ALPINE_BOUNDARY_1_0.md).

### One browser feature plan and document closure

`FREEZE-067` locks one immutable document browser plan that consolidates Alpine core/plugins,
registered modules, official-UI modules, and existing HTMX extension activation. Canonical Hedron
components and `Interaction` values contribute their exact typed requirements as part of rendering;
authors do not repeat an implementation plugin list on `Page`. Direct typed Alpine authoring carries
the same requirement facts, and reviewed custom modules enter through the one Advanced registered-
module path. Alpine is never inferred merely because a package is installed.

The PAGE shell compiles the transitive union of the initial tree and every statically declared
reachable view/fragment. A later fragment may use only features in that document plan. Build/static
analysis proves the closure where possible; a versioned plan fingerprint on HTMX requests lets the
server reject an incompatible dynamic fragment with a focused diagnostic. Raw or dynamically
selected fragment routes must declare their requirements through the Advanced path. Fragments never
install plugins, modules, or executable assets after `Alpine.start()`.

Phase 0.67 retains `Page.scripts` and `Page.htmx_extensions` as compatibility inputs, but they
normalize into the same plan and are classified for the 1.0 migration inventory. Separate browser
activation knobs that are not selected for 1.0 emit deprecation warnings in 0.67. A page that emits
reviewed Alpine directives without corresponding requirement facts fails. A page whose tree and
reachable fragments demand no Alpine emits no Alpine bytes or markers.

Assets use the existing registry, application-asset plan, CSP, fingerprint, manifest, head,
fragment, and build authorities. The locally served CSP build loads after registered plugins and
before application Alpine definitions. Duplicate declarations deduplicate by logical identity.

### Typed directives and one reviewed escape hatch

Stage 0 will freeze a single `AlpineAttrs`-style value accepted through normal Python component and
`html.*` attribute normalization. The preferred lane carries:

- JSON-compatible initial state with deterministic serialization;
- normalized long-form directives (`x-on:*` and `x-bind:*`, never shorthand-only APIs);
- finite event/modifier, selector, transition, mask, and plugin options;
- a small expression AST for names, literals, comparisons, assignments, calls to registered local
  methods, and the documented Alpine magic values; and
- provenance used by checks, diagnostics, manifests, Explorer, HDJ, and rendered traces.

Bindings are sink-specific rather than one generic runtime attribute map. Text/scalar, boolean,
ARIA, admitted class token, typed Hedron style-property, `SafeUrl`-purpose, and DOM-property bindings
have separate validation and serialization rules. Dynamic `href`/`src`, arbitrary styles/classes,
attribute dictionaries, and directive bundles are rejected or visibly Advanced; reactive updates
must not bypass the construction-time URL, style, event, and trust policies.

Advanced authors get exactly one explicit reviewed-expression type. It marks trusted application
code, is never constructed from request/user/third-party values, is scanned against the pinned CSP
grammar, and remains distinguishable in manifests. Arbitrary strings do not become executable
merely because an attribute begins with `x-`.

HDJ uses the same normalized directive model and requires an `alpine` feature declaration. Static
analysis checks attribute names, plugin declarations, CSP grammar, trust sinks, and state ownership
without executing templates or JavaScript.

### CSP and trust sinks

The standard Alpine build is excluded because its expression evaluator requires a policy equivalent
to `unsafe-eval`. Hedron vendors only `@alpinejs/csp` for the Supported path and keeps
`script-src 'self'` compatible with existing standard/strict profiles.

Upstream CSP documentation and recent release notes do not provide a sufficient frozen grammar for
Hedron: `3.15.12`, for example, included a CSP member-assignment fix while the documentation still
lists property assignment among unsupported complex expressions. Stage 0 therefore generates an
executable expression corpus from the exact artifact and freezes Hedron's accepted subset from
observed behavior. Patch upgrades must rerun the corpus before the pin changes.

`x-html` is excluded from the canonical API and normal typed lane. A narrowly typed Experimental
trusted-content escape may be proposed only if the pinned CSP artifact proves exact support.
This follows Alpine's own warning that `x-html` must never render user-provided content. Alpine
state serialization rejects secrets and sensitive provenance in tooling where it can be detected;
runtime authorization never relies on that detection.

### HTMX lifecycle and ownership

The integration module coordinates Alpine with the existing `htmx-ext-hedron` lifecycle. The public
contract specifies observable outcomes, not calls to undocumented Alpine internals. It must
cover initial page load, inner/outer replacement, out-of-band swaps, deletion, settle timing,
history save/restore, back/forward navigation, fragment errors, and repeated attach/detach.

The required rules are:

1. new Alpine roots initialize once after the final settled DOM is available;
2. removed roots run registered cleanup exactly once and leave no observer/listener/teleport leak;
3. ordinary HTMX replacement resets local state unless preservation is explicitly declared;
4. declared preserved state has a versioned, bounded schema and stable root identity;
5. Alpine-created `x-if`/`x-for` content containing HTMX attributes is passed through the supported
   `htmx.process()` path;
6. HTMX remains the request/swap authority, including when the Alpine Morph plugin is used; and
7. Alpine attribute/class/style changes are not overwritten by HTMX settle replay.

Stage 0 must select a mechanism using documented Alpine/HTMX lifecycle surfaces and prove that
Alpine's own DOM observation plus Hedron hooks do not double-initialize or double-clean roots.

Ordinary HTMX replacement with declared reset is the Supported 0.67 baseline. The `MORPH-048`
deferral is re-opened only for the Progressive Alpine-aware candidate owned by `MORPH-067`.
Idiomorph remains separately Deferred unless its own evidence is satisfied. A failed Morph probe
records non-admission and does not block otherwise complete 0.67 replacement/reset behavior.
Admitted morphing may preserve local input/presentation state, but cannot preserve stale server
authority or skip Hedron lifecycle, accessibility, and trace hooks.

### State classes

| State | Owner | Lifetime | Allowed example |
|---|---|---|---|
| Alpine component state | Browser root | Until replacement/navigation | open disclosure, selected local tab |
| Alpine store | Current document | Until full navigation | coordination among local presentation islands |
| Persist plugin value | Named browser storage key | Versioned preference lifetime | dismissed hint, density preference |
| Form value | Native form + server binding | Request/validation lifecycle | masked phone field submitted normally |
| Hedron interaction state | Hedron/HTMX operation identity | Request generation | pending, stale, terminal outcome |
| Domain/session/job state | Application/server | Application policy | permissions, saved record, job result |

Persist uses only Hedron-owned key namespaces and ordinary `localStorage` or `sessionStorage`.
Custom cookie/storage adapters, unbounded values, secrets, tokens, user records, and values whose
loss changes correctness are rejected or remain unsupported.

## Accessibility

Alpine never supplies semantics merely by making a widget move. Required examples begin with
meaningful native HTML and keep an understandable no-JavaScript state. Dropdown, disclosure, tabs,
dialog, menu/popover, mask, sortable, and anchored-overlay fixtures cover keyboard operation,
focus return, Escape/outside-click behavior, accessible names/states, zoom/reflow, reduced motion,
forced colors, RTL, and screen-reader-visible updates. Focus trapping uses the reviewed Focus
plugin, but native `dialog`, popover, disclosure, and form behavior remain preferred when adequate.

Essential content and the only usable control never rely on `x-cloak`: upstream's cloak stylesheet
keeps content hidden until Alpine removes the attribute, so a refused or missing script would hide it
permanently. Hedron renders the understandable semantic state first and scopes enhanced hiding or
rearrangement behind an initialized-root marker. `x-cloak` is limited to nonessential duplicate or
decorative projection with an explicit failure fallback. `x-show`, `x-if`, `x-teleport`, and Collapse
fixtures prove that focus is never stranded in hidden or removed content. Asset 404, integrity,
CSP-refusal, plugin-failure, and JavaScript-disabled fixtures prove the baseline remains usable. Sort
cannot be advertised as accessible until keyboard reordering and an ordinary non-drag fallback are
verified.

## Performance and packaging

No application build tool is required. Maintainers may use the upstream package build to reproduce
vendored artifacts; users receive reviewed local files plus license and provenance metadata.
Budgets are measured, not guessed, for core-only and each plugin: raw/gzip bytes, request count,
parse/initialization time, DOM-walk cost, observer/listener count, swap cost, and post-cleanup heap.

Pages whose rendered component/interaction tree and declared reachable fragments demand no Alpine
must remain byte-identical except for version-independent manifest schema additions. This promise
does not freeze the semantic markup of a component explicitly migrated to the Alpine-backed 0.67
contract. Demand-driven plugin loading is mandatory. A plugin may not ride the core bundle because
another page uses it.

## Alternatives considered

| Alternative | Disposition |
|---|---|
| Continue custom one-off JavaScript and Web Components only | Rejected for ordinary local interactions; it multiplies lifecycle and authoring interfaces |
| Make Alpine mandatory | Rejected; server HTML and no-JavaScript correctness remain core properties |
| Use Alpine's normal build and add `unsafe-eval` | Rejected; conflicts with Hedron's security profiles |
| Load Alpine/plugins from a CDN | Rejected for production; violates local asset, reproducibility, offline, and CSP policy |
| Let Alpine own requests and domain state | Rejected; duplicates HTMX and server authorities |
| Wrap only a few recipes and hide Alpine directives | Rejected; prevents full feature use and creates another bespoke mini-runtime |
| Permit raw `x-*` string attributes everywhere | Rejected as the default; no provenance, plugin checks, or CSP grammar boundary |

## Compatibility and migration

0.67 is additive for existing 0.66 applications. Existing `Page.scripts`,
`Page.htmx_extensions`, Web Components, and direct HTMX paths continue to run and normalize through
the unified browser plan where applicable. Alpine is opt-in.

Every public documented, exported, generated, configured, CLI, HDJ, and browser-markup 0.67 path
classified for removal in 1.0—including beta and experimental contracts—emits a deprecation
warning in 0.67 whenever it is observed. Python call paths use one public Hedron
deprecation-warning class with replacement, removal version, source location, and diagnostic code.
Build, HDJ, config, CLI, and markup-only paths that cannot warn at the Python call site produce the
equivalent deterministic `hedron check --target 1.0` finding. Private underscore/internal details
are excluded. No 1.0 removal is permitted without one of these 0.67 warning paths and a migration
fixture.

The canonical 1.0 lane is frozen during 0.67 and exercised by a separately versioned fixture
corpus. A 1.0 feature or call form absent from 0.67 is a release blocker. The 1.0 release may remove
only interfaces classified as `compatibility` or `transitional` in the 0.67 inventory and carrying
a deterministic replacement. This is intentionally one-way source compatibility:

```text
Hedron 1.0 canonical applications ⊆ Hedron 0.67 applications
Hedron 0.67 legacy/transitional applications ⊄ Hedron 1.0 applications
```

## Entry contract and remaining Stage 0 questions

Before W1, `FREEZE-067` must resolve and machine-lock the exact public names/signatures, single-tree
handler returns, discriminated `Interaction`, role-indexed `Outcome`, document feature-closure
contract, warning registry, and compatibility BOM. Remaining artifact/evidence questions are:

1. Decide whether reviewed expressions are stable in 1.0 or remain a single Advanced beta escape.
2. Reproduce and freeze the exact `3.16.3` CSP grammar and compatible official plugin/UI artifacts.
3. Decide whether Alpine Morph earns Progressive admission after three-engine lifecycle probes;
   ordinary replacement/reset remains Supported either way.
4. Freeze browser-storage namespaces, value limits, schema versioning, and clearing behavior.
5. Define whether `x-teleport` is restricted to a Hedron overlay host or admits reviewed selectors.
6. Lock the public component/HDJ attribute normalization rule without adding another attrs API.
7. Freeze the complete 0.67-to-1.0 removal inventory and warning behavior before the first 0.67 RC.
8. Decide the exact `@alpinejs/ui` package/version disposition after tagged-source, published-
    artifact, CSP, Focus dependency, HTMX lifecycle, accessibility, API stability, and size probes.
9. Freeze the open-source component intake ledger: PineMix remains catalog-only until its license
    grants redistribution; admitted MIT sources carry immutable provenance, notices, and modified-
    source tests without importing Tailwind or another component runtime.

## Acceptance criteria

Phase 0.67 implementation beyond W0 begins only after `FREEZE-067`; the release cuts only when every
Required gate in [RELEASE_0_67](../acceptance/RELEASE_0_67.md) is
Verified with zero undocumented deferral. The cut must prove exact local assets/license/digests,
CSP without `unsafe-eval`, exhaustive feature dispositions, directive and HDJ parity, normal and
optionally admitted Morph lifecycle, document feature closure, failure-safe semantic fallback,
headless-widget disposition, ecosystem-source provenance, security/a11y/performance budgets,
feature-off zero cost, migration tooling, compatibility BOM, and the frozen 1.0-on-0.67 corpus.
