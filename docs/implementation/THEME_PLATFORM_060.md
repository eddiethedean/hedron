# Custom theme platform implementation plan (phase 0.60)

**Status:** Implemented and verified in-tree; hosted release CI and coordinated publication remain
release-cut activities
**Authority:** RFC-0089 / proposed D-108 / `docs/acceptance/theme-platform-contract-060.toml`
**Baseline:** Published/Verified in-tree and PyPI `v0.59.0`
**Target:** `v0.60.0`

## Delivery strategy

0.60 is an in-place evolution of `Theme`, `DesignSystem`, `StyleRecipe`, `StyleScope`, the registry,
the default stylesheet, the 0.59 compiler, and style tooling. Work lands in vertical slices with
behavior evidence in the same change. No temporary second theme or validation authority may merge.

The critical path is:

```text
W0 baseline/contract
  -> W1 release-evidence reconciliation
  -> W2 color + W3 ThemeSpec/contracts/validation/package
  -> W4 accessibility modes + W5 recipes/scopes + W6 preferences
  -> W7/W8 component completion + W9 built-in catalog
  -> W10 tooling/docs + W11 whole-matrix hardening
  -> W12 cut
```

W7 and W8 can begin after W0 because their component contracts are mostly independent. W5 cannot
land scoped defaults before explicit-authored-value tracking passes. W6 cannot claim no-flash until
server-first page markers and the CSP asset order are browser-proven.

## W0 — baseline, contract, and issue ownership

- record the exact 0.59 APIs, CSS bytes, schema versions, browser floors, emitted markers, public
  themes, recipe catalog, validation behavior, and docs/release claims;
- lock candidate API names, finite values, diagnostics, schemas, budgets, package dispositions,
  coverage-profile membership, component-contract registration, theme gallery cap/design brief,
  and manual-review policy;
- assign #627–#635 to 0.60 workstreams/gates and add the 0.60 milestone without closing them;
- record the status of unrelated open #86/#192 and preserve their existing owners;
- freeze two upgrade sources: PyPI `v0.59.0` and the `v0.59.0` tag/in-tree fixture; and
- create executable contract checks that fail if issue mapping or required evidence disappears.

Exit: `CONTRACT-060` packet review passes. No runtime or version change occurs in W0.

## W1 — reconcile 0.59 claims and evidence

- inventory every 0.59 styling claim against runtime behavior and executable tests;
- add a negative/positive modern-color probe showing the current #633 gap;
- replace marker-only Brand/Toast/workflow assertions with computed-style/browser facts;
- classify each mismatch as 0.60-owned compatibility debt or a documentation correction;
- make gate scripts verify the advertised behavior, not only that named test files execute; and
- retain an immutable reconciliation report consumed by `REGRESS-060`.

Exit: `RECONCILE-060` explains every discovered mismatch and prevents false green evidence.

## W2 — typed color and palette-v2 (#633)

- implement the pure-Python absolute-color parser and immutable `Color` model;
- normalize admitted spaces through a documented conversion/white-point pipeline;
- implement deterministic clipping/gamut mapping and sRGB serialization;
- preserve optional higher-gamut declarations behind fallbacks;
- evolve brand compilation and contrast search to consume normalized colors;
- emit `hedron.brand-palette/2` provenance, adjustments, and compatibility metadata;
- fuzz functions, numbers, units, comments, escapes, URLs, relative/context values, and budgets; and
- cross Python/compiler/build/manifests/browser snapshots for identical resolved output.

Exit: `COLOR-060` and `PALETTE-060` pass for hex, RGB, HSL, HWB, Lab/LCH, OKLab/OKLCH, gamut,
contrast, injection, determinism, and legacy fixtures.

## W3 — ThemeSpec, contracts, validation, and packages

### Authoring model

- implement immutable serializable `ThemeSpec` as the canonical input and make `ThemeBuilder` a
  convenience facade over it rather than another authority;
- implement a bounded alias graph with cycle/missing-reference detection, resolved-value
  inspection, and field-level input/resolution/provenance;
- implement ordered `ThemePatch` overlays with compatible-base checks, retained layer provenance,
  and full revalidation after composition;
- fingerprint canonical specs, patches, algorithm revisions, registry inventory, and Hedron
  compatibility so equal inputs reproduce equal CSS, reports, and package digests;
- admit explicit expert token/palette input through the same validators;
- define required core and optional semantic token catalogs; and
- ensure direct `Theme` construction and `DesignSystem.from_theme` remain first-class.

### Component contracts and profiles

- add immutable `ComponentThemeContract` registration for every public themeable component before
  registry seal, declaring parts, states, variants, required roles, contrast relationships,
  accessibility mappings, and fallback policy;
- derive validation inventory from the existing registry and reject unregistered public components
  or handwritten-inventory drift;
- define monotonic `core`, `forms`, `data`, `workflow`, and `complete` coverage profiles;
- require packages, reports, previews, and docs claims to name the profile actually validated; and
- require every first-party built-in theme to pass `complete` without making limited-profile custom
  themes validate irrelevant optional packages.

### Validation

- implement structural, token, recipe, contrast/focus, state, asset/CSP, package, fallback, and
  compatibility validators;
- validate registered foreground/background, focus/surrounding, border/surface, selection, status,
  and disabled-state relationships across every applicable mode rather than isolated color values;
- return stable `hedron.theme-validation/1` reports with deterministic ordering/digest;
- distinguish error, warning, information, adjustment, waiver, and unsupported evidence;
- require a reason/owner/expiry for waivers and exclude waived failures from unqualified claims;
- expose one engine to Python, CLI, Explorer, build, and package verification; and
- offer source-aware candidate remediation previews while limiting `--fix` to canonical formatting;
  never silently change color/accessibility decisions or emit a single aggregate health score.

### Packaging

- implement data-only `hedron.theme-package/1` manifests and deterministic archives containing
  ThemeSpecs, optional ThemePatches, profiles, fingerprints, and migration metadata;
- validate namespaces, versions, Hedron compatibility, conflicts, assets, hashes, and licenses;
- register only after validation and existing registry lifecycle checks;
- reject remote fetches, executable hooks, traversal, duplicate authority, and unsafe CSS values; and
- prove install/load/build/uninstall/upgrade behavior from clean wheels.

Exit: `THEME-060`, `VALIDATE-060`, and `PACKAGE-060` pass with registry-derived inventories,
reproducible fingerprints, overlay provenance, and truthful profile claims.

## W4 — accessibility modes and state matrices (#634)

- add separate forced-colors and more-contrast maps to the theme model;
- define allowed semantic overrides and component-state mappings;
- generate framework-owned media queries with explicit `forced-color-adjust` policy;
- prefer system colors in forced-color mode and retain non-color state cues;
- validate focus, border, selected, active, disabled, danger/warning/success/info, controls, data,
  overlays, workflows, charts/maps, and authored elements;
- make opt-in incomplete/contradictory mode sets actionable errors; and
- test unsupported preference-media fallback without broken declarations or markup.

Exit: `A11Y-MODE-060` and the relevant `A11Y-060` matrix pass.

## W5 — recipe families and explicit style context (#631, #632)

1. Introduce constructor sentinels or equivalent field provenance so omitted, explicit `None`, and
   explicit concrete values remain distinguishable without breaking 0.59 calls.
2. Define `RecipeFamily` with finite values and per-component presentation-field bindings.
3. Register families deterministically before registry seal; validate component opt-in and package
   namespace ownership.
4. Keep inheritance same-family, acyclic, and bounded; reject behavior/state/security fields.
5. Define serializable `StyleContext` mapping family/semantic roles to registered recipes.
6. Apply precedence: explicit component > inner context > outer context > design role > component
   default.
7. Preserve scope through DOM-inherited fragments; require explicit host binding for detached OOB/
   overlay roots.
8. Extend design plans, manifests, explain/diff/eject, and Explorer with family/context provenance.

Exit: `RECIPE-060` and `SCOPE-060` pass direct, nested, fragment, OOB, invalid, cycle, package,
explicitness, and compatibility tests.

## W6 — theme preference and picker (#635)

- implement immutable allowlisted `ThemePreference` resolution;
- extend page asset injection to canonical theme/color-mode/`color-scheme` markers before paint;
- implement accessible `ThemePicker` ordinary-form behavior and optional HTMX enhancement;
- document cookie/session/account persistence adapter boundaries for each first-party host;
- implement an optional external CSP-safe bounded boot asset for local preference only;
- handle invalid/stale themes, catalog changes, history restoration, fragments, dialogs, toasts,
  nested scopes, multi-tab events, no JavaScript, and disabled assets; and
- keep application authorization and persistence authoritative.

Exit: `PREFERENCE-060`, `SECURITY-060`, and browser no-flash evidence pass.

## W7 — Brand and feedback hosts (#627, #628)

### Brand

- stack name/subtitle natively; apply min-inline-size and logical overflow behavior;
- reuse shared overflow/density vocabulary and emit public markers/tokens;
- preserve name-only, linked/unlinked, mark, attributes, and arbitrary `AppShell.brand` content;
- cover narrow, long, international, RTL, 200%/400% zoom, forced colors, print, and no CSS; and
- add a zero-application-CSS fixture with computed layout assertions.

### Feedback

- give `ToastHost` finite logical placement, position policy, width, max width, and gap;
- apply safe-area insets, layer tokens, narrow viewport and print behavior;
- retain `#hedron-toast`, OOB swap semantics, TTL/dismiss, reduced motion, and stable default output;
- eliminate duplicate announcement caused by nested live-region ownership; and
- prototype a separate AlertHost only if persistent request-error fragments cannot safely compose
  with one typed host contract.

Exit: `BRAND-060` and `FEEDBACK-060` pass.

## W8 — workflow canvas and ScrollRegion (#629, #630)

### ConnectorFlow

- add surface-aligned appearance/density, grid/dots/none decoration, overflow, and min-size intent;
- expose theme tokens rather than raw colors or arbitrary lengths;
- preserve horizontal/vertical/collapse semantics and authoritative state input;
- suppress decorative textures in forced colors/print and retain complete content; and
- cover long nodes, narrow widths, zoom, RTL, reduced motion, and feature-off layouts.

### ScrollRegion

- add a semantic-preserving wrapper with block/inline/both axes and finite size tokens;
- support accessible naming and visible overflow/scrollbar affordances;
- keep descendants reachable and conditionally focus the container only when evidence requires it;
- remove clipping/max-size in print and preserve DOM/source order; and
- compose with ordered/unordered lists, Timeline, ProcessFlow, arbitrary native nodes, and tables
  without replacing their semantics.

Exit: `WORKFLOW-060` and `SCROLL-060` pass.

## W9 — reviewed built-in theme catalog and fleet adoption

- lock a visual brief and public names for no more than three materially distinct additions;
- prioritize authoring/validation completeness over filling the maximum catalog allowance;
- require every theme to cover light/dark, accessibility modes, semantic/state tokens, complete
  fleet, fallbacks, local assets, and licensing;
- keep `default` and `aurora` compatibility snapshots unchanged unless a documented defect demands
  a reviewed delta;
- apply the new token/state catalog to every first-party component/package or record an explicit
  not-applicable disposition; and
- create zero-application-CSS reference pages for product, dashboard, data, workflow, auth, docs,
  chart, map, and rich-element surfaces.

Exit: `CATALOG-060`, `VISUAL-060`, and package disposition checks pass.

## W10 — tools, Explorer, documentation, and templates

- add `hedron style theme init|check|preview|diff|package|explain` using shared services;
- expose a read-only Theme Lab in Explorer with side-by-side mode rendering, token/state inspection,
  spec/patch diffs, gamut/fallback warnings, keyboard/focus/zoom exercises, and report export;
- generate starter theme packages without overwriting files;
- ship a third-party conformance kit that generates a declared-profile fixture, state/mode matrix,
  portable JSON report, human-readable artifacts, inventory digest, and fingerprint verification;
- provide CI/SARIF output with token/component/mode/state/source context;
- document built-in selection, builder, explicit Theme, recipes/scopes, accessibility modes,
  preference storage, packaging, compatibility, and advanced CSS/ejection paths;
- migrate maintained styling examples and add upgrade recipes from 0.59; and
- publish a validation troubleshooting catalog keyed by stable diagnostics and a lifecycle guide
  covering compatibility ranges, additive warnings, migration/rename maps, and announced errors.

Exit: `TOOLING-060`, `EXPLORER-060`, `CONFORMANCE-060`, and `DOCS-060` pass.

## W11 — security, accessibility, compatibility, and performance hardening

- fuzz every parser/manifest/preference/package/asset boundary and enforce resource budgets;
- run three engines across theme/mode/preference/direction/zoom/content/feature combinations;
- complete manual keyboard, focus, announcement, forced-color, print, and visual review;
- run public/in-tree 0.59 upgrade fixtures and package archive compatibility;
- prove token/component-contract/profile lifecycle warnings and migrations, strict versus
  compatibility validation, and that no package silently gains a broader coverage profile;
- enforce default CSS, per-theme CSS, optional JS, asset-request, build, validation, and browser
  style/layout budgets; and
- verify no theme or recipe changes behavior, authority, semantics, or data exposure.

Exit: `SECURITY-060`, `A11Y-060`, `COMPAT-060`, `PERF-060`, and `REGRESS-060` pass.

## W12 — release cut

- close #627–#635 only after their behavior evidence and source use cases pass;
- require zero unowned open styling issues or an accepted exclusion with owner/destination;
- build clean wheels and theme-package fixtures from both upgrade sources;
- verify every gate/report digest, docs claim, registry tier, changelog, and rollback path;
- rehearse install, theme creation, validation failure, package distribution, selection, and upgrade;
  and
- publish only when all gates are Verified with zero Deferred among required rows.

## Definition of done

An author can create, overlay, validate by declared profile, package, register, preview, diff, and
select a custom theme through documented finite APIs; the canonical ThemeSpec, registry-derived
contracts, semantic graph, and fingerprints are deterministic; modern color and accessibility modes
have deterministic fallbacks; recipes
and scoped defaults remain presentation-only and explicitly ordered; all nine issues close; every
built-in theme passes the complete matrix; the third-party conformance kit passes; 0.59 upgrade
fixtures remain valid; security,
accessibility, performance, docs, and packaging evidence passes; and no second styling authority or
unsupported compliance claim exists.
