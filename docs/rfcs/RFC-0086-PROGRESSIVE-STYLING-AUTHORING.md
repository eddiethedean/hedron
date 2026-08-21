# RFC-0086: Progressive styling authoring and inspectable design systems

**Status:** Accepted; conditionally Stage 0 Refined  
**Target phase:** 0.59 (`v0.59.0`)  
**Decision:** D-103  
**Stage 0 contract refine:** D-104 (early/conditional)  
**Required predecessor:** Published and Verified in-tree `v0.58.0` (not yet satisfied)  
**Planning baseline:** Published/Verified in-tree `v0.57.0` plus the D-101/D-102 0.58 contracts  
**Tracking:** `docs/acceptance/styling-tracking-059.toml`

**Revision:** 2026-08-21 — D-104 conditionally freezes the Stage 0 packet against the shipped
`v0.57.0` styling runtime and D-102's exact 0.58 contracts. Because `v0.58.0` is not implemented,
Stage 1 remains blocked until a predecessor audit confirms the final 0.58 seams or an accepted
D-104 amendment records drift. This revision adds no runtime API, package version, registry claim,
or release status.

## Summary

Phase 0.59 gives styling the same progressive-disclosure treatment that phase 0.58 gives feature
authoring. A beginner should be able to select a polished built-in look, derive a coherent and
accessible application design from a small set of brand choices, reuse named presentation recipes,
and preview the result without first learning semantic token dictionaries, CSS cascade layers,
component style contracts, scoped selectors, build manifests, or CSP rules.

The explicit styling system remains authoritative:

- `Theme`, `compile_palette`, semantic tokens, modes, variants, and registration;
- the closed appearance vocabulary and stable `data-hedron-*` markers;
- component props, first-party presentation CSS, and the documented cascade layers;
- typed `StyleSymbols`, component `styles.css`, style contracts, and the CSS compiler;
- asset policy, strict CSP, theme checks, visual conformance, and zero-application-CSS checks.

The high-level values—`DesignSystem`, brand inputs, `StyleRecipe`, and
`StyleScope`—compile to those authorities. They do not add a second cascade, selector language,
browser runtime, or stylesheet injection mechanism. An author can inspect the compiled theme and
recipe plan, override one named decision, eject explicit Python or scoped CSS, and continue with the
lower-level system at any time.

## Why another phase after 0.57

Phase 0.57 solved presentation completeness: a representative application can use shared semantic
props and first-party CSS instead of application layout/component CSS. It did not make creation of
a distinct, coherent application look beginner-friendly.

Today the first custom theme example asks an author to understand and coordinate:

1. `compile_palette(seed)`;
2. `default_theme().extend(...)`;
3. the difference between `tokens`, `palette`, `modes`, `variants`, `shape`, `elevation`, density,
   and navigation width;
4. registration and application selection;
5. which values are raw CSS and which are closed Hedron vocabulary;
6. contrast checks, forced colors, reduced motion, and print behavior;
7. component-level appearance, emphasis, size, density, padding, shape, and elevation;
8. when to use component props, a class hook, a theme token, scoped CSS, an override layer, or
   ejected styles; and
9. the build and strict-CSP consequences of each choice.

Those concepts are powerful, but they are an advanced starting point. The missing layer is not
more CSS capability. It is a small vocabulary of design intentions with transparent lowering and a
safe path to the existing details.

## Design principles

1. **One styling authority.** High-level values compile to `Theme`, appearance markers, component
   props, style contracts, and the existing CSS build.
2. **Intent first, details available.** Beginners choose brand, density, geometry, typography, and
   named roles before editing token maps or selectors.
3. **Accessibility is a compiler obligation, not a marketing claim.** Generated measurable pairs
   must pass the locked contrast rules; focus, motion, forced-color, print, zoom, and non-color
   semantics remain explicit evidence.
4. **CSP by construction.** Supported high-level styling emits external first-party build assets
   and finite markers, never inline style text or runtime-generated rules.
5. **Finite choices at the high level.** Arbitrary CSS values, selectors, URLs, fonts, and
   animations belong to explicit advanced layers with their existing policies.
6. **Predictable precedence.** Component-explicit values beat recipe values; local scopes beat
   application defaults; design defaults beat the base theme. Conflicts are explainable.
7. **No hidden semantic changes.** Styling cannot reorder DOM, change an accessible name, hide an
   authoritative value, grant interaction, or infer content/state meaning.
8. **Graduation is local.** A user may eject or replace one recipe, token group, component style,
   or scope without abandoning the design system.
9. **Deterministic output.** Equivalent inputs produce byte-equivalent plans, manifests, CSS, and
   source maps regardless of absolute path, process, or import order.

## Progressive styling ladder

| Level | Beginner-facing action | Existing representation |
|---|---|---|
| Built-in | `Hedron(theme="default" | "aurora")` | Registered first-party `Theme` |
| Brand | Construct a design from name + accent + finite feel choices | Resolved `Theme` and generated light/dark semantic tokens |
| Recipe | Apply a named semantic recipe such as `primary_action` or `data_surface` | Existing appearance and family-specific component props |
| Scope | Change theme, color mode, or density for one explicit subtree | Bounded `data-hedron-*` markers and inherited theme variables |
| Inspect | Explain, preview, diff, and check compiled decisions | Theme, recipe, style-contract, asset, and build manifests |
| Eject | Materialize one group/recipe/component or the whole design | Reviewable `Theme` Python, scoped CSS, manifest, and tests |
| Primitive | Edit semantic tokens, props, `styles.css`, or override layers directly | Existing 0.57 styling APIs and CSS compiler |

The high-level system remains a valid production authoring path. Ejection is a graduation tool,
not a requirement or deprecation signal.

## Abstraction exploration

### 1. Built-in looks remain the zero-config path

The default experience does not need a new object:

```python
app = Hedron(theme="aurora")
```

0.59 should improve discovery and preview of built-in themes, but must not force an author to
instantiate a design system to get Hedron's complete first-party presentation. `theme="default"`
and `theme="aurora"` remain ordinary, stable starting points.

### 2. A brand compiler is the smallest useful custom-design abstraction

Locked API shape:

```python
design = DesignSystem.brand(
    name="acme",
    accent="#2f6fed",
    density="comfortable",
    geometry="soft",
    typography="system-sans",
)

app = Hedron(theme=design)
```

D-104 freezes the exact signatures in `styling-authoring-inventory-059.toml` and the following
behavior:

- `name` and one trusted brand accent are sufficient for a complete result;
- light and dark semantic token sets are generated together rather than accidentally mixing a
  custom light accent with an unrelated inherited dark accent;
- neutral/background/surface families, on-colors, focus, danger, borders, and muted content are
  selected through deterministic accessible algorithms;
- density, geometry, typography, navigation width, elevation, and motion use finite named choices;
- system font stacks require no asset policy; a custom or remote font uses the existing explicit
  asset/egress/CSP path and is never fetched by the compiler;
- the result can be converted to and registered as an ordinary `Theme`;
- generated output records which values came from the seed, a preset, a user override, or an
  inherited base.

The brand compiler does not promise that every arbitrary color can remain visually unchanged.
When an input cannot produce the locked contrast/focus result, it fails with candidate remediation
or explicitly adjusts the derived semantic color and records that adjustment. It never silently
ships a failing pair.

### 3. Typed design choices replace raw maps on the beginner path

The current `Theme` maps remain available. The beginner facade should group common choices into
bounded, typed concepts:

| Design group | Beginner intent | Lowering target |
|---|---|---|
| Brand colors | 3/6-digit hex accent | `Theme.tokens`, `modes`, `palette` |
| Typography | system family, scale, readable measure | semantic font/size/line tokens |
| Geometry | square, soft, rounded | `Theme.shape` token values |
| Density | compact, comfortable, spacious | existing density vocabulary/default markers |
| Elevation | flat, subtle, layered | existing elevation/overlay tokens |
| Motion | standard, calm, none | motion tokens plus mandatory reduced-motion behavior |
| Navigation | compact, default, wide | validated `nav_width`/shell tokens |

These values are not a general property bag. The compiler rejects unknown fields and unsupported
combinations. Advanced authors may inspect the generated `Theme`, then use `Theme.extend`, token
maps, or scoped CSS for needs outside the bounded vocabulary.

### 4. Named style recipes capture repeated semantic presentation

Applications often repeat coherent prop combinations even after adopting a theme: the primary
submit action, a quiet secondary action, a raised KPI surface, a dense data surface, a destructive
confirmation action, or subdued metadata text. Copying those props everywhere makes visual intent
hard to audit and change.

The locked recipe catalog groups only already-supported optional props:

```python
design = DesignSystem.brand(name="acme", accent="#2f6fed").with_recipes(
    StyleRecipe.control(
        "primary_action",
        emphasis="primary",
        appearance="solid",
        size="md",
    ),
    StyleRecipe.surface(
        "data_surface",
        appearance="raised",
        density="compact",
        padding="md",
    ),
)
```

Application syntax is the render-free `design.apply(recipe, component)` compiler helper. It returns a
clone of the same component type before render; the original remains unchanged. D-104 rejects an
additive argument on every built-in because that would widen the whole constructor fleet and make
legacy non-`None` defaults indistinguishable from explicit values. The helper obeys these rules:

- a recipe is immutable, named, family-scoped, and serializable;
- families are exactly control, surface, data, status, and content in 0.59;
- a recipe contains semantic Hedron values, not CSS declarations or selectors;
- applying a recipe produces the same component and existing props/markers, with no wrapper DOM or
  browser behavior;
- a recipe incompatible with the component family fails before render;
- explicit component props win over the recipe and the explanation records the override;
- a recipe may extend another recipe only through an acyclic, bounded chain;
- required state meaning stays with component content/semantics, never the recipe name alone.

Recipes are useful for consistency and migration, but they do not replace purpose-specific
components. A recipe cannot turn a `Text` node into a button, a `Surface` into a landmark, or a
neutral action into a destructive operation.

### 5. Style scopes make local defaults explicit

Some applications need a compact data region inside an otherwise comfortable UI, or a themed
preview mounted inside a page. A bounded `StyleScope` can make that decision once for a visible
subtree:

```python
StyleScope(density="compact", children=[orders_table])
```

Contract:

- the scope is an explicit DOM boundary with documented semantics, not ambient thread-local or
  request-global state;
- it accepts only `theme`, `color_mode`, and `density`, and emits their finite markers and inherited
  custom properties through first-party CSS;
  by first-party CSS;
- it does not visually reorder content, alter tab order, or hide content by default;
- nested scope precedence is deterministic and inspectable; recipe defaults are not supported on a
  scope in 0.59;
- explicit child values win;
- scopes cannot smuggle raw CSS variables, selectors, URLs, or user data into style text;
- an author who needs an arbitrary layout or selector uses explicit components or scoped CSS.

D-104 selects a dedicated semantically neutral `StyleScope` that renders one explicit `div` with
`data-hedron-style-scope`. No invisible wrapper or landmark is permitted. Scope-wide recipes,
field recipes, and layout recipes are Deferred because the 0.57 component models cannot prove
explicitness for their non-`None` defaults without hidden descendant mutation or specificity.

### 6. Inspection is part of the API

The compiled design projection should answer beginner questions without requiring CSS inspection:

```python
plan = design.explain()

plan.theme                 # resolved Theme identity and parent
plan.inputs                # trusted author inputs, never request/user values
plan.tokens                # values plus source/provenance
plan.modes                 # light/dark and explicit overrides
plan.recipes               # family, inheritance, resolved props
plan.scopes                # named or discovered explicit scope decisions
plan.components            # affected first-party style contracts
plan.assets                # local/remote policy dispositions
plan.diagnostics           # contrast, compatibility, missing contract facts
plan.limitations           # what requires explicit Theme/CSS work
```

Locked tooling:

```text
hedron --app app:app style explain
hedron --app app:app style preview
hedron --app app:app style diff default acme
hedron --app app:app style check
hedron --app app:app style eject acme --recipe primary_action --output styling-ejected
```

D-104 freezes these spellings and `hedron.design-system-plan/1`,
`hedron.design-system-diff/1`, `hedron.design-system-preview/1`, and
`hedron.design-system-source-map/1`. All views consume one static design plan. Explanation and diff
must not call routes, loaders, component callbacks, remote font services, or arbitrary application
code.

### 7. Preview is a finite conformance gallery, not a design application

The preview should render a locked representative matrix:

- typography roles and long/international text;
- actions, fields, validation, focus, disabled and destructive states;
- surfaces, shell, navigation, overlays, status, tables, and forms;
- light, dark, forced-colors, reduced-motion, print, RTL, narrow viewport, and 200% zoom;
- recipe and scope examples with resolved-source annotations.

Explorer may host the interactive view and the CLI may emit a static local artifact, but both use
the same plan and fixtures. 0.59 does not add a drag-and-drop editor, hosted design service, Figma
sync, arbitrary live CSS editor, or production route.

### 8. Override and ejection are the advanced bridge

The high-level system must expose stable named groups and recipes so an author can graduate one
piece:

```text
design
├── brand
├── typography
├── geometry
├── elevation
├── motion
├── recipes
│   ├── primary_action
│   └── data_surface
└── component_overrides
```

Ejection may materialize:

- a resolved explicit `Theme` definition;
- one typed design group as `Theme.extend(...)` overrides;
- one recipe as explicit component props;
- one component override as scoped `styles.css` plus its `StyleSymbols`/contract metadata; or
- a complete reviewable design package.

Generated output includes a versioned source map and visual/contract checks. It writes only inside
the selected project root, never overwrites by default, never includes request data or secrets, and
never generates selectors against undocumented private markup. The result uses public APIs and
continues to compile through the existing build.

## Lowering and precedence contract

The intended lowering is:

```text
DesignSystem.brand inputs
    → deterministic accessible light/dark semantic palette
    → typed design groups
    → ordinary resolved Theme

named StyleRecipe
    → validate component family
    → existing appearance/family props
    → stable data-hedron-* markers

StyleScope
    → explicit theme/color-mode/density boundary markers

Theme + markers + component styles
    → existing CSS compiler/build manifest
    → external fingerprinted CSS under current cascade layers
```

Precedence from strongest to weakest:

1. explicit component prop or explicit scoped-CSS override;
2. explicit recipe applied at the component;
3. nearest explicit `StyleScope` recipe/default;
4. design-system application defaults;
5. resolved `Theme` values;
6. first-party baseline presentation.

Conflicting values at the same level follow `styling-precedence-059.toml`: duplicates fail unless
the explicit replacement option is used, and canonical mapping order never becomes precedence. The system
must never rely on incidental Python mapping order or selector specificity accidents.

## Interaction with phase 0.58 abstractions

Every 0.58 generated screen, form, workspace, task, dashboard, auth surface, and upload surface
uses 0.57 presentation primitives. In 0.59 those facades may accept or inherit design-system recipe
roles, but they may not fork styling logic.

- Generated surfaces use stable semantic recipe slots such as primary action, secondary action,
  form surface, data surface, status, and destructive action.
- 0.58 named-surface overrides remain stronger than 0.59 style defaults.
- Feature explanation links to the same style-plan facts rather than copying them.
- Feature ejection preserves recipe references or resolves them to explicit props according to the
  selected ejection level.
- Styling never changes authorization, route exposure, mutation meaning, refresh effects, upload
  enforcement, or task state.

This dependency is why D-104 is conditional: Stage 1 waits for the final 0.58 cut and its required
predecessor audit even though the 0.59 contract packet is now frozen.

## Starter-example adoption policy

At the 0.59 cut, every maintained documentation example identified as **starter**,
**beginner**, **quick start**, **golden path**, **minimal**, **first app**, **theming tutorial**, or
generated **scaffold** uses the highest applicable 0.59 styling abstraction.

Normative teaching order:

1. use a built-in theme or the one-step branded design-system facade;
2. introduce a named recipe only when repeated visual intent appears;
3. show explain/preview before token dictionaries or selectors;
4. show the equivalent resolved `Theme`, appearance props, or ejected scoped CSS afterward; and
5. link to explicit styling APIs for advanced customization.

The inventory includes root/flagship/package README starts, getting-started pages, beginner
cookbook entries, theme examples, zero-CSS examples, generated scaffolds, 0.58 starter templates,
and any package quick start that demonstrates styling. A document specifically teaching `Theme`,
semantic tokens, `StyleSymbols`, component `styles.css`, cascade layers, CSS compilation, or
ejection may use those primitives first only when labeled **Advanced**, **Explicit**,
**Lower-level**, or **Under the hood**. Historical release notes and upgrade fixtures stay
historically accurate.

D-104 freezes a machine-readable inventory and required destination for every entry. `DX-059`
fails if an inventoried starter still teaches raw token maps, repeated appearance prop bundles, or
scoped CSS first when an applicable 0.59 abstraction exists.

## Accessibility

- Generated light/dark color pairs satisfy the locked measurable contrast matrix or fail
  compilation with remediation.
- Focus remains visible and distinguishable; focus tokens cannot be omitted by a preset.
- Forced-colors behavior uses semantic structure and system colors where required, not generated
  brand colors as the source of truth.
- Reduced motion always has a static equivalent and a design choice cannot disable the user
  preference.
- Recipe/state meaning is expressed in text, semantics, icons with labels, or structure—not color,
  elevation, or animation alone.
- Typography/spacing choices pass 200% zoom, narrow viewport, long-content, and user text-spacing
  checks.
- Preview evidence includes keyboard focus order and screen-reader semantics even though the
  abstraction is visual.

## Security and privacy

- Only trusted application configuration may become design input. Request values, database values,
  and arbitrary user content cannot become CSS, tokens, selectors, class names, URLs, or font
  sources.
- All CSS-like values reuse existing validation. High-level APIs prefer closed names over raw
  strings.
- Remote fonts, images, imports, and styles are never fetched or authorized implicitly; they use
  registered assets and current CSP/egress policy.
- Preview and explanation are static and redacted. They do not render sensitive application data or
  invoke application callbacks.
- Ejection defends project-root, traversal, symlink, collision, and overwrite boundaries.
- Component customization uses public parts/slots/tokens or ejected owned CSS; private selectors
  remain unsupported.
- Generated CSS remains external and fingerprinted; no `unsafe-inline` relaxation is introduced.

## Performance and build behavior

- Using only a built-in theme adds no new runtime asset or import cost.
- A compiled design emits one deduplicated token/recipe contribution through the existing bundle;
  it does not generate per-request or per-component stylesheets.
- Recipe application is normalized before render and must not add wrapper DOM or browser runtime.
- Unused optional preview/Explorer tooling stays out of production imports and wheels where
  package boundaries require it.
- D-104 locks maximum token groups, recipes, inheritance depth, scopes in the representative
  corpus, emitted CSS delta, build latency, and explanation/preview artifact sizes. Excess input is
  rejected rather than silently truncated.

## Compatibility and migration

- Existing `Hedron(theme="...")`, `Theme(...)`, `default_theme().extend(...)`,
  `compile_palette(...)`, theme registration, appearance props, `class_`, scoped `styles.css`,
  `StyleSymbols`, build manifests, and cascade order retain behavior.
- `default_styles=False` remains the explicit fully custom canvas and is not silently combined with
  design-system assumptions.
- Explicit component props always retain their current defaults when no recipe/design is supplied.
- Existing custom themes can be wrapped/imported as the advanced base of a design system without
  rewriting token values.
- Existing theme output is covered by golden CSS/manifest fixtures; introducing provenance cannot
  change hashes unless the actual emitted CSS changes through an explicit migration.
- Third-party components consume only declared public style contracts and record unsupported recipe
  families honestly.

## Adapter and package disposition

The portable design plan, recipes, and explanation schema belong as low in the package graph as
their existing authorities permit. D-104 locks final ownership.

- `hedron-core` is the likely authority for portable frozen values, compilation, `Theme` lowering,
  appearance validation, and conformance fixtures.
- `hedron` owns FastAPI application selection, CLI integration, build/ejection orchestration, and
  starter scaffolds.
- Explorer may visualize the shared plan but does not own a second design model.
- Flask/Django consume portable compiled themes/markers through existing adapter asset behavior;
  they receive no nominal application facade claim without native evidence.
- elements, charts, maps, data, extras, Jinja, simulation, and conformance publish honest recipe/
  token/style-contract compatibility rather than copying the compiler.
- No new package is authorized for 0.59.

## Non-goals

0.59 does not authorize:

- a Tailwind-like utility API, free-form CSS-in-Python DSL, arbitrary property dictionary, or
  runtime atomic-CSS engine;
- a second token registry, component tree, renderer, cascade, asset pipeline, or CSS compiler;
- drag-and-drop design tooling, hosted collaboration, Figma synchronization, or design-file import;
- AI-generated production CSS or automatic brand scraping;
- implicit remote fonts/assets, CDN dependencies, or CSP relaxation;
- private-selector support, shadow-DOM piercing, or global-selector expansion;
- DOM reordering, content hiding, accessible-name changes, or state semantics inferred from style;
- automatic logo generation, copywriting, data visualization semantics, or product design quality
  certification;
- a claim that generated palettes alone make an application accessible;
- removal or deprecation of `Theme`, appearance props, scoped CSS, or `default_styles=False`;
- implementation of 0.58, a 1.0 schedule, or a package-version bump during planning.

## Workstreams

| Workstream | Outcome | Depends on |
|---|---|---|
| W0 | D-104 locks plus required final-0.58 predecessor audit/amendment | Published/Verified `v0.58.0` before Stage 1 |
| W1 | Portable design plan, provenance, lowering, explanation, and diff | W0 |
| W2 | Brand compiler with coordinated light/dark semantic palettes | W1 |
| W3 | Typed design groups and bridge to/from existing `Theme` | W1–W2 |
| W4 | Family-scoped named recipes and deterministic resolution | W1, W3 |
| W5 | Explicit bounded scopes and precedence behavior | W3–W4 |
| W6 | Shared CLI/Explorer preview, explain, diff, and check | W1–W5 |
| W7 | Local override and safe whole/partial ejection | W1–W6 |
| W8 | 0.58 surfaces and ecosystem package/style-contract integration | W4–W7 |
| W9 | Starter migrations, branded/recipe examples, and learning path | W6–W8 |
| W10 | Accessibility, CSP/security, visual, browser, performance, upgrade evidence | W2–W9 |
| W11 | Exports, optional isolation, clean wheels, metadata, and release rehearsal | W10 |

## Planned release gates

| Gate | Required evidence |
|---|---|
| `CONTRACT-059` | Exact symbols, schemas, finite vocabularies, precedence, maturity, diagnostics, dispositions |
| `LOWER-059` | Differential design→Theme/props/markers/build parity and no second styling runtime |
| `BRAND-059` | Deterministic coordinated light/dark generation, failure/remediation, provenance |
| `THEME-059` | Typed design groups, Theme bridge, registration, inheritance, compatibility |
| `RECIPE-059` | Family validation, inheritance, explicit-prop precedence, no wrapper/browser runtime |
| `SCOPE-059` | Explicit boundaries, nesting, no semantic/DOM-order changes, predictable resolution |
| `TOOLING-059` | Static redacted explain/preview/diff/check from one manifest |
| `EJECT-059` | Whole/partial public-API ejection, source maps, parity, path/overwrite safety |
| `A11Y-059` | Contrast, focus, non-color meaning, motion, zoom, text spacing, media/RTL evidence |
| `CSP-059` | External deterministic CSS, asset/egress policy, hostile input and no-inline proof |
| `VISUAL-059` | Three-engine representative gallery and controlled visual-diff evidence |
| `ADAPTER-059` | Honest core/FastAPI/Flask/Django/elements/Jinja/sim/conformance dispositions |
| `REGRESS-059` | Existing Theme/appearance/scoped-CSS/build output and 0.53–0.58 compatibility |
| `DX-059` | Beginner tasks, complete starter migration, explain-to-eject learning outcomes |
| `PKG-059` | Clean wheels, exports, optional isolation, docs, upgrades, metadata, rehearsal |

## Acceptance criteria

Phase 0.59 is complete only when:

- one accent plus finite optional choices produces a complete deterministic design and coordinated
  light/dark output through an ordinary `Theme`;
- generated measurable color/focus pairs pass the locked matrix or compilation fails clearly;
- named recipes resolve only to existing semantic component props and markers;
- explicit props, scopes, design defaults, themes, and base CSS follow one documented precedence;
- explain, preview, diff, and check consume one static redacted manifest without callbacks;
- whole and partial ejection produce safe, reviewable public-API output with parity evidence;
- 0.58 generated surfaces consume the same recipe/style authority;
- existing styling APIs and emitted default/built-in-theme behavior remain compatible;
- every inventoried styling starter uses the highest applicable 0.59 abstraction, while primitive
  examples remain available as clearly labeled advanced material;
- strict CSP, no-JS, forced colors, reduced motion, print, RTL, keyboard, screen-reader semantics,
  200% zoom, text spacing, long content, narrow viewport, and three-engine evidence pass;
- all fifteen 0.59 gates are Verified with zero Deferred; and
- release metadata truthfully records Beta maturity and the real registry status.

## Resolved questions (D-104)

1. **Root value?** `hedron_core.design_system.DesignSystem`, exported from `hedron_core` and
   `hedron`; exact Beta signatures are locked in `styling-authoring-inventory-059.toml`.
2. **Application boundary?** Widen existing `Hedron(theme=...)` to accept `str | Theme |
   DesignSystem | None`. A `Theme` registers then selects its name; a `DesignSystem` compiles to an
   ordinary Theme, registers it, and selects its name before the existing lifespan. Configuration
   and environment values remain names only; there is no second app-state authority.
3. **Brand inputs/algorithm?** Name plus a 3/6-digit hex accent is sufficient. Optional choices are
   existing density plus finite geometry, system typography, elevation, motion, and navigation
   presets. `hedron.brand-palette/1` compiles light/dark together, preserves the requested seed as
   palette provenance, and reports every semantic adjustment.
4. **Finite design groups?** Geometry `square|soft|rounded`; typography
   `system-sans|system-serif|system-mono`; elevation `flat|subtle|layered`; motion
   `standard|calm|none`; navigation `compact|default|wide`; density retains the shipped three
   values. Everything else uses explicit `Theme`/assets/CSS.
5. **Recipe application?** `DesignSystem.apply(recipe, component)` clones before render. No
   constructor-fleet widening, wrapper DOM, browser runtime, or mutation of the input component.
6. **Recipe catalog?** Five families: control, surface, data, status, and content. Only catalogued
   optional `None`-default presentation fields may be filled, so explicit non-`None` props always
   win. Inheritance is same-family, acyclic, and at most four levels. Field/layout recipes are
   Deferred.
7. **Scope?** A dedicated neutral `StyleScope` renders an explicit `div` boundary and supports only
   registered theme name, light/dark mode, and density. Recipe defaults on scopes are Deferred.
8. **Schemas?** `hedron.design-system-plan/1`, `hedron.design-system-diff/1`,
   `hedron.design-system-preview/1`, and `hedron.design-system-source-map/1`; canonical JSON digests,
   project-relative paths, no runtime values/callables/secrets.
9. **Preview/deltas?** `styling-gallery/1` across Chromium/Firefox/WebKit, three viewports, light/
   dark/forced-colors/reduced-motion/print, LTR/RTL, 100%/200%, text-spacing and hostile content.
   Pixel delta above 1% fails; 0.1–1% requires recorded review; DOM/computed facts are mandatory.
10. **Budgets?** Exact reject-not-slice ceilings and p95/ratio limits are in
    `styling-budgets-059.toml`, including 64 recipes, depth four, 128 KiB generated design CSS,
    5 MiB static preview, and zero unused import/asset delta.
11. **0.58 roles?** Ten built-ins cover primary/secondary/destructive actions, page/form/data/
    dashboard surfaces, dense data, inline status, and metadata. Styling never supplies domain
    authority for a destructive role.
12. **Starter inventory?** `styling-starter-docs-059.toml` locks root/flagship starts, getting-
    started pages, theme/presentation docs, zero-CSS/theme-gallery examples, the FastAPI scaffold,
    and all four 0.58 scaffolds. Primitive architecture/acceptance documents remain explicit.
13. **Host disposition?** Portable compiler/values/recipes/scope are core Supported; FastAPI owns
    direct constructor/CLI/build integration; Flask/Django are compiled-theme consumers with
    explicit adapter spelling; Jinja/elements/ecosystem claims are inventory-limited.
14. **Early refine honesty?** D-104 is conditional because runtime `v0.58.0` does not exist. All
    Stage 1 work is blocked until Published/Verified 0.58 and a recorded audit; material drift
    requires an accepted amendment rather than silent contract reinterpretation.
