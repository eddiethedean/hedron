# Phase 0.65 refined scope and definition of done

Status: **Implemented; release candidate**. This document records the bounded release cut
so implementation can proceed without turning every missing styling idea into an unbounded theme
project.

Authority: [RFC-0092](../rfcs/RFC-0092-INTEGRATED-STYLING-PLATFORM.md),
[APPLICATION_STYLING_065](../implementation/APPLICATION_STYLING_065.md), and
[RELEASE_0_65](RELEASE_0_65.md).

## Release cut

The Required 0.65 cut has three layers of responsibility:

1. **Integration foundation:** declared local CSS assets, the `application` cascade layer,
   public hook metadata, namespaced tokens, static diagnostics, and provenance-preserving ejection.
2. **Four issue verticals:** the exact motion, public parts/state, data-view, and native
   control slices listed below.
3. **Cross-cutting safety:** every touched surface has keyboard/focus, forced-colors/high-contrast,
   reduced-motion, print, responsive/RTL where applicable, native/no-JS, and semantic fallbacks.

The cut does not promise a complete redesign of every Hedron component. A surface outside the
touched inventory is either unchanged and compatible or explicitly listed as Progressive/Deferred.

## Required issue slices

| Issue | Required named slice | Contract lock | Evidence |
|---|---|---|---|
| [#690](https://github.com/eddiethedean/hedron/issues/690) | `instant`, `standard`, `emphasized`, `reveal`, `elevate`, and `crossfade` motion presets; bounded duration/easing/distance/opacity; deterministic reduced-motion and print behavior | No arbitrary animation strings; motion cannot own state or layout | `MOTION-065` six-preset matrix, reduced-motion, print, busy/progress, performance |
| [#693](https://github.com/eddiethedean/hedron/issues/693) | `AppShell.nav.link`, `ProcessFlow.step`, `Card` content roles, `FormField` control states, and `SplitView` separator/collapse | Hook manifest is the only public selector surface; values are finite theme/recipe tokens | `HOOKS-065` + `RECIPE-065` manifest, state, forced-colors, print, responsive fixtures |
| [#694](https://github.com/eddiethedean/hedron/issues/694) | Table/data-view border/radius, header, row separator/hover/selected, numeric/code cells, sticky header, compact/spacious density | Tokens compose with TableColumn metadata and never replace semantic table markup | `DATA-065` state/density/sticky/overflow/print/forced-colors matrix |
| [#698](https://github.com/eddiethedean/hedron/issues/698) | Checkbox/radio, select, range, file, date/time, and number controls; accent/appearance policy; focus/invalid/busy/disabled/read-only/checked/selected/indeterminate | Native-first paint with a usable platform fallback; no generic input-selector contract | `CONTROLS-065` browser/platform/keyboard/touch/forced-colors matrix |
| [#712](https://github.com/eddiethedean/hedron/issues/712) | Document-level `AmbientCanvas` with ordered radial/dots/grid/mesh layers and flow/surface/fixed-canvas placement | Decorative layers are tokenized, deterministic, noninteractive, and suppressed for print, forced colors, reduced transparency, and contrast | `PRESENT-065`, `A11Y-065` ambient conformance matrix |
| [#713](https://github.com/eddiethedean/hedron/issues/713) | `AppShellChrome` presets for header/nav behavior, named sticky offsets, gap/inset, banner spacing, and density | Geometry is finite, themeable, deterministic, and has mobile/print/forced-colors/reduced-motion fallbacks | `PRESENT-065`, `REGRESS-065` shell recipe matrix |
| [#714](https://github.com/eddiethedean/hedron/issues/714) | Authoritative presentation token consumption for built-in typography, spacing, geometry, motion, data, and controls | Manifest distinguishes declared, consumed, and overridden tokens; unused public tokens fail validation | `TOKEN-065`, `PRESENT-065` token-consumption matrix |
| [#715](https://github.com/eddiethedean/hedron/issues/715) | Bounded viewport/container maximum and named between-range conditions | Compiler orders ranges deterministically and rejects contradictory or unreachable combinations | `RECIPE-065`, `A11Y-065` responsive-condition matrix |

Issue closure requires the implementation, public API/manifest, tests, and release evidence to
link back to the issue. A passing foundation gate cannot close an issue whose named slice remains
unimplemented.

## Integration contracts

| Contract | Required decision |
|---|---|
| Asset registration | `app.styles(name, source, *, scope=None, layer="application", global_=False, media=())`; local package-owned source only; no implicit discovery |
| Scope | A named scope emits a stable application scope root; selectors are checked against the registered scope and public hooks |
| Cascade | `reset < tokens < base < components < application < utilities < overrides`; application CSS overrides defaults/recipes, explicit props use the stronger explicit lanes |
| Public hooks | `data-hedron-component`, `data-hedron-part`, `data-hedron-state`, and `data-hedron-slot`; only manifest entries are stable |
| Tokens | `namespace/name`, type, default, modes, fallback, source, and provenance are required; collisions with core names reject |
| Diagnostics | Static deterministic findings include code, severity, source, selector/hook, property, layer, token, fallback, and remediation |
| Ejection | Generated blocks carry source-manifest hash, component/hook/token provenance, upstream version, and manual merge markers; update never overwrites drift |
| Safety | Remote imports, unsafe at-rules, response CSS, user-data selectors/values, behavior changes, and silent budget slicing reject |

The exact serialized fields and compatibility rules are locked in
[application-styling-contract-065.toml](application-styling-contract-065.toml).

## Progressive catalog

These recommendations remain in the phase roadmap but are not Required release blockers unless a
0.65 Required slice uses them:

| Area | Progressive outcome | Fallback in 0.65 |
|---|---|---|
| Focus/interaction expansion | Full state catalog beyond touched components | Existing focus-visible and semantic state contracts |
| Navigation and overlays | New navigation chrome, anchor positioning, and placement recipes | Existing component props and native positioning |
| Layout and density | New container/layout/touch scale catalog | Existing bounded layout and responsive conditions |
| Typography/media/icons | Product-wide text, media, icon, and asset contracts | Existing semantic props/tokens and native media behavior |
| Visualization/print/export | New visualization chrome and export themes | Existing chart/data contracts and readable print fallback |
| RTL/preferences | Full logical-property and preference-mode expansion | Required fallback checks on every 0.65-touched surface |
| Tooling | Typed selectors, Explorer cascade UI, visual regression, recipe suggestions | Static manifests and deterministic CLI diagnostics |
| Interchange | Third-party token packages and external design-token synchronization | Application-local namespaced tokens |

## Stage 0 exit checklist

- [ ] D-110 records the exact contracts above and owners for every Required gate.
- [ ] A component/part/state/slot inventory identifies the five #693 surfaces and all touched
      motion/data/control hooks.
- [ ] Browser support probes cover the native control families and motion fallbacks before API
      names are frozen.
- [ ] Baseline CSS/request/compile/layout measurements are recorded; budgets are frozen from
      measurements, not guesses.
- [ ] The application asset graph proves full-page, fragment, HTMX, CSP, package, and no-JS paths.
- [ ] The upgrade fixture proves feature-off 0.64.0/0.64.1 compatibility and explicit drift handling.
- [ ] Progressive rows have owners, fallbacks, and no implied Supported claim.

Stage 1 starts only when this checklist, the machine-readable contract, and the issue-to-gate
matrix are accepted. Stage 1 may amend a named contract only through a recorded decision; it may
not silently widen the Required cut.
