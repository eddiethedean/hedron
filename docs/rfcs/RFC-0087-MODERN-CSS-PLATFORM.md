# RFC-0087: Modern CSS platform and intuitive built-in styling

**Status:** Accepted; Stage 0 contract refined by D-107 (Stage 1 implementation blocked)
**Phase:** 0.59
**Planning baseline:** Published/Verified in-tree `v0.58.1`
**Published upgrade source:** PyPI `v0.58.0`
**Target:** `v0.59.0`

**Contract lock:** [`modern-css-contract-059.toml`](../acceptance/modern-css-contract-059.toml)

**Revision:** 2026-08-22 — D-107 freezes the additive API vocabulary, compiler and diagnostic
schemas, browser revisions, budgets, package dispositions, and issue-mirror IDs. No runtime or
version change occurs during the refine.

## Summary

Phase 0.59 modernizes Hedron's complete styling path: the default stylesheet, themes and design
systems, semantic appearance APIs, responsive layout, component-scoped CSS compiler, cascade and
asset build, browser fallbacks, diagnostics, examples, and visual evidence. The outcome is a
styling system that covers common product UI without application CSS while letting advanced users
author modern standards-based CSS directly in component `styles.css` files.

The phase keeps one styling authority. Existing `Theme`, `DesignSystem`, semantic component props,
`StyleRecipe`, `StyleScope`, stable `data-hedron-*` markers, style contracts, `StyleSymbols`, the
scoped CSS compiler, cascade layers, and the asset build are evolved in place. There is no second
theme registry, CSS runtime, CSS-in-Python property language, client-side style injector, or
mandatory Node toolchain.

This is not a revival of RFC-0086. D-105 correctly integrated that proposal's brand, recipe, scope,
inspection, and ejection work into 0.58. D-106 supersedes only D-105's future-scheduling statement
that no distinct 0.59 phase would exist; RFC-0087 owns a new standards-platform and fleet-overhaul
scope on top of the shipped 0.58 contracts.

## Motivation and background

Hedron 0.57 and 0.58 established a strong presentation foundation:

- semantic tokens and coordinated light/dark themes;
- finite appearance, density, spacing, layout, overflow, and responsive markers;
- cascade layers, logical properties, Flexbox/Grid, custom properties, `minmax()`, `clamp()`,
  `color-mix()`, `:is()`, `:where()`, and `:has()`;
- native dialog and popover use, strict-CSP external styles, reduced-motion and forced-color rules;
- component-scoped CSS with generated symbols and local-asset validation;
- `DesignSystem`, five recipe families, explicit theme/mode/density scopes, and inspect/diff/check/
  preview/eject tooling; and
- three-engine, light/dark, forced-colors, reduced-motion, print, direction, zoom, text-spacing, and
  long-content evidence contracts.

The implementation is nevertheless uneven. At the `v0.58.1` baseline,
`hedron-default.css` is 3,165 lines, 85,136 raw bytes, and 11,851 gzip bytes. A lexical inventory
finds 228 Hedron class identifiers, 47 `data-hedron-*` identifiers, and 49 Hedron custom-property
identifiers. The size is manageable, but repeated viewport-selector matrices and mixed token
namespaces make extension harder than necessary.

The scoped compiler uses a focused parser plus regular-expression symbol rewriting. It handles the
current authored subset, but it cannot claim standards-complete handling of modern selector and
value grammars. Baseline probes demonstrate why the boundary must be tightened: modern nested
rules and at-rules can be preserved without being semantically understood; a quoted
`@import "theme.css"` can make `css` appear as a class symbol; and an authored
`@layer components` can be wrapped into an unintended `components.components` layer. Animation
shorthand rewriting is token-by-whitespace rather than grammar-aware.

The default system also lacks a first-party container-query contract, subgrid alignment, anchor
positioning, typed custom-property registration, modern absolute-color input, a real print
stylesheet, and an explicit writing-mode/RTL architecture. `Theme.variants` is stored and
registered but not emitted by `emit_theme_css`. Most responsive built-ins are driven by viewport
breakpoints even when their behavior should depend on component width.

Finally, a real consumer application has four open Hedron enhancement requests that expose the
practical edge of the current system:

- [user-token-management-app #4](https://github.com/eddiethedean/user-token-management-app/issues/4)
  — safe global, `aria-*`, `data-*`, approved `hx-*`, and dialog-trigger attributes on typed
  `Button` and `LinkButton`;
- [#5](https://github.com/eddiethedean/user-token-management-app/issues/5) — complete and
  consistent Button/LinkButton size and width styling;
- [#6](https://github.com/eddiethedean/user-token-management-app/issues/6) — composable branded,
  account, footer, authenticated, and unauthenticated AppShell chrome; and
- [#7](https://github.com/eddiethedean/user-token-management-app/issues/7) — provider-neutral
  pipeline nodes/connectors, operational states, reduced-motion-aware progress, logs, and compact
  run history.

These are phase inputs and release fixtures, not incidental links.

## Design principles

1. **Common UI should need no application CSS.** Product-specific art direction remains an escape
   hatch, not a prerequisite for compact controls, responsive shell chrome, forms, data surfaces,
   workflows, or overlays.
2. **Use CSS as the advanced language.** Python exposes finite semantic intent; component
   `styles.css` exposes standards-based CSS. Hedron does not mirror CSS properties in Python.
3. **One source of truth.** Themes produce tokens, components produce public markers, the compiler
   scopes application/component CSS, and one cascade/asset build combines them.
4. **Progressive enhancement is explicit.** Required behavior has a tested baseline. Newer visual
   capabilities use `@supports` and usable static fallbacks, never user-agent sniffing.
5. **Presentation cannot acquire behavior authority.** Styling never changes route, effect,
   authorization, state, DOM reading order, accessible name, form ownership, or destructive
   meaning.
6. **Safe defaults, inspectable exceptions.** Finite values are easy to discover; every generated
   token, marker, recipe, fallback, and compatibility alias is explainable and ejectable.
7. **Modernization must reduce accidental complexity.** New features do not justify another
   runtime, a mandatory bundler, a larger specificity contest, or unbounded stylesheet growth.

## Proposed design

### Capability tiers

Every CSS capability receives one machine-readable disposition in
`modern-css-inventory-059.toml`:

- **Required:** part of the Supported 0.59 path and tested in the pinned Chromium, Firefox, and
  WebKit floors.
- **Progressive:** an enhancement behind feature detection; its fallback must independently pass
  semantic, keyboard, layout, and content-access checks in all Supported engines.
- **Experimental:** opt-in and honestly labeled; excluded from unqualified Supported claims.
- **Deferred:** deliberately outside 0.59 with a reason and destination.

Support is evidence-based. A syntax being standardized, parsed, or present in one browser is not
enough to promote it. Conversely, Hedron need not wait for universal native support when a small,
static, non-divergent fallback is available.

### Modern CSS cross-analysis

| Capability | 0.58 position | 0.59 disposition | Hedron-facing result |
|---|---|---|---|
| Cascade layers and low-specificity selectors | Shipped | Required, normalized | One documented layer order; generated selectors use `:where()` where safe; authored sublayers cannot double-nest the compiler layer |
| Native CSS nesting | Preserved in probes, not guaranteed | Required authoring | Nested selectors are parsed and scoped correctly, with source locations and deterministic output |
| `@supports`, modern media queries, and unknown future at-rules | Structurally preserved | Required preservation contract | Safe syntax is retained byte-semantically where no rewrite is needed; unsupported dangerous constructs reject clearly |
| `@scope` | No first-party contract | Progressive | Built-in specificity containment and advanced component authoring with a compiled selector fallback where required |
| Size/style container queries and container units | No public contract | Required size-query path; style queries Progressive | `Container` can establish an explicit query boundary; Grid/FormGrid/shell/workflow adaptations can respond to component width |
| Grid `subgrid` | Not used | Progressive with ordinary Grid fallback | Form labels, metadata, cards, and data rows align across nested structures without changing DOM order |
| Logical properties and writing modes | Partially shipped | Required fleet-wide | LTR, RTL, and selected vertical-writing fixtures share one logical layout contract |
| Intrinsic sizing, `min()`/`max()`/`clamp()`, modern viewport units, aspect ratio | Partially shipped | Required finite recipes | Safer narrow-screen, shell, media, and split-panel sizing without arbitrary Python CSS lengths |
| `:is()`, `:where()`, `:not()`, `:has()` | Shipped selectively | Required compiler/fleet contract | Predictable specificity and parent-state styling without behavior state moving into CSS |
| `color-mix()` and wide-gamut/OKLCH colors | `color-mix()` used; brand input hex-only | Required sRGB fallback; Progressive wide gamut | Absolute modern color input is parsed and normalized; generated themes disclose gamut mapping and contrast adjustments |
| `light-dark()` and `color-scheme` | Explicit mode selectors | Progressive emission, Required semantics | Native controls and tokens follow explicit/system mode without replacing the existing explicit override precedence |
| `@property` | Not used | Progressive and prefix-bounded | Selected animatable Hedron tokens gain typed registration; unregistered custom-property fallbacks remain authoritative |
| Modern text wrapping, hyphenation, font metrics, variable fonts | Partial | Required finite typography roles | Better headings, prose, code, international text, and locally hosted variable fonts without remote fetches |
| Popover/top layer | Shipped | Required foundation | Existing native popover/dialog semantics remain canonical across shell, menu, help, and workflow surfaces |
| CSS anchor positioning and position fallbacks | Not used | Progressive | Logical popover/menu placement with tested non-anchor static placement |
| `@starting-style` and discrete transitions | Not used | Progressive | Entry/exit polish without a JS animation runtime; reduced motion resolves to immediate stable states |
| View Transitions | Narrow navigation enhancement exists | Progressive, opt-in | Stable logical transition names for declared page/HTMX surfaces; ordinary navigation/swap remains canonical |
| Scroll-driven animation | No contract | Experimental, decorative only | Optional demos may enhance progress/storytelling; timelines never represent authoritative task state |
| User-preference media (`forced-colors`, reduced motion, contrast, transparency) | First two partly shipped | Required fallback matrix; newer preferences Progressive | Non-color/non-motion state, visible focus, and usable surfaces across preference modes |
| Print | Matrix named but no default `@media print` rules | Required | Navigation/interactive chrome is handled deliberately; content, links, tables, statuses, and disclosures print legibly |
| Content containment / `content-visibility` | No contract | Progressive and narrowly benchmarked | Large static galleries/lists may skip off-screen paint only when find-in-page, print, focus, and AT behavior remain intact |
| CSS masonry, customizable native select, Paint/Layout Worklets | No contract | Deferred | No production dependency on unstable/interoperability-poor layout or worklet platforms in 0.59 |

The normative feature rows and fallbacks live in `modern-css-inventory-059.toml`. Relevant primary
specifications include CSS Cascade 5, CSS Nesting 1, CSS Containment 3, Grid 2, CSS Color 5,
Properties and Values API 1, CSS Anchor Positioning 1, CSS Transitions 2, View Transitions 1,
Scroll-driven Animations 1, CSS Logical Properties 1, and Media Queries 5.

Primary standards references:

- [CSS Cascading and Inheritance Level 5](https://www.w3.org/TR/css-cascade-5/)
- [CSS Nesting Module Level 1](https://www.w3.org/TR/css-nesting-1/)
- [CSS Containment Module Level 3](https://www.w3.org/TR/css-contain-3/)
- [CSS Grid Layout Module Level 2](https://www.w3.org/TR/css-grid-2/)
- [CSS Color Module Level 5](https://www.w3.org/TR/css-color-5/)
- [CSS Properties and Values API Level 1](https://www.w3.org/TR/css-properties-values-api-1/)
- [CSS Anchor Positioning Level 1](https://www.w3.org/TR/css-anchor-position-1/)
- [CSS Transitions Level 2](https://www.w3.org/TR/css-transitions-2/)
- [CSS View Transitions Module Level 1](https://www.w3.org/TR/css-view-transitions-1/)
- [Scroll-driven Animations](https://www.w3.org/TR/scroll-animations-1/)
- [CSS Logical Properties and Values Level 1](https://www.w3.org/TR/css-logical-1/)
- [Media Queries Level 5](https://www.w3.org/TR/mediaqueries-5/)

### One intuitive authoring ladder

The documentation and tooling teach one progression:

1. **Built-in styling:** use semantic components with no application CSS.
2. **Brand:** pass a built-in `Theme` or compile a `DesignSystem.brand`.
3. **Intent:** select finite component appearance, size, density, layout, responsive, placement, and
   typography values.
4. **Reuse:** apply a named `StyleRecipe` or an explicit `StyleScope` variant/default set.
5. **Adapt:** opt a region into container-aware layout rather than adding app breakpoints.
6. **Inspect:** use `style explain`, preview, diff, check, and Explorer computed-token/cascade views.
7. **Extend:** author ordinary modern CSS in a component `styles.css`, bound through
   `StyleSymbols` and public parts/tokens.
8. **Own:** safely eject a whole design, group, recipe, component, or generated surface into public
   Hedron APIs and standards-based CSS.

No step invalidates the prior step, and no beginner feature silently opts an application into the
advanced compiler.

### Standards-capable scoped CSS compiler

The compiler is upgraded by behavior, not by implementation brand. The Stage 0 refine must select
a parser/tokenizer path that preserves the pure-Python Supported install and does not require Node
in consuming applications. An optional native accelerator may exist only with pure-Python parity.

The new compiler must:

- distinguish selector, declaration, descriptor, string, comment, URL, custom-property, and
  at-rule grammar contexts before discovery or rewriting;
- scope classes inside nested selectors and functional pseudo-classes, including `&`, `:is()`,
  `:where()`, `:not()`, and `:has()`, without touching strings, URLs, comments, decimals, file
  extensions, or at-rule descriptors;
- parse animation shorthand/name references rather than replacing whitespace-delimited words;
- define handling for locally scoped custom identifiers such as keyframes and any accepted
  `@property`, counter-style, view-transition, or anchor names;
- preserve or correctly transform nesting, `@media`, `@supports`, `@container`, `@scope`,
  `@starting-style`, keyframes, font descriptors, and future unknown at-rules that do not require a
  semantic rewrite;
- resolve quoted and `url()` local `@import` forms at build time under registered roots, with
  cycle/depth/byte budgets, or reject them diagnostically; remote imports remain outside the
  Supported strict-CSP path;
- keep compiler-owned layer placement distinct from authored sublayers, collapse an authored copy
  of the owning layer, and preserve legal top-level ordering for charset/import/layer statements;
- validate every nested URL-bearing token, including font and image descriptors, against the same
  asset/root/remote policy;
- produce line/column diagnostics, a deterministic v2 compilation manifest, source maps, and a
  semantic compatibility report; and
- retain v1 manifest consumption and symbol-hash compatibility for the migration window unless a
  separately recorded collision/security reason requires a change.

The compiler remains build-time in production. Runtime compilation stays prohibited by the
existing compile gate.

### Cascade and default stylesheet architecture

The public layer order remains `reset, tokens, base, components, utilities, overrides`. Phase 0.59
splits the source into maintainable modules but emits one deterministic default asset so ordinary
pages do not pay more stylesheet requests. Optional Experimental enhancement CSS may be a separate
demand-driven asset; Required and Progressive fallbacks remain in the default build.

Rules follow these constraints:

- semantic markers and documented public parts/tokens are the only cross-package selector ABI;
- source order is generated from a manifest rather than filesystem accident;
- selectors have a documented specificity ceiling, with `:where()` used where zero specificity is
  intended and `:is()` retained where specificity is meaningful;
- component state uses native attributes/ARIA/public markers, never text matching or private DOM
  position;
- viewport matrices are deduplicated, and component-level responsiveness moves to explicit
  container queries where that preserves compatibility; and
- applications retain the `overrides` layer and `default_styles=False` escape hatch.

### Tokens, themes, variants, and color

`Theme` and `DesignSystem` remain the authorities. Phase 0.59 defines one canonical semantic token
namespace and emits compatibility aliases for every public 0.58 token spelling for at least the
0.59 line. Alias use is diagnosed by tooling but does not break existing CSS.

`Theme.variants` becomes an actual finite output contract. An explicit variant marker on
`StyleScope` or a supported component surface selects a named token subset. Variants can alter
presentation tokens only; they cannot select recipes, hide content, or change component behavior.
Unknown variants reject with an actionable diagnostic.

`DesignSystem.brand` expands from 3/6-digit hex to parsed absolute CSS Color 4 inputs: hex,
`rgb()`/`rgba()`, `hsl()`/`hsla()`, `hwb()`, Lab/LCH, and OKLab/OKLCH where the Stage 0 parser proves
deterministic normalization. `var()`, `currentColor`, relative colors, URLs, system colors, and
context-dependent values are not brand seeds. Generated output always includes a tested sRGB
fallback. Wide-gamut output is additive and records conversion, clipping/gamut mapping, contrast,
and focus adjustments in `hedron.brand-palette/2`.

`@property`, `light-dark()`, relative-color syntax, and wide-gamut declarations may reduce
duplication or improve interpolation only behind fallbacks. They never replace the server-side
token validation or explicit light/dark precedence.

Remote-font convenience remains Deferred. Variable and static fonts use explicit local assets,
declared licenses, preload policy, fallback stacks, and metric-compatible fallbacks.

### Container-aware and intrinsic layout

The existing `Container`, `Grid`, `GridItem`, `FormGrid`, `Stack`, `Inline`, `SplitView`,
`MasterDetail`, `ActionGroup`, and AppShell contracts evolve rather than being replaced.

The intended ergonomic shape is:

- an explicit finite option on `Container` establishes an inline-size query boundary, with an
  optional validated name for advanced nested layouts;
- responsive built-ins can choose `viewport` or `container` as their finite adaptation context;
- existing `base`/`sm`/`md`/`lg` maps remain accepted and keep viewport semantics by default;
- container-context maps reuse named semantic thresholds locked by Stage 0, not arbitrary CSS in
  Python;
- subgrid is used for nested field/metadata/data alignment only with a normal Grid fallback; and
- dynamic viewport units, safe-area insets, intrinsic tracks, and aspect ratios are exposed through
  finite component intent, not raw declarations.

No responsive mode may reorder DOM, make authoritative content unreachable, or rely on hover,
pointer precision, color, or animation. Priority hiding retains an explicit complete-content path.

### Recipes and explicit style context

The 0.58 deferred recipe work is re-evaluated under stricter rules:

- `field` and `layout` recipe families may graduate only after Hedron can distinguish a constructor
  default from an explicitly authored value without changing 0.58 behavior;
- scope-wide defaults may graduate only as an explicit, serializable style-context object that
  targets public semantic roles, emits presentation tokens/markers, and can statically enumerate
  every affected role;
- explicit component props and named-surface replacements remain stronger than recipes/defaults;
- a context cannot mutate component objects, add wrappers beyond the explicit `StyleScope`, alter
  semantics/state/behavior, or target private selectors; and
- if the Stage 0 prototype cannot satisfy those constraints, the affected family stays Deferred
  with a named post-0.59 owner rather than shipping a surprising abstraction.

### Typography, content, media, and internationalization

Finite typography roles gain coherent fluid sizing, balanced/pretty wrapping where appropriate,
safe word breaking/hyphenation, tabular-number options, code overflow, and locally hosted variable
font support. Truncation remains opt-in and always has a complete-content path.

The default stylesheet gains an actual print contract. Print evidence covers headings, links and
URLs, tables, status, process flows, disclosures, forms, shell landmarks, page breaks, color
adjustment, and hidden interactive-only chrome. Print does not expose secrets or force collapsed
private content open.

All layout and spacing rules are audited for logical properties. The visual matrix covers LTR,
RTL, mixed-direction content, and selected vertical writing-mode fixtures. Physical directions
remain only where the underlying platform behavior is physically defined and the exception is
documented.

Preference handling includes reduced motion, forced colors, increased contrast where available,
reduced transparency where available, coarse/fine pointer, hover/no-hover, print, and no-script
fallbacks. No preference query is treated as an identity or authorization signal.

### Native overlays and motion

Existing dialog/popover/top-layer semantics remain primary. Phase 0.59 adds finite logical
placement and collision-fallback intent to Popover, context menus, help, and applicable shell/
workflow surfaces. CSS anchor positioning is an enhancement; fallback placement is usable without
it and cannot cover or detach the trigger from keyboard order.

`@starting-style`, discrete transitions, and view transitions add polish only when explicitly
enabled by a component/design motion preset. Reduced motion removes nonessential animation and
retains an immediate final state. HTMX/full-page navigation, focus restoration, title/history, and
server state remain authoritative.

Scroll-driven animation is Experimental, decorative, and excluded from task progress, validation,
loading, destructive action, or other semantic state. There is no general animation timeline DSL.

### Consumer vertical slices

The four open `user-token-management-app` issues are owned as complete vertical slices:

1. **Safe typed-control attributes (#4):** Button and LinkButton share a validated safe-attribute
   contract for applicable global, ARIA, data, approved HTMX, and Hedron dialog-trigger attributes.
   Event handlers, inline style, unsafe URLs, invalid ARIA, and unknown security-sensitive sinks
   reject. The actual native element receives the accepted attributes.
2. **Control sizing and width (#5):** Button and LinkButton share documented size/width semantics,
   including small/compact and full-width behavior, line-height, padding, focus, disabled, icon,
   and responsive states. The Data Mover selectors become unnecessary.
3. **Composable shell chrome (#6):** existing Brand, AccountSummary, AppFooter, banner, navigation,
   and AppShell seams gain typed mark/name/subtitle/home, account-action/form, and footer-content
   composition across authenticated and unauthenticated surfaces without nested landmarks.
4. **Pipeline and operational presentation (#7):** provider-neutral source/destination connector
   nodes, responsive horizontal/vertical connectors, ready/blocked/running/succeeded/failed states,
   reduced-motion-aware progress, run status/log, and compact history compose existing
   ProcessFlow, FlowStep, Status, DescriptionList, Table, Card, and layout authorities rather than
   creating a workflow runtime.

Each slice must be demonstrated by a locked Hedron fixture and by the source application's current
use case. The phase does not copy Data Mover branding, provider policy, transfer execution, logs,
or domain state into Hedron.

### Inspection and developer experience

Existing style tooling is extended rather than renamed:

- `style explain` shows winning token/recipe/scope/container/layer/fallback provenance;
- `style check` validates compiler syntax, feature tiers, token aliases, contrast, style contracts,
  URL/CSP policy, container use, unsupported no-fallback features, and stylesheet budgets;
- preview renders the versioned whole-fleet gallery in all required media/direction/content modes;
- diff reports semantic token, selector ABI, layer, fallback, computed-style, and asset changes, not
  only text diffs;
- Explorer exposes public computed tokens, layer/specificity provenance, active container,
  resolved variant, and fallback/enhancement state without leaking application data; and
- ejection emits public semantic CSS with source maps and never private generated selectors.

Diagnostics include source path, line, column, rule/property context, capability disposition,
fallback requirement, and remediation. Static tooling never executes routes, callbacks, loaders,
or application data.

### Fleet adoption

Every first-party package receives an explicit styling disposition. Core, elements, charts, maps,
data, extras, Jinja, Explorer, sample-kit, notebook, sim, workbench, Flask, and Django fixtures must
either consume canonical tokens/public markers or record why styling is not applicable. Package
CSS cannot privately fork theme token names or layer order.

The zero-application-CSS gallery expands to include compact actions, container-aware forms/data,
authenticated/unauthenticated shell composition, overlays, long/international content, and the
pipeline/operational slice. Advanced examples then show component `styles.css`, not a second
framework styling API.

### Issue inventory and governance

A live audit on 2026-08-22 found two open issues in the Hedron repository: #86 (outstanding human
assistive-technology sessions) and #192 (an unrelated chart redaction bug). Neither is an open
styling enhancement. Therefore the Hedron-local open styling-enhancement set is honestly empty at
planning time.

#86 remains a cross-cutting evidence dependency: 0.59 may ship automated accessibility and browser
evidence, but it cannot claim completed human screen-reader/participant validation while `SR-021`
and companions remain Planned. #192 stays with its chart/security regression owner and is not
silently absorbed into 0.59.

The four consumer-repository issues #4–#7 above are the current open styling/presentation inputs.
Before Stage 1, maintainers must file a Hedron umbrella issue and workstream mirrors, link them in
`modern-css-tracking-059.toml`, and leave the consumer issues open until their acceptance fixtures
pass. Mirroring must not alter scope or erase the source-app validation requirement.

## Alternatives considered

### Continue with isolated selector and component patches

Rejected as the primary plan. It can close individual gaps but cannot safely fix parser semantics,
layer ordering, token aliases, container-responsive architecture, feature fallback policy, and
whole-fleet evidence as one compatible system.

### Adopt Tailwind, Bootstrap, or another design system as Hedron's built-in authority

Rejected. It would introduce another naming/cascade/version authority, weaken semantic Python
contracts, and couple Hedron defaults to an external product aesthetic. Applications remain free
to disable defaults and use those systems.

### Add a free-form CSS-in-Python or utility-string API

Rejected. It duplicates CSS with weaker tooling, expands injection/validation surface, makes CSP
and static analysis harder, and asks Python APIs to chase the CSS specification. Finite semantic
intent plus ordinary CSS is the clearer split.

### Require PostCSS/Vite/Node for modern syntax

Rejected for the Supported path. Hedron must remain consumable as a Python package without an
application Node toolchain. Maintainers may use build tooling internally only when clean wheels
contain deterministic final assets and the pure-Python component compiler remains Supported.

### Move built-ins to closed Shadow DOM

Rejected. It would break existing light-DOM composition, public selector/marker contracts, SSR and
HTMX assumptions, and application escape hatches. Public custom properties/parts may complement
the existing Web Component contract where already applicable.

### Ship only features native in every browser and avoid progressive features

Rejected. It would unnecessarily block useful modern CSS. The tier/fallback model permits
interoperable enhancement without making a feature-detection result a correctness boundary.

### Revive RFC-0086 as originally written

Rejected. Its design-system scope already shipped in 0.58. Reopening it would duplicate authority
and lose the compiler/layout/media/fleet focus that justifies a distinct 0.59 phase.

## Security implications

CSS and theme inputs are trusted build/application-author inputs, never end-user content. Even so,
the compiler and tooling must defend against accidental or malicious package CSS:

- tokenize all URL-bearing functions/descriptors and validate local roots, traversal, symlinks,
  schemes, remote policy, and missing assets;
- resolve local imports under bounded depth/count/bytes and reject cycles; remote import and font
  convenience remain outside the Supported strict-CSP path;
- reject legacy executable constructs, inline event handlers/style passthrough, unsafe global
  selectors, and unsupported at-rules whose semantics cannot be preserved safely;
- keep runtime user data out of custom properties, selectors, source maps, manifests, previews,
  diagnostics, and transition names;
- ensure safe typed-control passthrough has an allowlisted grammar and cannot smuggle `on*`,
  `style`, script URLs, refresh/navigation authority, or unvalidated HTMX sinks;
- preserve `style-src 'self'` with no `unsafe-inline` requirement and no runtime injection;
- keep build output deterministic and attest parser/compiler versions and asset digests; and
- fuzz parser, nested grammar, escapes, imports, URLs, declaration values, and manifest readers.

CSS cannot grant authorization, infer tenancy, expose routes, or make private content public.

## Accessibility implications

The overhaul must preserve semantic HTML and DOM reading order before visual testing. Required
evidence covers keyboard operation, focus visibility/obscuration, accessible names/descriptions,
native form and no-script behavior, status announcements, non-color state, target size, reflow at
320 CSS px, 200% zoom, text-spacing overrides, long/unbroken/international content, LTR/RTL,
forced colors, reduced motion, contrast preferences, print, and fragment replacement.

Container queries, subgrid, priority modes, content containment, line clamping, overlays, anchor
positioning, and transitions each require a feature-off fallback test. Visual reordering and
authoritative-content hiding remain prohibited. Motion is never the only state cue, and reduced
motion yields an immediate complete state.

Automated/browser evidence does not close #86. Human AT claims remain scoped exactly as the 0.21
ledger permits until real sessions and remediations are complete.

## Performance implications

The `v0.58.1` default CSS snapshot is the baseline: 85,136 raw bytes and 11,851 gzip bytes. The
initial 0.59 cut budgets are 90,000 raw bytes and 13,000 gzip bytes for the shipped default asset,
zero required styling JavaScript bytes, and no additional Required stylesheet request. A later
Stage 0 refine may lower these limits after generated-selector deduplication, but may not raise them
without measurements and an accepted amendment.

Representative component-CSS cold compile time may not regress beyond 1.25× the pinned 0.58.1
corpus baseline, and representative style/layout work may not regress beyond 1.10× without an
accepted benchmark-specific rationale. Measurements record hardware, browser, corpus, warm/cold
state, sample count, and variance. Pixel-paint savings alone do not justify `content-visibility` if
focus, find, print, or accessibility behavior regresses.

Default CSS source is modular, but delivery stays consolidated. Production runtime compilation and
style injection remain forbidden.

## Testing strategy

Phase evidence includes:

1. tokenizer/parser unit and property tests for strings, comments, escapes, nested selectors,
   pseudo-functions, declarations, descriptors, keyframes, custom identifiers, at-rules, malformed
   input, imports, URLs, and source locations;
2. regression probes for quoted `.css` imports, compiler-owned/authored layers, animation shorthand,
   modern functions, unknown at-rules, and v1 manifest/symbol compatibility;
3. differential compile/browser CSSOM fixtures for every Required syntax family;
4. security fuzz/adversarial corpora for global selectors, traversal, remote assets, unsafe values,
   passthrough attributes, source-map redaction, and budget exhaustion;
5. three-engine browser tests with every Progressive feature forced both on and off where the test
   harness can control it;
6. visual/computed-style/DOM facts for light, dark, forced colors, reduced motion, contrast,
   transparency, print, LTR, RTL, vertical writing, zoom, text spacing, viewport and container
   sizes, short/long/international/unbroken content, no-script, and fragment replacement;
7. accessibility tests for the base gallery and all four consumer vertical slices;
8. default CSS, compile, style/layout, asset-request, and optional-feature performance budgets;
9. fleet token/marker/layer/style-contract conformance and zero-application-CSS gallery checks;
10. upgrade fixtures from both public `v0.58.0` and in-tree `v0.58.1`; and
11. a source-app validation proving user-token-management-app #4–#7 can remove the identified
    workarounds without semantic or security regression.

Pixel snapshots never stand alone: reviewed visual deltas require DOM and computed-style facts plus
an accessibility confirmation.

## Compatibility and migration

- Existing 0.58 component signatures, default behavior, DOM order, public classes/markers/tokens,
  theme names, `default_styles=False`, style contracts, and `StyleSymbols` remain valid unless a
  specific accepted migration entry says otherwise.
- New responsive behavior remains opt-in; existing breakpoint maps keep viewport semantics.
- Token namespace consolidation emits aliases throughout 0.59. Tooling reports canonical
  replacements; removal cannot occur before a later minor with a separate decision.
- Theme variants are additive. Existing themes with stored variants gain output only when an
  explicit variant is selected.
- Compiler v2 reads v1 manifests. Existing public symbol access goes through `StyleSymbols`;
  production hash changes require explicit compatibility evidence.
- Visual refinements to built-in defaults are allowed only with reviewed before/after evidence,
  release notes, and no semantic/accessibility regression. A compatibility mode is preferred when
  a change would materially disrupt a documented 0.58 layout.
- Application CSS keeps the strongest documented override position. No automatic source rewrite
  occurs; diagnostics and optional codemods produce reviewable changes and never overwrite by
  default.
- Flask/Django/Jinja/elements/other package parity is capability-labeled; no host gains nominal API
  parity that it cannot implement safely.

The normative migration corpus is `upgrade-fixtures-059.md` and the machine-readable compatibility
lock is `modern-css-compatibility-059.toml`.

## Refined contract and remaining entry work

D-107 resolves the former open questions in the machine-readable contract lock. In particular, the
in-tree pure-Python CSS tokenizer/AST remains the implementation authority; the additive query,
variant, safe-attribute, overlay, and workflow vocabularies are finite; compiler v2 reads v1 and
preserves v1 symbol hashes by default; diagnostics and source maps carry source spans; and the
browser floor is Playwright 1.62.0 with Chromium 151.0.7922.34/revision 1234, Firefox 153.0/revision
1538, and WebKit 26.5/revision 2336. The exact values, schemas, budgets, and package dispositions
are maintained only in `modern-css-contract-059.toml`.

Stage 1 remains blocked on evidence rather than an unresolved design choice: capability probes,
the parser corpus probe, explicit-set recipe feasibility, the Hedron umbrella/workstream mirrors,
consumer backlinks, and a refreshed live issue audit. Failure of an explicitness probe removes the
affected recipe capability from Required scope through an amendment; it does not weaken the
precedence or mutation boundary.

## Acceptance criteria

Phase 0.59 may cut only when:

- D-107 and `modern-css-contract-059.toml` freeze exact APIs, schemas, diagnostics, capability
  tiers, budgets, browser floors, package dispositions, and reserved issue-mirror IDs;
- all rows in `release-gate-0.59.toml` are Verified with zero Deferred at cut;
- the modern compiler handles the locked grammar corpus, fixes the import/layer/animation probes,
  preserves v1 compatibility, and passes security fuzzing;
- the canonical cascade/token architecture and real print/RTL/media contracts are used across the
  first-party fleet;
- container-aware layout, subgrid fallback, modern color/theme variants, overlays, motion, and
  typography each pass their required feature-on/feature-off evidence;
- common built-in UI remains usable with JavaScript disabled, Progressive features absent, default
  styling enabled, and application CSS absent;
- user-token-management-app issues #4, #5, #6, and #7 satisfy their source acceptance criteria,
  have locked Hedron fixtures, and close against a validated consumer migration;
- the live Hedron and consumer issue audit is refreshed at Stage 1 entry and release cut, with new
  relevant open styling enhancements either owned or explicitly excluded with rationale;
- #86 claim limits remain honest and #192 remains under its actual owner;
- default CSS, compilation, layout/style, request, CSP, accessibility, and package budgets pass;
- public 0.58 APIs, markers, tokens, themes, scoped CSS, manifests, examples, and
  `default_styles=False` pass the upgrade corpus; and
- release docs teach the built-in → brand → intent → recipe/scope → container → inspect → CSS →
  eject ladder without presenting a second styling authority.
