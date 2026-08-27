# Alpine capability audit for Hedron 0.67 and 1.0

**Status:** Research and planning input  
**Reviewed:** 2026-08-26  
**Upstream baseline:** Alpine.js `3.16.3`, subject to reproducible Stage 0 pinning  
**Phase contract:** [RFC-0095](../rfcs/RFC-0095-ALPINE-BROWSER-ENHANCEMENT.md) / D-116  
**Implementation plan:** [ALPINE_INTEGRATION_067](ALPINE_INTEGRATION_067.md)  
**1.0 follow-on:** [RFC-0096](../rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md)

The authoritative bidirectional native/Alpine/Web-Component audit is
[COMPONENT_ENGINE_DISPOSITIONS_067_1_0](COMPONENT_ENGINE_DISPOSITIONS_067_1_0.md). This capability
audit determines what Alpine can safely supply; it does not presume Alpine is the correct engine
for every component.

## Goal

Hedron should take full advantage of Alpine rather than expose a token toggle helper. “Full” means:

- every documented core directive, magic, global, advanced hook, and official plugin has an exact
  Supported, Progressive, Experimental, Advanced, or Excluded disposition;
- all admitted features are reachable through one normalized Python/HDJ/manifest model;
- reusable and complex behavior uses registered modules instead of growing inline expressions;
- plugins load only when used and retain their complete admitted modifier/options surface;
- HTMX and Alpine share one lifecycle, identity, state-reconciliation, and tracing contract; and
- the 1.0 `Interaction` API compiles local-only, server-only, and combined behavior without
  reducing Alpine to the least common denominator.

Full use does not transfer request, authorization, validation, mutation, persistence, or durable
state authority into the browser.

## Official sources reviewed

- [Start Here](https://alpinejs.dev/start-here),
  [installation](https://alpinejs.dev/essentials/installation),
  [state](https://alpinejs.dev/essentials/state),
  [templating](https://alpinejs.dev/essentials/templating),
  [events](https://alpinejs.dev/essentials/events), and
  [lifecycle](https://alpinejs.dev/essentials/lifecycle)
- [CSP build](https://alpinejs.dev/advanced/csp),
  [reactivity](https://alpinejs.dev/advanced/reactivity),
  [extending](https://alpinejs.dev/advanced/extending), and
  [async](https://alpinejs.dev/advanced/async)
- all directive, magic, global, and plugin pages linked from the official navigation
- [HTMX scripting and third-party integration](https://htmx.org/docs/#scripting),
  [HTMX events](https://htmx.org/events/), and
  [`hx-preserve`](https://htmx.org/attributes/hx-preserve/)
- [Alpine `3.16.3` release](https://github.com/alpinejs/alpine/releases/tag/v3.16.3), the
  tagged [`packages/ui` source](https://github.com/alpinejs/alpine/tree/v3.16.3/packages/ui), its
  [`@alpinejs/ui` package manifest](https://github.com/alpinejs/alpine/blob/v3.16.3/packages/ui/package.json),
  and the repository
  [MIT license](https://github.com/alpinejs/alpine/blob/main/LICENSE.md)
- the public [Alpine UI Components catalog](https://alpinejs.dev/components) and its separate
  [product license](https://alpinejs.dev/license); and
- the W3C [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/) and complete
  [widget-pattern index](https://www.w3.org/WAI/ARIA/apg/patterns/)
- PineMix's public [30-component catalog](https://pinemix.com/components),
  [dependency guide](https://pinemix.com/docs/getting-started),
  [license page](https://pinemix.com/license), and
  [terms page](https://pinemix.com/terms-of-service); and
- the explicit source/license pages for [Pines](https://github.com/thedevdojo/pines),
  [Penguin UI](https://www.penguinui.com/docs/license),
  [Alpine Components](https://alpinecomponents.dev/license), and
  [Vimesh UI](https://github.com/vimeshjs/vimesh-ui)

Alpine now has two UI surfaces that must not be conflated:

- “Alpine UI Components” remains a paid copy-paste/tutorial product under a separate restrictive
  product license. Its license prohibits redistribution and specifically identifies a competing UI
  component project as impermissible use. Hedron does not buy, inspect, translate, copy, vendor,
  reproduce, or claim compatibility with that material.
- The official Alpine repository separately contains `packages/ui`, whose package manifest names
  `@alpinejs/ui`, describes it as headless UI components, and declares MIT. Its source exposes nine
  directive families: combobox, dialog, disclosure, listbox, menu, popover, radio, switch, and
  tabs. The `v3.16.3` tag and published npm metadata both declare version `3.16.3` and MIT; the npm
  artifact records integrity `sha512-+XqQcRijbRZopSQLZJsFlmILB73E5k7fmGv4eesk3wOHZ+jAZ3s0IyXASGT+gpH8Qi7+wSNMI2V9QVegB93AQA==`.
  It is therefore a genuine open-source candidate, not an inference from the paid product pages.
  Stage 0 still reproduces the tarball and records its complete files/notices before vendoring.

Hedron's widget program is independently designed from W3C APG behavior/keyboard guidance, web
platform specifications, existing Hedron components, public Alpine runtime APIs, and Hedron's own
accessibility contracts. Shared generic names such as dialog, tabs, and combobox describe standard
web patterns, not Alpine product compatibility. No contributor may use restricted Alpine UI source,
screencasts, subscriber materials, or copied markup as an implementation or test input. A release
provenance check records the public standards and first-party designs used for every widget.

The preferred Stage 0 path is to test the exact `@alpinejs/ui` artifact as the behavior substrate
for its nine widget families. If it passes CSP, lifecycle, browser, accessibility, size, and license
gates, Hedron vendors it beside the CSP core and generates its directives from existing `ui.*`
components. Hedron does not expose `x-dialog` versus a custom Hedron dialog module as two choices.
If the package fails a gate, each family gets a recorded fallback or Progressive disposition; the
project does not silently fork the full package.

## Runtime and activation

Hedron vendors one exact `@alpinejs/csp` build and compatible exact official plugin/UI artifacts.
Core, plugin, and UI packages are pinned independently when upstream package versions differ. The
normal Alpine build is excluded because its expression evaluator requires CSP `unsafe-eval`.
Applications do not load from a CDN, install Node, call `Alpine.start()`, choose script order, or
register response-time plugins. The application asset plan guarantees:

1. reviewed extensions and demanded plugins register before the single `Alpine.start()`;
2. each plugin precedes core in script-tag builds or registers before start in a module build;
3. Alpine is absent when no normalized feature demands it;
4. duplicate core/plugin/module registration fails rather than starting a second Alpine instance;
5. versions, hashes, licenses, dependency order, and feature sources appear in build manifests; and
6. the same plan is used by Python, HDJ, adapters, Explorer, tests, and production builds.

Demand is a render/route fact, not a manual plugin checklist. Canonical components and
`Interaction` values contribute exact requirements; direct typed Alpine values carry their own
requirements; reviewed custom modules use the one Advanced registration path. The PAGE plan closes
over the initial tree plus every declared reachable view/fragment. Later fragments must be a subset
of that plan, verified statically where possible and by a versioned plan fingerprint at request
time. A fragment never installs a missing plugin/module after start.

For Hedron-owned common widgets, Alpine is the sole enhanced browser-local behavior engine in 1.0.
This does not replace semantic server-rendered HTML, sufficient native element behavior, or HTMX
request/swap authority. It eliminates parallel delegated controllers, one-off per-widget scripts,
and duplicate Web Component implementations for the same Hedron task. Thin Alpine registration,
HTMX lifecycle coordination, retained/promoted specialist Web Components, and provider-owned
integrations remain ordinary implementation modules rather than alternative application-facing
runtimes. The accepted public Web Component ABI and third-party authoring path remain supported.

## Directive inventory

| Directive | Hedron use | 0.67 / 1.0 disposition and guardrails |
|---|---|---|
| `x-data` | Local reactive state and method scope | **Required.** Typed serializable initial state for small cases; named `Alpine.data()` module for reusable or complex behavior. Nested scope and shadowing are diagnosed. No secrets or domain objects. |
| `x-init` | Element initialization | **Required.** Local initialization and registered method calls. Direct `fetch()` is not a canonical request path; server work uses a view/action interaction. Initialization must be idempotent across swaps/history. |
| `x-show` | Keep an element mounted while toggling visibility | **Required and preferred** for disclosure, tabs, dropdowns, and transient panels. Semantic initial HTML, initialized-root enhancement, ARIA state, focus behavior, and reduced-motion rules are generated together. Essential content is not cloaked before successful initialization. Hidden DOM is not a security boundary. |
| `x-bind` | Reactive HTML/ARIA/class/property binding and directive bundles | **Required.** Separate typed scalar, boolean, ARIA, admitted-class, Hedron-style-token, `SafeUrl`-purpose, and DOM-property bindings plus registered `Alpine.bind()` bundles. Dynamic URL/style/class sinks and arbitrary directive dictionaries are Advanced or rejected because they can bypass styling, URL, and syntax policy. |
| `x-on` | DOM and custom-event handling | **Required.** Full admitted keyboard, mouse, custom-event, target, timing, propagation, and listener-option modifiers. The `Interaction` model owns canonical event spelling. `.prevent` cannot destroy a valid no-JS form/link fallback without an equivalent enhanced path. |
| `x-text` | Safe text projection | **Required.** Preferred dynamic-content projection; values become text, never markup. |
| `x-html` | `innerHTML` projection | **Excluded from the canonical API.** Upstream warns that it is trusted-content-only and the CSP documentation lists HTML injection as unsupported. An Experimental `TrustedHtml` path is possible only if the pinned artifact probe proves exact behavior without weakening serializer/CSP policy. |
| `x-model` | Local two-way form-control state | **Required.** Text, textarea, checkbox, radio, select, multi-select, and range plus admitted lazy/change/blur/enter/number/boolean/debounce/throttle/fill behavior. Native form fields remain the submitted truth; Alpine values do not bypass server parsing. |
| `x-modelable` | Expose a reusable component's internal value to `x-model` | **Progressive.** Useful for Hedron composite controls and reviewed modules. Requires one typed value contract, native form fallback, cleanup, and swap evidence. |
| `x-for` | Client projection of bounded local collections | **Required.** Only over already authorized/bounded local data. A `<template>` with one root is enforced and a stable key is required for reorderable/stateful items. Not a client database, paginator, or server-filter replacement. |
| `x-transition` | Enter/leave animation | **Required.** Helper and class-phase forms normalize to Hedron motion tokens/recipes. Durations, delays, opacity, scale, origins, and phase classes are bounded; reduced motion remains authoritative. |
| `x-effect` | Auto-tracked reactive side effect | **Required.** Presentation effects only, with cleanup and loop diagnostics. Network mutations, authorization decisions, and persistent writes are not effects. |
| `x-ignore` / `.self` | Alpine ownership boundary | **Advanced.** Used for third-party widgets, Web Components, or HTMX-owned islands. The boundary, cleanup owner, and nested activation behavior must be explicit. |
| `x-ref` | Static element reference | **Required.** References are scoped and static; upstream does not support dynamically evaluated V3 refs. Generated recipes prefer stable typed refs/IDs over general queries. |
| `x-cloak` | Hide pre-initialized content | **Bounded.** Upstream's rule hides until Alpine removes the attribute, so essential content and the only usable control may not use it. Admit it only for nonessential duplicate/decorative projection with a tested failure fallback; enhanced hiding otherwise scopes beneath an initialized-root marker. |
| `x-teleport` | Move template content to a portal target | **Progressive.** Bounded application portal targets only. Requires one template root, event forwarding, focus, inertness, layering, cleanup, HTMX target, history, and ownership evidence. |
| `x-if` | Conditionally create/destroy content | **Required with caution.** Used only when destruction is intended; `x-show` remains the toggle default. One template root is enforced. Inserted content containing `hx-*` is automatically processed exactly once. |
| `x-id` | Scoped unique-ID groups | **Required.** Integrates with Hedron logical identity and accessible relationships without accepting IDs as authorization or durable identity. |

Long-form `x-on:*` and `x-bind:*` names are canonical in serialized output. Shorthands such as `@`
and `:` may be accepted only by the reviewed expression escape hatch and never create a second
Python authoring model.

## Event and model modifier coverage

The normalized modifier grammar must cover the complete pinned upstream set, not a hard-coded
counter subset:

- keyboard keys and modifier chords, expressed from valid `KeyboardEvent.key` names;
- mouse/pointer modifier keys;
- `.prevent`, `.stop`, `.outside`, `.window`, `.document`, `.once`, `.debounce`, `.throttle`,
  `.self`, `.camel`, `.dot`, `.passive`, and `.capture` where supported by the pin;
- explicit debounce/throttle durations with frozen numeric bounds;
- model timing/conversion modifiers including `.lazy`/`.change`, `.blur`, `.enter`, `.number`,
  `.boolean`, `.debounce`, `.throttle`, and `.fill` where supported by the pin; and
- custom DOM events with bounded JSON-compatible detail.

Modifier combinations are order-normalized and validated. Conflicting combinations, unbounded
durations, unknown keys, and presentation that defeats native keyboard/form behavior fail checks.

## Magic inventory

| Magic | Intended use | Disposition |
|---|---|---|
| `$el` | Current element access | **Advanced.** Prefer typed binding/effects; raw DOM mutation can conflict with HTMX and rendering. |
| `$refs` | Static scoped element lookup | **Required.** Static names only; no dynamic V2-style refs. |
| `$store` | Page-wide browser presentation state | **Progressive.** Registered, typed, bounded stores only; never auth, tenant, form truth, or domain truth. |
| `$watch` | Observe a named property with old/new values | **Required.** Presentation/reconciliation effects; detect self-mutating infinite loops. |
| `$dispatch` | Bubble a custom DOM event | **Required.** Primary Alpine-to-Interaction/HTMX/Web Component bridge with namespaced event names and bounded detail. |
| `$nextTick` | Run after reactive DOM projection | **Required.** Focus, measurement, and HTMX processing after `x-if`; avoid timing sleeps. |
| `$root` | Current Alpine component root | **Required.** Scope/lifecycle inspection and bounded root-relative behavior. |
| `$data` | Current data stack access | **Advanced.** Useful for module integration and diagnostics; not a serialization or cross-root state API. |
| `$id` | Resolve an `x-id` scoped identifier | **Required.** Generated accessible relationships and stable local references. |

Plugin-provided magics such as `$persist`, `$focus`, `$anchor`, `$input`, `$money`, `$item`, and
`$position` are admitted only with their owning plugin and inherit its disposition.

## Globals and extension APIs

| API | Hedron policy |
|---|---|
| `Alpine.data()` | Canonical implementation for named reusable local behaviors. Factories may accept bounded explicit parameters, expose `init()`/cleanup-aware methods, and are registered before start. |
| `Alpine.bind()` | Canonical reusable attribute/directive bundle beneath typed recipes. Bundle contents are normalized and source-mapped. |
| `Alpine.store()` | Reviewed app-scoped presentation stores only. Namespaced ownership, schema/version, size, sensitivity, and reset policy are required. |
| `Alpine.reactive()` / `Alpine.effect()` | Advanced module authoring tools. Effects must be tied to an Alpine cleanup owner; do not create an independent application state system. |
| `Alpine.directive()` | Reviewed registered extensions only. The implementation must use auto-cleaned reactive effects and explicit `cleanup()` for listeners/observers/resources. |
| `Alpine.magic()` | Reviewed narrow helpers only. No broad access to secrets, arbitrary network calls, global evaluation, or raw application services. |
| `Alpine.plugin()` | Internal asset-plan registration for pinned official or separately reviewed plugins before start. No response-time or arbitrary package discovery. |
| expression evaluation helpers | Internal to reviewed directives. Untrusted strings never become expressions; repeated evaluation uses the prepared/evaluate-later form and cleanup. |

`alpine:init` is the single pre-start registration phase and `alpine:initialized` is the single
post-start application hook. Hedron owns start ordering and refuses multiple starts.

## Official plugin inventory

| Plugin | Full-use plan | Maturity / boundary |
|---|---|---|
| Mask | Fixed `*`/`a`/`9` masks, dynamic masks, `$input`, and bounded `$money` formats | **Required.** Formatting is not parsing or validation; native value, locale, accessibility, password/payment, paste, autofill, and server-error evidence required. |
| Intersect | enter/leave, once, half/full/custom threshold, margin, and parent-root observation | **Required.** Local visibility/lazy presentation. A server request triggered by visibility compiles through `Interaction`, not a hidden `fetch`. Observer cleanup and fallback are required. |
| Resize | element and document observation with `$width`/`$height` | **Required.** Presentation/geometry only; batching, loop protection, observer cleanup, SSR fallback, and container-query preference are documented. |
| Persist | `$persist`, custom namespaced keys, app-approved storage | **Progressive.** Upstream defaults to `localStorage` with no expiry; Hedron therefore requires app/version/scope namespacing, schema, size, expiry/cleanup, unavailable-storage behavior, and a non-sensitive UI-preference classification. |
| Focus | `x-trap`, nested traps, inert/noscroll/noreturn/noautofocus options, and `$focus` traversal | **Required.** Powers dialog, popover, menu, tabs, listbox, and command-palette recipes. Native semantics, focus return, nested overlays, HTMX removal, forced cleanup, and human AT evidence remain required. |
| Collapse | height animation over `x-show`, duration and minimum behavior | **Required.** Disclosure/accordion enhancement with reduced-motion and semantic content access. It never replaces `x-show` or disclosure state. |
| Anchor | Floating-UI positioning, placements, fixed/offset/noflip, and manual `$anchor` values | **Required.** Used by one Hedron overlay recipe with viewport/scroll/zoom/RTL/mobile and cleanup evidence. Manual style is Advanced. |
| Morph | state-preserving DOM reconciliation, stable keys, lifecycle hooks, and lookahead option | **Progressive candidate.** Ordinary replacement/reset is Supported. Hedron may admit exactly one Morph authority only after the full matrix passes; a failed probe records non-admission without blocking 0.67. Server HTML remains authoritative; local state preservation is declared and versioned, not accidental. |
| Sort | sortable lists/groups, item identity/position, handles, ignored controls, ghosting, and configuration | **Progressive.** Local reorder is presentation only. Persistence requires an explicit action with revision/auth/idempotency. Keyboard/non-drag controls and semantic order fallback are mandatory. |

Plugins are demand-loaded individually. “Support all plugins” does not mean ship all bytes on every
page or treat every plugin feature as equally mature.

`@alpinejs/ui` is decided per widget family and stays hidden behind the existing Hedron component
contract. A single package asset may contain several upstream modules, but that packaging fact may
not create a second `Alpine*` component family or force an upstream behavior where native Hedron
semantics are stronger.

## Independent widget and behavior program

Hedron should use Alpine to complete its existing built-in browser-local UX with independently
implemented, typed recipes. It must enhance the existing semantic component instead of introducing
parallel names such as `AlpineDialog` or a second recipe API:

1. disclosure and accordion;
2. dropdown/menu button and context menu;
3. dialog, alert dialog, drawer, and popover;
4. tabs and roving-focus composite controls;
5. tooltip and anchored teaching hint;
6. combobox/listbox/local filtering over already authorized options;
7. switch/radio group and bounded composite form controls;
8. local counter, character count, password reveal, copy feedback, and clear/reset controls;
9. mask/format previews whose native submission remains unchanged;
10. carousel controls and local media presentation without hiding full semantic access;
11. lazy reveal/measurement responsive behavior where CSS cannot express the task;
12. optimistic-looking pending presentation tied to authoritative Hedron operations;
13. persisted non-sensitive density/color/teaching preferences; and
14. sortable/reorderable presentation with complete keyboard and server-persistence alternatives.

Each recipe declares state keys, directives/plugins, semantic initial HTML, keyboard model, ARIA,
focus, no-JS behavior, HTMX lifecycle, cleanup, reduced motion, persistence sensitivity, and test
matrix. A recipe does not create another state or interaction API.

### Practical coverage plan

The public Alpine catalog lists nine styled examples, nine headless widget categories, and twelve
third-party integrations. Hedron does not use their implementations, but it should meet the common
application needs that overlap the standards-based inventory below.

| Widget need | Existing Hedron base | 0.67 outcome | 1.0 outcome |
|---|---|---|---|
| disclosure / accordion | `Expander`, `hedron-elements.Disclosure` | Consolidate on one semantic base; Alpine supplies single/multiple-open policy, Collapse, IDs, and focus-safe transitions | One `ui.disclosure` / `ui.accordion` family; retire duplicate names after warnings |
| dialog / alert dialog / drawer | two `Dialog` implementations | Consolidate behavior around native dialog semantics plus Focus; add alert and drawer recipes only where their distinct semantics are proven | One dialog family with explicit modal/alert/drawer variants and one open/close interaction |
| menu button / dropdown / context menu | `MenuButton`, `ContextMenu`, `Popover` | Add roving focus, Escape, outside close, typeahead where applicable, Anchor positioning, and focus return | One menu primitive; “dropdown” is presentation terminology, not another behavioral API |
| popover / teaching hint | `Popover`, `Help` | Upgrade placement, collision, dismissal, focus, and HTMX cleanup using Anchor/Focus | One popover primitive with non-modal and teaching-hint recipes |
| tabs | `Tabs` | Add APG keyboard behavior, activation policy, stable ID relationships, and preserved/reset state tests | One tabs component; static and enhanced renderings are modes of the same component |
| switch / radio group / segmented choice | `ToggleSwitch`, `RadioGroup`, `SegmentedControl` | Keep native form controls authoritative while Alpine provides local projection and group behavior | One field-family contract, never separate “headless” and “form” choices for the same task |
| notifications / toast / alert | `Toast`, `ToastHost`, `Alert`, `Status` | Add queue, timed/persistent dismissal, pause, live-region policy, and swap-safe cleanup | One notification service plus semantic alert/status components; severity controls interruption |
| tooltip / described help | `Tooltip`, `Help` | Replace title-only enhancement with focus/hover/Escape behavior where tooltip is appropriate; retain visible help as default | One tooltip recipe; interactive hover content is a popover, not a tooltip variant |
| carousel / gallery | `Carousel`, `Gallery` | Add manual controls, current-slide status, pause-on-focus/hover, reduced motion, and full-content/no-JS access; autoplay remains Progressive | One carousel family; external carousel libraries are not a second supported route |
| listbox / local select | `Select`, `MultiSelect`, `Pills` | Prefer native select; add listbox only for rendering needs native controls cannot meet, with full keyboard and form fallback | One advanced listbox component with single/multiple modes |
| combobox / autocomplete / command palette | no complete composite | Add bounded local-option combobox as Progressive; remote suggestions cross through a declared view interaction | Graduate only after APG keyboard, IME, mobile, AT, empty/error, and HTMX-race evidence |
| clipboard and field helpers | `ClipboardCopy`, form inputs | Add copy result, clear, reveal, count, mask, local filter, and formatting recipes using native fields/buttons | These remain recipe options on their owning control, not standalone mini-frameworks |
| sortable / reorderable collections | collection components plus Sort plugin | Progressive with handle, keyboard/non-drag controls, semantic order, and explicit persistence action | Graduate only with equivalent pointer, touch, keyboard, AT, revision, and conflict behavior |
| tree, toolbar, composite grid, treegrid | layout/table primitives, no complete widgets | Prototype only; keep Progressive because focus and selection models are complex | Admit individually after APG, virtualization, editing, HTMX, and human AT evidence |
| feed/infinite reveal and window splitter | scroll/layout primitives | Progressive; ordinary pagination and fixed layout remain the fallbacks | Admit only if browser-local behavior materially improves the workflow and cleanup is bounded |

Simple W3C patterns—button, checkbox, link, breadcrumb, landmark, meter/progress, native slider,
spinbutton, table, and ordinary radio group—remain native HTML-first. Alpine may project local
presentation around them, but Hedron does not replace a sufficient native control merely to raise
the component count.

### Third-party integration disposition

The public Alpine product catalog also advertises integrations with charting, rich-text editing,
select enhancement, date/calendar, and carousel libraries. Hedron evaluates these by workflow and
package ownership, not by catalog parity:

| Integration family | Hedron plan |
|---|---|
| Chart.js / ApexCharts-like libraries | Use existing `hedron-charts` authorities and adapters. Alpine may coordinate local presentation but does not create a second chart integration layer. |
| Trix / Quill / SimpleMDE-like editors | Deferred pending sanitization, upload, form, CSP, lifecycle, and server-validation contracts. A generic arbitrary-editor wrapper is too weak. |
| Select2 / Choices-like controls | Prefer native Select and the standards-based listbox/combobox work. Admit an adapter only when it provides a distinct, evidenced capability. |
| Flatpickr / date-range / FullCalendar-like tools | Prefer native date/time inputs. Calendar scheduling crosses domain and server authority; any adapter belongs with its workflow and exact dependency review. |
| Glide / Splide-like carousels | Improve Hedron's own semantic Carousel first. Do not support multiple interchangeable carousel runtimes. |

This preserves the 1.0 rule: broad capability coverage, but one clear Hedron interface for each
task. “Many components” means many useful, evidenced workflows—not many libraries or aliases.

### Free ecosystem audit and PineMix coverage

PineMix currently advertises 30 free copy-paste Alpine/Tailwind components and says they may be
used in personal, commercial, and open-source projects. However, its dedicated license page, as
retrieved on the review date, contains a heading and update date but no license grant or
redistribution text. Hedron may use the public catalog to identify needs, but must not copy, adapt,
or vendor PineMix code until an exact license permits modification and redistribution and its
notices/assets are inventoried. PineMix also assumes Tailwind CSS 4, Tailwind forms/typography,
ordinary Alpine, and the Focus plugin; Hedron cannot inherit those runtime/build assumptions.

Existing Hedron components already provide a semantic starting point for 23 of the 30 public
PineMix categories. The remaining needs receive explicit dispositions:

| PineMix-identified gap | Hedron disposition |
|---|---|
| breadcrumb | Add a native semantic breadcrumb component; Alpine is unnecessary except for optional bounded truncation disclosure |
| command palette | Progressive composition of dialog + combobox + declared actions; local filtering is Alpine, command authorization/execution remains Hedron/HTMX |
| countdown | Add a local `<time>` recipe with pause/resume/background-clock and reduced-update behavior; it cannot be transaction or expiry authority |
| marquee | Excluded from the canonical widget catalog because continuous duplicate motion is rarely task-essential; ordinary content and opt-in Advanced styling remain possible |
| password strength | Add a local advisory meter recipe without exposing the password or claiming policy acceptance; authoritative password rules remain server-side |
| tree view | Progressive APG tree with keyboard/typeahead/selection evidence; ordinary nested lists/disclosures remain the fallback |
| two-factor entry | Add an OTP form recipe with one native submitted value, paste/autofill/mobile support, and no forced auto-submit; verification remains a server action |

The other PineMix needs map to existing Hedron bases: accordion (`Expander`/`Disclosure`), banner
(`Alert`/`EnvironmentBanner`), color picker (`ColorInput`), clipboard (`ClipboardCopy`), dark mode
(`ThemePicker`), dropdown (`MenuButton`/`Popover`), gallery/slider (`Gallery`/`Carousel`), modal
(`Dialog`), notification (`Toast`/`Alert`), off-canvas (`Sidebar`/drawer recipe), popover,
pricing switch (`SegmentedControl`), progress, range/selected slider, rating, select/multi-select,
side navigation, skeleton, table, tag input (`ChipInput`), tabs, and tooltip. Mapping a name does not
claim behavior parity; each still passes the widget gate.

Other sources with explicit permissive terms can be evaluated as attributable implementation or
test inputs:

| Source | License/evidence | Disposition |
|---|---|---|
| Alpine `@alpinejs/ui` | Tagged source and published `3.16.3` metadata declare MIT; nine headless directive families | Preferred candidate substrate; reproduce the tarball and verify CSP build compatibility, APIs, accessibility, lifecycle, and beta/stability status |
| Pines UI | Public GitHub repository declares MIT | Selective source/test reference after per-file provenance; do not import Tailwind markup or create a Pines compatibility layer |
| Penguin UI | License explicitly permits modification and distribution under MIT with attribution | Selective behavioral/test reference; retain notices and translate styling to Hedron contracts |
| Alpine Components | MIT component-loading runtime | Do not adopt by default: remote/lazy templates, HTML insertion, and a second component runtime conflict with local assets, Trusted Types/CSP, and one-way authoring |
| Vimesh UI / headless ecosystem | MIT runtime using custom elements, remote loading, auto-import, and extra magics/directives | Research only unless a distinct interoperability need survives; wholesale adoption would recreate the runtime and custom-element ambiguity 1.0 removes |
| WireKit and other framework suites | MIT examples but coupled to Livewire/Tailwind or another server framework | Workflow/backlog evidence only; do not import framework authority or dependencies |

Every reused code fragment requires a source URL, immutable commit/tag, SPDX expression, copyright
notice, modification record, dependency inventory, and focused review. License permission is only
the entry gate; Hedron still revalidates semantics, keyboard/AT behavior, CSP, Trusted Types, HTMX
swaps, cleanup, no-JS behavior, styling, and all three browser engines. Popularity or an
“accessible” marketing claim is not release evidence.

### Current runtime migration

0.67 must inventory every current common-widget behavior before the 1.0 switch. At minimum:

| Current path | 0.67 treatment | 1.0 treatment |
|---|---|---|
| delegated tabs/dialog/toast/password/swap behavior in `hedron-ui.mjs` | Keep as compatibility behavior, implement the canonical components through registered Alpine modules, and warn when an application explicitly selects the legacy controller path | Remove overlapping local controllers; retain only the unified HTMX/Alpine lifecycle functions that cannot be expressed as component-local state |
| `hedron-disclose.mjs` custom element | Keep installed applications working; map its events/state into the canonical disclosure contract and emit a migration warning for direct authoring | Canonical Hedron disclosure renders semantic HTML plus Alpine; no duplicate custom-element authoring path |
| common UI primitives in `hedron-elements` | Classify each as distinct interoperability value or duplicate Hedron task; provide source-mapped target-1.0 findings | Duplicate dialog/disclosure/form widget paths leave the canonical facade; truly framework-neutral interoperability elements remain Advanced and cannot be the documented Hedron workflow |
| specialist chart/map/data/editor/extra hosts | Do not mechanically rewrite: their third-party lifecycle and package ownership are distinct | Keep reviewed specialist hosts behind their owning package; Alpine may coordinate presentation but does not impersonate the third-party runtime |

The inventory also runs in the other direction: current scripts, native hosts, and Alpine modules
for advanced editors, terminals, uploads/media, grids, canvas, WebGL/WebGPU, or WASM are evaluated
for Web Component promotion when an independent lifecycle and typed host ABI is materially better.
No promotion creates a second public component name or a permanent choice between engines.

The migration is behavior-equivalent, not markup-equivalent. Tests compare semantics, form
submission, keyboard/focus, events, lifecycle, and no-JS outcomes. They do not freeze legacy
controller internals or require 1.0 to retain old data markers.

## CSP expression profile

The official CSP build supports common literals, member access, arithmetic/comparison/boolean and
conditional operations, simple assignments/updates, and method calls, while excluding various
complex expressions, globals, and HTML injection. The documentation contains a notable edge:
`x-model="user.name"` is shown as supported while a direct nested-property assignment is listed as
unsupported. The earlier `3.15.12` release included a CSP member-assignment fix, and `3.16.x`
changed structural/morph/model behavior. Hedron therefore
does not infer grammar from prose alone.

Stage 0 generates and runs an exact grammar corpus against the vendored artifact in Chromium,
Firefox, and WebKit. It covers literals, nested access, assignment/update, model assignment,
methods/getters, arrays, iteration, async, magics, plugin expressions, errors, globals, template
literals, arrow functions, destructuring, spread, and HTML injection. The resulting grammar—not
the normal Alpine grammar—is frozen in Python/HDJ validation and completion.

Complex logic moves into a registered `Alpine.data()` module with a small named expression surface.
Hedron never solves CSP limitations by enabling `unsafe-eval` or silently switching builds.

## HTMX coexistence contract

Alpine and HTMX operate on the same DOM, so taking full advantage requires lifecycle coordination,
not merely loading both scripts.

| Event/path | Required behavior |
|---|---|
| initial page | Register all demanded modules/plugins, start Alpine once, then expose initialized facts. |
| `htmx:beforeRequest` / response | Project pending/error/success into the owning interaction state without treating browser state as server proof. |
| `htmx:beforeCleanupElement` | Run Alpine/module cleanup exactly once before removal; release traps, observers, anchors, listeners, timers, and portal ownership. |
| normal inner/outer/delete swap | New roots initialize once; retained ancestors are not double-started; removed roots cannot keep effects. |
| `htmx:afterSwap` / `htmx:afterSettle` / `htmx:load` | Reconcile state, process generated roots/content, restore declared focus/announcement, and finalize trace facts in a fixed order. |
| OOB swaps | Apply the same lifecycle to every target and reject conflicting ownership/state-transfer declarations. |
| `x-if` creates `hx-*` content | Call `htmx.process()` once after insertion; the official HTMX docs explicitly require processing dynamically created HTMX markup. |
| Alpine creates/removes local DOM | Never invent server route/target authority; cleanup remains tied to the element root. |
| history save/restore | Strip or serialize only declared disposable projections before snapshot; reinitialize/reconcile on restore without replaying mutations. |
| `hx-preserve` | Preserve only explicitly compatible stable-ID islands; upstream notes limitations for inputs, caret, iframes, and some video. |
| morph swap | Use the one selected Alpine-aware morph path, stable logical keys, lifecycle hooks, and explicit reset/retain/version-transfer policy. |
| late response | App, target, operation generation, binding, and revision must still match; stale responses never overwrite newer local presentation. |

These rows are observable public outcomes. The implementation may use Alpine's documented DOM
observation, lifecycle events, directive `cleanup()`, and HTMX events/APIs, but cannot freeze a
dependency on undocumented `initTree`/`destroyTree`-style internals. The lifecycle probe must prove
that automatic observation plus Hedron coordination does not initialize or clean a root twice.

HTMX emits camelCase and kebab-case event names because Alpine attribute names require lowercase;
Hedron normalizes one canonical event identity in authoring and tracing.

## State ownership

| Alpine state | Allowed lifetime | Examples | Not allowed |
|---|---|---|---|
| element/component local | element or swap generation | open tab, menu visibility, draft local filter, measured geometry | credentials, permissions, authoritative validation |
| document store | current document | overlay stack, local announcement coordination, presentation density | untyped global session/domain store |
| persisted preference | explicit bounded browser lifetime | dismissed hint, density, admitted color preference | secrets, tenancy, cart/order/job truth, sensitive form data |
| form mirror | one visible form | mask display, character count, local reveal state | bypassing Pydantic/server parse and errors |
| operation presentation | one request generation | pending, disabled, optimistic appearance | proof of commit, idempotency, transaction outcome |
| domain projection | read-only rendered facts | filtering already authorized rows | client-owned writes or authorization |

Each root declares its state schema, owner, sensitivity, reset policy, and HTMX reconcile behavior:
`reset`, `retain-if-same-identity`, or `transfer-if-schema-version-matches`.

## Failure and no-JavaScript behavior

The semantic state is usable before enhancement and remains usable when JavaScript is disabled,
Alpine/core/plugin assets return 404, integrity verification fails, CSP refuses execution, a plugin
throws during registration, or initialization is slow. No essential content or sole control is
permanently hidden by `x-cloak`. Recipes activate enhanced hiding/rearrangement only under an
initialized-root marker and expose bounded diagnostics without leaking application data. Partial
runtime failure never changes server authorization, form parsing, navigation, or HTMX authority.

## 0.67 versus 1.0

### 0.67

- ships the exact CSP runtime, normalized directive/magic/plugin model, registered modules, typed
  recipes, lifecycle coordinator, diagnostics, and complete capability inventory;
- exposes the frozen discriminated `Interaction` for local/request/combined effects and role-indexed
  `Outcome` values;
- ships Alpine-backed canonical versions of all Required Hedron-owned local widgets while retaining
  old common-widget controllers/elements only as warned compatibility paths;
- retains the public Web Component ABI, reviewed specialist elements, and third-party authoring;
  records evidence-backed promotion or non-admission for each specialist candidate;
- keeps direct typed Alpine authoring as an Advanced escape hatch;
- proves all plugin and modifier dispositions independently; and
- carries visible structured warnings for any transitional spelling not entering 1.0.

### 1.0

- makes `Interaction` the only canonical control/event/request declaration;
- makes Alpine the sole enhanced browser-local behavior engine for Hedron-owned common widgets;
- removes overlapping delegated controllers, per-widget scripts, and common-widget custom elements
  after 0.67 warnings, while retaining semantic/native fallbacks and separately owned specialist
  Web Component and third-party hosts;
- removes duplicate HTMX-only, Alpine-only, raw-attribute, script/module, and browser-activation
  beginner paths after 0.67 warnings;
- preserves the full admitted Alpine capability set behind the canonical model rather than removing
  features merely to make the facade smaller; and
- retains one clearly Advanced direct Alpine lane for capabilities the typed model cannot express,
  with explicit trust, asset, lifecycle, and state ownership.

## Required deep-dive probes

1. Exact CSP grammar across every directive, magic, plugin expression, and three browsers.
2. Plugin compatibility with `@alpinejs/csp`, including dynamic Mask and complex Sort handlers.
3. Nested data shadowing, stores, modelable controls, refs/IDs, teleport event forwarding, and
   async behavior through inner/outer/OOB/delete/history swaps.
4. Mutation-observer initialization versus explicit HTMX hooks, proving no double init or leaks.
5. `x-if` plus `htmx.process()` for nested/new roots and repeated toggle cycles.
6. Normal swap, `hx-preserve`, Alpine Morph, and any HTMX alpine-morph candidate with input/caret,
   focus, media, nested roots, Web Components, OOB, history, and revisioned state.
7. Cleanup counters for effects, watchers, window/document listeners, focus traps, Intersection and
   Resize observers, Floating UI anchors, timers, Sort instances, stores, and teleports.
8. CSP/XSS probes for expressions, globals, `x-html`, `TrustedHtml`, bound URLs/styles/classes,
   persisted values, custom events, plugin inputs, and server-returned markup.
9. Keyboard, focus, AT, zoom/reflow, RTL, forced colors, reduced motion, coarse pointer, and
   no-JavaScript evidence for every recipe/plugin claim.
10. Feature-off, core-only, per-plugin, combined-plugin, initial scan, swap, observer, memory, and
    raw/gzip/request performance budgets.
11. Initial-page plus reachable-fragment feature closure, dynamic fragment subset/fingerprint
    failure, and proof that no response-time plugin/module registration occurs.
12. JavaScript-disabled, 404, integrity, CSP-refusal, slow-start, and partial-plugin failure with no
    essential cloaked content or loss of ordinary form/link/server behavior.

## Acceptance result

0.67 cannot claim complete Alpine integration until the machine-readable inventory has no omitted
upstream row, every admitted row has an executable fixture, every excluded/experimental row has a
named reason, and the selected CSP/HTMX lifecycle model passes. Hedron 1.0 cannot remove an admitted
Alpine capability merely to simplify the interface; it simplifies the authoring paths while
preserving the capability depth established in 0.67.
