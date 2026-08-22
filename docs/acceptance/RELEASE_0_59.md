# Phase 0.59 acceptance plan — modern CSS platform

**State:** Stage 1 entry packet locked; runtime implementation and release gates remain in progress.
**Baseline:** Published/Verified in-tree `v0.58.1`; public upgrade source PyPI `v0.58.0`.
**Target:** `v0.59.0`.
**Authority:** RFC-0087 / D-106 / D-107 / `modern-css-*-059.toml` /
`modern-css-contract-059.toml` / `release-gate-0.59.toml`.
**Execution plan:** [`../implementation/EXECUTION_0_59.md`](../implementation/EXECUTION_0_59.md).

## Outcome

An ordinary Hedron application can ship polished controls, branded authenticated or unauthenticated
shells, container-responsive layouts, forms/data/workflows, overlays, print, international text,
and preference-aware presentation without application CSS. An advanced component author can use
modern standards-based CSS—nesting, conditional rules, container queries, modern colors, and safe
progressive enhancements—through the same scoped compiler, manifest, cascade, assets, and CSP
authority.

The phase evolves the shipped 0.58 system. It does not create a second theme registry, CSS runtime,
Python property DSL, mandatory Node pipeline, private-selector theming system, or styling-owned
behavior/state.

## Stage 1 entry checklist

Stage 1 implementation may begin only after all of the following are recorded:

- D-107 is accepted and `modern-css-contract-059.toml` is the contract authority;
- exact public signatures, finite values, markers, diagnostics, schemas, browser revisions, and
  package dispositions are locked in machine-readable inventories;
- a parser/tokenizer prototype passes the import, layer, nesting, animation, URL, source-location,
  and v1 compatibility probes;
- browser capability probes assign every feature row to Required, Progressive, Experimental, or
  Deferred;
- explicit-set tracking proves whether field/layout recipes can preserve 0.58 constructor behavior;
- a scoped-default prototype proves static impact explanation and no hidden component mutation, or
  the feature is re-homed before implementation;
- a Hedron umbrella issue and workstream mirrors link back to all four source-app issues;
- the live Hedron and consumer issue audit is refreshed; and
- the raw/gzip, compile, style/layout, request, and zero-required-JS budgets are reproducible.

## Workstream order

1. **W0 — contract and probes:** freeze the feature matrix, browser floors, issue mirrors, exact
   APIs, diagnostics, compatibility aliases, schemas, and benchmark methods.
2. **W1 — compiler foundation:** implement the grammar-aware scoped transform, bounded local
   imports/assets, source maps, v2 manifests, v1 readers, and fuzz corpus.
3. **W2 — cascade/default CSS:** modularize source, normalize layers/specificity, generate one
   deterministic asset, deduplicate selector matrices, and preserve the public ABI.
4. **W3 — tokens/color/type:** canonicalize tokens with aliases, emit Theme variants, parse modern
   absolute colors with sRGB fallbacks, and complete typography/local-font contracts.
5. **W4 — responsive layout:** add explicit query containers, container-context responsive maps,
   intrinsic sizing, subgrid fallback, logical layout, RTL, and writing-mode evidence.
6. **W5 — overlays/motion:** add finite logical placement, anchor fallback, entry/exit and view
   transition enhancement, and reduced-motion/static equivalence.
7. **W6 — controls:** close user-token-management-app #4 and #5 through safe typed attributes and
   complete Button/LinkButton size/width parity.
8. **W7 — shell chrome:** close source issue #6 through typed brand/account-action/footer slots and
   container-responsive authenticated/unauthenticated composition.
9. **W8 — workflow presentation:** close source issue #7 through provider-neutral pipeline nodes,
   connectors, run states, logs, history, responsive orientation, and reduced-motion behavior.
10. **W9 — contextual styling:** graduate only the recipe/scope features proven explicit,
    serializable, inspectable, and behavior-neutral.
11. **W10 — media/a11y:** land real print CSS and whole-fleet preference, direction, zoom, content,
    no-script, keyboard, focus, and fragment evidence.
12. **W11 — tooling/migration:** extend explain/check/preview/diff/eject and Explorer; add diagnostics,
    compatibility reports, reviewable codemods, and the single learning ladder.
13. **W12 — fleet/cut:** migrate packages and examples, validate the consumer app, enforce budgets,
    run regression/package rehearsals, refresh issue state, and publish honest release evidence.

W1 is the critical predecessor for advanced authoring. W2–W5 may proceed in parallel after W0/W1
contracts stabilize. W6–W8 can begin against W0 component contracts and integrate with W2–W5 as
those foundations land. W9 cannot precede its explicitness prototype. W10–W12 run continuously but
close last.

## Planned release gates

| Gate | Required evidence |
|---|---|
| `CONTRACT-059` | Exact APIs, finite values, feature tiers, browser floors, schemas, diagnostics, issue mirrors, package dispositions, and budget methods |
| `COMPILER-059` | Grammar-aware nesting/selectors/at-rules/declarations/descriptors/custom identifiers; local imports; line/column diagnostics; v2 manifest/source map; v1 compatibility |
| `CASCADE-059` | Fixed layers, authored sublayer behavior, specificity ceiling, public selector ABI, deterministic generated asset, and no source-order accident |
| `TOKENS-059` | Canonical semantic namespace, 0.58 aliases, Theme variant emission, explicit precedence, typed-property fallbacks, and fleet consumption |
| `COLOR-059` | Parsed absolute modern color inputs, sRGB/wide-gamut output, deterministic gamut mapping, contrast/focus adjustments, and palette-v2 provenance |
| `CONTAINER-059` | Explicit query boundaries, named thresholds, nested/unnamed behavior, feature-off fallback, fragment parity, and no accidental containment |
| `LAYOUT-059` | Container/viewport responsive layouts, intrinsic sizing, subgrid fallback, logical properties, RTL/writing modes, narrow viewport, and full-content paths |
| `TYPE-059` | Typography roles, international wrapping/hyphenation, code/prose overflow, fluid sizing, variable/local fonts, metrics fallback, and no remote convenience |
| `CONTROL-059` | Safe typed-control attributes and complete Button/LinkButton size/width/focus/disabled/icon/responsive parity; source issues #4/#5 criteria |
| `CHROME-059` | Typed brand/account-action/footer/auth-state shell composition, correct landmarks/forms, container behavior, and source issue #6 criteria |
| `WORKFLOW-059` | Provider-neutral pipeline nodes/connectors/states/log/history, horizontal/vertical layout, static/reduced-motion parity, and source issue #7 criteria |
| `OVERLAY-059` | Native popover/dialog/top-layer behavior, finite logical placement, anchor feature-on/off collision fallback, keyboard/focus, and no-script/static path |
| `MOTION-059` | Motion presets, starting/discrete/view transition feature-on/off, reduced motion, canonical navigation/state, and Experimental scroll-animation isolation |
| `MEDIA-059` | Real print rules; preference media; LTR/RTL/vertical writing; zoom/text spacing; long/unbroken/international content; no-script output |
| `A11Y-059` | Semantics, keyboard, focus visibility/obscuration, announcements, reflow, non-color state, complete-content path, fallback parity, and honest #86 limits |
| `DX-059` | One authoring ladder; source-located diagnostics; explain/check/preview/diff/eject; Explorer provenance; no-overwrite migration; advanced modern-CSS examples |
| `VISUAL-059` | Three-engine DOM/computed-style/pixel gallery across modes, directions, zoom, content, viewport/container sizes, feature on/off, and reviewed-delta policy |
| `PERF-059` | ≤90,000 raw and ≤13,000 gzip default CSS; zero required styling JS; zero extra Required stylesheet request; compile/style-layout ratio budgets |
| `SECURITY-059` | CSS/parser/import/URL/asset/passthrough fuzzing, strict `style-src 'self'`, redacted manifests/maps/tooling, deterministic builds, and no runtime injection |
| `COMPAT-059` | Public and in-tree 0.58 upgrade sources, API/DOM/marker/token/theme/style-contract/default-styles/compiler-manifest compatibility, aliases, and rollback |
| `CONSUMER-059` | Reproducible Data Mover before/after migration proving all four consumer issue acceptance criteria and removing the identified workarounds |
| `REGRESS-059` | Full fleet suites plus closed 0.57/0.58 styling issue contracts and feature-off/no-CSS/no-JS regressions remain green |
| `PKG-059` | Clean wheels, pure-Python Supported compiler path, lazy optional assets/deps, licenses, exports/docs, reproducible build, metadata, and release rehearsal |

## Required consumer issue closure

| Source issue | Phase result | Closing gates |
|---|---|---|
| [user-token-management-app #4](https://github.com/eddiethedean/user-token-management-app/issues/4) | Typed Button/LinkButton express the current HTMX/dialog/global/ARIA/data cases through a safe validated contract | `CONTROL-059`, `SECURITY-059`, `COMPAT-059`, `CONSUMER-059` |
| [#5](https://github.com/eddiethedean/user-token-management-app/issues/5) | Small/compact and full-width actions need no app selector; Button/LinkButton visual semantics agree | `CONTROL-059`, `CASCADE-059`, `VISUAL-059`, `CONSUMER-059` |
| [#6](https://github.com/eddiethedean/user-token-management-app/issues/6) | Brand, account action/form, footer, and auth-state shell are typed, responsive, and landmark-correct | `CHROME-059`, `CONTAINER-059`, `A11Y-059`, `CONSUMER-059` |
| [#7](https://github.com/eddiethedean/user-token-management-app/issues/7) | Pipeline/connector/run-state/log/history presentation is provider-neutral, responsive, themed, and reduced-motion safe | `WORKFLOW-059`, `MOTION-059`, `A11Y-059`, `VISUAL-059`, `CONSUMER-059` |

Issues stay open until both Hedron evidence and the source-app migration pass. A Hedron mirror does
not replace the source issue, and issue closure without gate evidence does not satisfy the phase.

## Required evidence matrix

The gallery and browser suites cross these dimensions where applicable:

- Chromium, Firefox, WebKit;
- feature native/enabled and fallback/disabled;
- default, Aurora, generated brand, inherited theme, and selected variant;
- light, dark, forced colors, reduced motion, contrast, transparency, and print;
- LTR, RTL, mixed direction, and selected vertical writing;
- 320/360/768/1440 CSS-pixel viewport widths plus named container widths;
- 100% and 200% zoom, default and WCAG text-spacing override;
- keyboard, pointer, touch/coarse pointer, hover and no-hover;
- short, long, international, bidirectional, unbroken, empty, loading, error, and dense content;
- full navigation, HTMX fragment replacement, no script, and default-styles disabled; and
- zero application component/layout CSS for the representative gallery.

Print artifacts are rendered and inspected, not inferred from a media-mode flag. Progressive
features require separate fallback assertions rather than one snapshot from a supporting browser.

## Compatibility and rollback

The source corpus begins at public `v0.58.0` and living in-tree `v0.58.1`. Existing component calls,
theme selection, DesignSystem/recipes/scopes, public markers/classes/tokens, style contracts,
component stylesheets, StyleSymbols, manifests, default CSS behavior, and `default_styles=False`
remain runnable. New container behavior and variants are opt-in. Token aliases remain through the
0.59 line. Compiler v2 reads v1 manifests and preserves symbol hashing unless an accepted security/
collision exception supplies a migration map.

Rollback is application-local: remove new finite options or pin 0.58; no generated source is
silently overwritten, and no migration requires deleting application CSS.

## Non-goals

The release does not add a free-form CSS-in-Python API, utility-string framework, second compiler/
cascade/theme registry, runtime style injector, mandatory Node build, automatic remote font/assets,
closed Shadow-DOM rewrite, visual DOM reordering, behavior/state authority, universal design
builder, CSS masonry/worklet dependency, automatic application-CSS conversion, human-AT Supported
claim, or Hedron 1.0 schedule.

## Exit condition

The cut requires a satisfied Stage 1 entry lock, all 23 release rows Verified with zero Deferred,
all four consumer issues validated and closed, a refreshed live issue audit, compiler/cascade/token/
layout/media/security compatibility proof, three-engine feature-on/off evidence, the expanded
zero-application-CSS gallery, passing size/performance budgets, clean packages, and release docs
that clearly distinguish Required, Progressive, Experimental, and Deferred capabilities.
