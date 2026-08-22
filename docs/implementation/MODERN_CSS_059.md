# Modern CSS platform implementation plan (phase 0.59)

**Status:** Stage 1 entry packet locked; runtime work and release evidence are in progress.
**Authority:** RFC-0087 / D-106 / D-107 / `docs/acceptance/RELEASE_0_59.md` /
`docs/acceptance/modern-css-contract-059.toml`.
**Execution sequence:** [`EXECUTION_0_59.md`](EXECUTION_0_59.md).
**Baseline:** in-tree `v0.58.1`; public upgrade source `v0.58.0`.
**Target:** `v0.59.0`.

## Delivery strategy

The overhaul is an in-place evolution with one vertical integration branch at a time. Compiler,
cascade, token, component, and evidence changes land behind compatibility fixtures; no long-lived
second stylesheet/compiler path is introduced. Each workstream closes only when its fallback and
upgrade evidence lands with the implementation.

Stage 1 uses seven milestones:

| Milestone | Workstreams | Exit |
|---|---|---|
| M0 — refine | W0 | Exact contracts, probes, issue mirrors, browser floors, schemas, and budgets accepted |
| M1 — compile | W1 | Compiler v2 handles the locked corpus, reads v1, and passes security/determinism checks |
| M2 — foundation | W2–W3 | One generated default asset, canonical cascade/tokens, variants, color, and typography |
| M3 — responsive | W4 | Container/intrinsic/logical layout and media-independent fallbacks pass three engines |
| M4 — surfaces | W5–W8 | Overlay/motion plus all four consumer vertical slices pass component/browser evidence |
| M5 — authoring | W9–W11 | Safe contextual styling, print/a11y/media, tools, migration, Explorer, and docs complete |
| M6 — cut | W12 | Fleet, consumer migration, budgets, regression, packaging, issue refresh, and release rehearsal pass |

M2 work can parallelize after the compiler output contract is stable. W6 controls can proceed with
W2; W7 shell and W8 workflow consume W3/W4 foundations. W9 remains blocked on the explicitness
prototype. M6 never waives unfinished earlier gates.

## W0 — contracts, probes, and issue mirrors

Deliverables:

- accept the contract-refine decision and update RFC-0087 resolved questions;
- lock exact public signatures/values/markers for container context, variants, safe control
  attributes, control size/width, shell slots, pipeline presentation, overlay placement, and any
  field/layout/scope-default recipe additions;
- choose and license-audit the parser/tokenizer implementation, including pure-Python install and
  optional-native parity decisions;
- pin reproducible Playwright Chromium/Firefox/WebKit versions and probe each inventory feature;
- freeze compiler/manifest/source-map/design palette schema v2 and v1 read/hash behavior;
- freeze diagnostic IDs, package dispositions, benchmark hardware/method, and visual matrix;
- file the Hedron umbrella/workstream issues and backlink
  user-token-management-app #4, #5, #6, and #7; and
- refresh all open issue queries and update `modern-css-tracking-059.toml`.

No runtime symbols, package versions, default CSS behavior, or issue state changes occur in W0
except filing/linking the explicitly required tracking mirrors.

## W1 — standards-capable scoped compiler

Implement the token/grammar pipeline in small verified layers:

1. tokenize with source spans while preserving comments/strings/escapes and legal unknown syntax;
2. classify rules, nested rules, declarations, descriptors, functions, URLs, and custom identifiers;
3. discover only local symbols in valid grammar positions;
4. rewrite nested selector class symbols and accepted custom identifiers structurally;
5. parse animation shorthand/name references and any accepted anchor/transition/property names;
6. resolve bounded local imports before scoping and validate every asset-bearing token;
7. normalize compiler-owned/authored layers and legal top-level ordering;
8. emit deterministic CSS, v2 manifest, source map, capability report, and redacted diagnostics;
9. read v1 manifests and preserve symbol hashing by default; and
10. fuzz malformed input, recursion, imports, URL traversal/schemes, escapes, and resource budgets.

Required regression seeds include quoted `.css` imports, authored `@layer components`, nested
functional selectors, modern at-rules/functions, animation shorthands, comments/strings/URLs, and
unknown safe at-rules.

## W2 — cascade and default stylesheet generation

- split `hedron-default.css` source by reset/tokens/base/component-family/utility concern;
- generate one deterministic public asset from an explicit source manifest;
- retain public layer order and application overrides;
- collapse the authored owning layer and define deterministic sublayer names;
- audit selector specificity and use `:where()` only where zero specificity is intentional;
- replace repeated viewport matrices with generated/deduplicated selectors;
- inventory every public class, marker, token, part, and package consumer;
- preserve `default_styles=False` and strict-CSP external delivery; and
- add raw/gzip/request budgets to the build and release evidence.

Do not hand-edit generated output. Source modules and the generation manifest are reviewed; the
final asset and digest are reproducible artifacts.

## W3 — tokens, variants, color, and typography

- select one canonical semantic token namespace and emit 0.58 public aliases;
- make `Theme.variants` explicit, finite, emitted, nestable, explainable, and additive;
- implement absolute CSS Color 4 parsing/normalization, sRGB fallback, optional wide-gamut output,
  deterministic gamut mapping, contrast/focus checks, and `hedron.brand-palette/2` provenance;
- add bounded prefixed `@property` registration only where interpolation evidence justifies it;
- retain existing explicit/system light/dark precedence while optionally emitting `light-dark()`;
- define finite typography roles for fluid type, balance/pretty wrap, hyphenation, code, numbers,
  and long/international content; and
- support explicit local static/variable fonts with license/asset/preload/metric-fallback evidence.

Remote font fetches and context-dependent color seeds remain outside the Supported path.

## W4 — container-aware, intrinsic, and logical layout

- evolve existing Container rather than adding a parallel layout root;
- add opt-in viewport/container context to existing responsive built-ins while preserving viewport
  defaults;
- lock semantic container thresholds and nested/named behavior;
- use subgrid only with ordinary Grid/FormGrid fallbacks;
- apply intrinsic sizing, modern viewport units, safe areas, and aspect ratio through finite intent;
- convert remaining directional layout to logical properties or document physical exceptions;
- cover LTR, RTL, mixed direction, vertical writing, narrow/zoom/text-spacing, and long/unbroken
  content; and
- prove query feature-off, fragment replacement, containment, overflow, focus, and complete-content
  behavior.

## W5 — overlays and motion

- retain native dialog/popover/top-layer semantics and details/static fallbacks;
- add finite logical placement and collision strategies to applicable existing surfaces;
- enhance with anchor positioning only behind feature detection;
- add bounded starting/discrete/view transitions under existing motion presets;
- preserve canonical navigation, HTMX swap, focus, title/history, and server state;
- remove nonessential motion under reduced-motion preference; and
- keep scroll-driven animations opt-in Experimental, decorative, and absent from semantic states.

## W6 — controls (consumer issues #4 and #5)

Build one shared typed-control contract:

- validate and forward applicable global, ARIA, data, approved HTMX, and Hedron dialog-trigger
  attributes to the correct Button/LinkButton native element;
- reject `on*`, inline `style`, unsafe URLs, malformed ARIA, and non-allowlisted HTMX sinks/values;
- align Button and LinkButton size/width vocabulary and markers;
- provide complete small/compact and full-width default CSS;
- align line-height, padding, icon, focus, disabled, hover/no-hover, and responsive states; and
- migrate the Data Mover call sites and remove the issue-identified workarounds.

Tests include rendering, typing, security, CSP, keyboard, visual, and compatibility facts.

## W7 — AppShell chrome (consumer issue #6)

Evolve existing AppShell/Brand/AccountSummary/AppFooter/banner/navigation primitives with:

- typed brand mark, product name, subtitle, and home-link composition;
- account identity plus an ordinary form/action slot suitable for sign-out;
- footer content without nested landmark elements;
- shared authenticated and login/register shell composition;
- canonical theme/recipe tokens for banner, navigation, account, footer, and responsive states; and
- container-aware behavior with viewport/static fallback.

The source fixture preserves its current forms, CSRF, routes, accessible names, and auth boundary.

## W8 — pipeline and operational presentation (consumer issue #7)

Compose existing ProcessFlow, FlowStep, Status, DescriptionList, Table, Card, and layout authorities
into provider-neutral presentation for:

- source/destination connector nodes with icon/identity, metadata, and state slots;
- responsive horizontal/vertical connectors;
- ready, blocked, running, succeeded, and failed states with non-color cues;
- optional progress/connector motion plus reduced/absent equivalent;
- run status and log surfaces; and
- compact operational history.

Hedron does not own transfer execution, provider integrations, polling/jobs, logs, authorization,
or domain transitions. State is explicit input and presentation only.

## W9 — contextual styling and recipe feasibility

Prototype explicit authored-value tracking without changing 0.58 constructor signatures or
behavior. Field/layout recipe defaults may fill only genuinely unset eligible presentation fields.

Prototype a serializable scoped-default object that targets public semantic roles and emits only
tokens/markers. `style explain` must enumerate every affected role and winning source before render.
The scope cannot mutate component instances, add hidden wrappers, change behavior/semantics/state,
hide content, or target private selectors.

If either prototype fails these invariants, remove that capability from the Required phase scope
through the contract-refine/amendment process and record a destination. Do not weaken precedence to
make the API ship.

## W10 — print, media, internationalization, and accessibility

- implement and render-verify a real print stylesheet;
- cover forced colors, reduced motion, contrast, transparency, pointer, hover, and no-script paths;
- test keyboard, focus visibility/obscuration, announcements, target/reflow, zoom, text spacing,
  truncation/full content, and fragment swaps;
- cross all relevant fixtures with LTR/RTL/mixed/vertical writing and international/unbroken data;
- force every Progressive feature on and off; and
- keep human AT claims bounded by open Hedron #86 / the 0.21 evidence ledger.

## W11 — inspection, migration, and learning path

- extend style explain/check/preview/diff/eject with compiler spans, capability tier, active
  container, variant, layer/specificity, fallback, alias, asset, and budget provenance;
- add equivalent read-only Explorer inspection without application data or callback execution;
- provide reviewable no-overwrite codemods for canonical token names and accepted API changes;
- migrate maintained starter/theming/component-CSS docs to the highest applicable 0.59 abstraction;
- teach built-in → brand → intent → recipe/scope → container → inspect → CSS → eject; and
- label Experimental/Deferred syntax and primitive-level material clearly.

## W12 — fleet integration and release

- assign and verify every first-party package styling disposition;
- expand the zero-application-CSS gallery with controls, shell, container layout, overlays, print,
  international content, and pipeline operations;
- validate the Data Mover migration and close source issues only after evidence passes;
- run compiler/cascade/token/visual/a11y/security/performance/upgrade/full-suite gates;
- build clean wheels without a consumer Node requirement and verify lazy optional assets;
- refresh open issues and own/exclude any new relevant styling enhancement with rationale; and
- rehearse release metadata, docs, compatibility notes, rollback, and registry truth.

## Definition of done

All 23 rows in `release-gate-0.59.toml` are Verified with zero Deferred. The compiler and default
asset are singular and deterministic; public 0.58 contracts pass both upgrade sources; every
Progressive feature has an independently passing fallback; all four consumer issues close from a
validated source migration; size/performance/security/accessibility/package evidence passes; and
the release makes no unsupported human-AT, browser, CSS-spec-completeness, or 1.0 claim.
