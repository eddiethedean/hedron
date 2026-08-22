# Upgrade fixtures for phase 0.59

**Public source:** PyPI `v0.58.0`
**Living source:** Published/Verified in-tree `v0.58.1`
**Target:** `v0.59.0`
**Authority:** D-106 / D-107 / RFC-0087 / `modern-css-contract-059.toml` /
`modern-css-compatibility-059.toml`

The corpus proves that the modern CSS overhaul is additive and reviewable. It compares rendered
DOM, public attributes/classes, manifests, compiled CSS semantics, computed styles, visual facts,
assets, diagnostics, accessibility facts, and behavior. Textual CSS identity is required only where
it is itself a public/determinism contract.

## Existing application contracts

Fixtures retain and exercise:

1. `default_styles=True` and `default_styles=False` pages.
2. Built-in `default` and `aurora` themes, string selection, `Theme`, `Theme.extend`, modes,
   registered metadata, compiled theme CSS, and existing DesignSystem brand output.
3. Existing `DesignSystem` groups, five recipe families, ten generated-feature roles,
   `DesignSystem.apply`, `StyleScope(theme/color_mode/density)`, inspect/diff/check/preview/eject,
   and feature/style explanation links.
4. Existing semantic appearance, size, density, width, spacing, layout, responsive, overflow,
   priority, typography, elevation, and motion props/markers.
5. Existing Container, Stack, Inline, Grid, GridItem, FormGrid, SplitView, MasterDetail,
   ActionGroup, AppShell, surfaces, controls, forms, tables, data, status, workflow, dialog, popover,
   and Web Component output.
6. Existing public classes, `data-hedron-*` markers, custom properties, style contracts, public
   parts, component `styles.css`, `StyleSymbols`, local assets, and strict-CSP pages.
7. Existing v1 CSS symbol manifests, class/keyframe hashes, source maps, build manifests, wheel
   assets, and production compile gate.
8. Flask, Django, Jinja, Explorer, data, charts, maps, elements, extras, sample-kit, notebook, sim,
   workbench, and conformance package styling dispositions.

No source fixture is automatically opted into query containers, Theme variants, scoped defaults,
new recipe families, modern color input, anchor positioning, transitions, or consumer primitives.

## Compiler compatibility corpus

For each v1 component stylesheet, compile with the source and target compilers and compare public
symbols, assets, selector meaning, keyframes, cascade placement, and browser computed results.
Required fixture groups include:

- simple classes, multiple selectors, combinators, attributes, pseudo-elements, and
  `:global(...)`;
- `:is()`, `:where()`, `:not()`, `:has()`, escaped identifiers, Unicode, comments, and strings;
- nesting with `&`, nested declarations, nested selectors, nested `@media`, `@supports`,
  `@container`, and `@scope`;
- keyframes plus every accepted animation-name/shorthand position, multiple animations, CSS-wide
  keywords, timing functions, and custom properties;
- compiler-owned layers, an authored copy of the owning layer, named sublayers, anonymous layers,
  and legal top-level layer ordering;
- quoted and `url()` local imports, import cycles/depth/bytes, remote imports, local/remote/data URL
  assets, fonts, image sets, traversal, symlinks, missing files, and unsafe legacy values;
- custom properties, `@property`, font descriptors, counter/custom identifiers, modern color/value
  functions, unknown safe at-rules, malformed syntax, and line/column diagnostics; and
- development and production names, deterministic rebuilds, v1/v2 reader behavior, source maps,
  redaction, and no-runtime-compile enforcement.

The historical regressions are explicit: `@import "theme.css"` must not discover `css` as a class;
an authored `@layer components` must not accidentally become `components.components`; animation
rewriting must use grammar rather than whitespace; and syntax inside strings/comments/URLs must
never be rewritten.

## Token, theme, and color fixtures

1. Record every public 0.58 custom property and its 0.59 canonical/alias disposition.
2. Compare built-in and generated theme values in light, dark, explicit-light, explicit-dark, and
   system-mode cases.
3. Verify that no selected variant produces exactly the 0.58 base behavior.
4. Select each locked Theme variant through the public explicit marker and verify nesting,
   precedence, fragment replacement, unknown-value diagnostics, and ejection.
5. Compile equivalent hex, RGB, HSL, HWB, Lab/LCH, and OKLab/OKLCH absolute brand inputs; record
   normalization, sRGB fallback, gamut mapping, contrast/focus adjustments, and stable digests.
6. Reject context-dependent, relative, variable, URL, system, malformed, and out-of-budget brand
   inputs.
7. Force `@property`, `light-dark()`, and wide-gamut support on/off and compare final semantic
   tokens and static reduced-motion behavior.
8. Verify that local static/variable fonts retain asset, license, preload, fallback, and CSP policy;
   remote-font convenience remains absent.

## Layout, content, overlay, and media fixtures

1. Existing responsive maps retain viewport semantics and 0.58 computed layouts.
2. New explicit query containers cover unnamed/named/nested containers, base/sm/md/lg thresholds,
   fragment swaps, containment side effects, and feature-off fallback.
3. Grid/FormGrid with and without subgrid preserve DOM order, labels, focus order, width, overflow,
   and complete-content access.
4. LTR, RTL, mixed bidirectional text, selected vertical writing, physical exceptions, narrow
   viewport, 200% zoom, and text-spacing override produce reviewed facts.
5. Intrinsic sizing, dynamic viewport units, safe areas, aspect ratio, balanced/pretty text,
   hyphenation, unbroken text, code, and line clamp retain usable fallbacks.
6. Popover/dialog/menu/help placement runs with anchor positioning enabled and disabled, keyboard
   only, touch/coarse pointer, hover/no-hover, no script, clipped/scrolling ancestors, and all
   logical edges.
7. Starting/discrete/view transitions run enabled/disabled and under reduced motion; focus,
   history, title, HTMX swap, server state, and final DOM remain canonical.
8. Print fixtures render actual artifacts for shell, links, forms, tables, statuses, process flows,
   disclosures, long content, page breaks, and interactive-only chrome.
9. Preference media cover forced colors, reduced motion, contrast, transparency, pointer, hover,
   and static non-color/non-motion state.
10. Content containment runs enabled/disabled with focus, find-in-page, print, AT tree, scroll, and
    benchmark comparisons.

## Consumer vertical slices

The target fixtures reproduce the current Data Mover use cases from
`eddiethedean/user-token-management-app`:

1. **Issue #4:** typed Button and LinkButton forward accepted `id`, `title`, ARIA, data, approved
   HTMX, and Hedron dialog-trigger attributes to the correct native element; event handlers, inline
   style, unsafe URLs, malformed ARIA, and disallowed HTMX values reject.
2. **Issue #5:** small/compact Button and LinkButton plus full-width Button/LinkButton share
   documented line-height, padding, focus, disabled, icon, and responsive behavior without source
   app selectors.
3. **Issue #6:** typed brand mark/product/subtitle/home link, account identity plus sign-out form
   action, footer content, banners, and navigation compose both authenticated and login/register
   shells with valid landmarks and responsive behavior.
4. **Issue #7:** source/destination nodes, metadata slots, horizontal/vertical connectors,
   ready/blocked/running/succeeded/failed states, progress, run status/log, and compact history use
   provider-neutral Hedron primitives/recipes with animation enabled and reduced/absent.

For each slice, preserve forms, methods, CSRF, HTMX targets/swaps, dialog operation, routes,
authorization, state, accessible names, announcements, provider metadata, and full content. The
source application's identified bespoke CSS/native-control workaround is removed in a reviewable
fixture branch or patch. Hedron does not absorb transfer execution or domain policy.

## Rollback and ejection

Fixtures remove every new finite option and recover the 0.58-compatible path. Ejected output for a
theme/variant, container layout, recipe/context, control, shell, pipeline surface, overlay, and
whole design uses only public APIs/markers/tokens/scoped CSS, has source maps, refuses overwrite by
default, and passes behavioral/visual parity.

Applications may pin 0.58 or disable default styles without deleting generated files, adding Node,
fetching remote assets, or accepting runtime CSS. Compatibility diagnostics are deterministic and
redacted.
