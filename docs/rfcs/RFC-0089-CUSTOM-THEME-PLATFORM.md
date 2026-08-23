# RFC-0089: Custom theme platform and styling completion

**Status:** Draft
**Phase:** 0.60
**Planning baseline:** Published/Verified in-tree `v0.59.0`
**Public upgrade source:** PyPI `v0.59.0`
**Target:** `v0.60.0`
**Decision:** Proposed D-108
**Contract:** [`theme-platform-contract-060.toml`](../acceptance/theme-platform-contract-060.toml)

## Summary

Phase 0.60 turns Hedron's shipped styling foundation into a complete custom-theme platform. A
theme author can start from a built-in theme or modern color seed, build a finite design system,
validate every semantic and component state, package it, preview and diff it, select it without
flash, and apply bounded recipe defaults without application CSS or a second styling runtime.

The phase also closes the nine Hedron styling issues opened after the 0.59 cut:

- [#627](https://github.com/eddiethedean/hedron/issues/627) — Brand subtitle layout;
- [#628](https://github.com/eddiethedean/hedron/issues/628) — ToastHost placement and error-host composition;
- [#629](https://github.com/eddiethedean/hedron/issues/629) — themed ConnectorFlow canvas;
- [#630](https://github.com/eddiethedean/hedron/issues/630) — bounded semantic ScrollRegion;
- [#631](https://github.com/eddiethedean/hedron/issues/631) — explicit scoped recipe defaults;
- [#632](https://github.com/eddiethedean/hedron/issues/632) — extensible typed recipe families;
- [#633](https://github.com/eddiethedean/hedron/issues/633) — modern color input for `DesignSystem.brand`;
- [#634](https://github.com/eddiethedean/hedron/issues/634) — forced-colors and contrast-preference theme modes; and
- [#635](https://github.com/eddiethedean/hedron/issues/635) — persisted no-flash theme selection.

0.60 retains one authority chain:

```text
Color / ThemeSpec / ThemeBuilder / ThemePatch / ThemePackage
  -> Theme / DesignSystem / recipes
  -> validation plan and registered tokens
  -> existing markers, cascade, compiler, and assets
  -> server-first preference resolution and optional no-flash helper
```

## Problem

0.58 introduced `DesignSystem`, recipes, and explicit `StyleScope`; 0.59 modernized the CSS and
component presentation platform. The result is capable but incomplete as a theme-authoring
product:

- `DesignSystem.brand` still normalizes only 3/6-digit hexadecimal input even though the 0.59
  public contract describes absolute CSS Color 4 input;
- `Theme` has no first-class accessibility-mode authoring contract and emits only light/dark mode;
- recipes are closed global maps and `StyleScope` explicitly rejects recipe defaults;
- custom themes lack one portable package, compatibility, asset, validation, and provenance schema;
- current checking is token/contrast oriented rather than a complete component-state matrix;
- custom-theme selection requires application-owned allowlisting, persistence, and boot behavior;
- Brand, toast hosting, workflow canvases, and semantic logs still require consumer CSS; and
- release evidence can pass while testing only marker presence rather than the advertised visual
  or color-input behavior.

Treating these as isolated props would leave theme creation fragmented. The phase therefore owns
the full lifecycle and uses the nine issues as vertical acceptance fixtures.

## Goals

1. Make custom theme creation typed, deterministic, inspectable, and approachable.
2. Accept safe absolute modern colors with canonical sRGB fallback and palette-v2 provenance.
3. Validate registry-derived component contracts, declared coverage profiles, structural
   integrity, semantic relationships, contrast, focus, component states, accessibility modes,
   assets, browser fallbacks, and package compatibility.
4. Support distributable, locally resolved theme packages without remote-code or CSS authority.
5. Add extensible presentation-only recipe families and explicit scoped defaults with exact
   precedence and static impact explanation.
6. Provide server-first theme preference resolution, progressive no-JavaScript forms, and an
   optional CSP-safe no-flash path.
7. Close every 0.60-owned styling issue with zero-application-CSS browser fixtures.
8. Repair release-evidence gaps by requiring behavior and computed-style assertions in addition to
   marker/string assertions.
9. Make theme composition, compilation, and third-party conformance reproducible through bounded
   overlays, provenance graphs, deterministic fingerprints, and a portable conformance kit.

## Non-goals

- a general CSS-in-Python property language or utility-class framework;
- arbitrary selectors, declarations, URLs, remote fonts, or remote theme execution;
- a second registry, compiler, cascade, stylesheet runtime, or client-side design authority;
- recipes that change workflow state, route, effect, authorization, visibility, DOM order, or
  accessible semantics;
- Hedron-owned users, sessions, databases, preference authorization, or synchronization service;
- a drag-and-drop theme editor or mandatory browser/Node build;
- automatic aesthetic or accessibility fixes, a single aggregate "theme health" score, or a claim
  that passing automation certifies a theme;
- round-trip external design-token interchange, AI palette generation, or remote theme discovery;
- an accessibility certification claim generated from automated validation; or
- removal of `Theme`, `DesignSystem`, `default`, `aurora`, hexadecimal seeds, explicit component
  props, component `styles.css`, or `default_styles=False`.

## Proposed design

### Theme authoring ladder

Documentation and tooling teach one progression:

1. select a reviewed built-in theme;
2. compile a brand theme from a typed color;
3. refine finite geometry, type, density, elevation, motion, and navigation groups;
4. provide explicit semantic/component tokens where expert control is needed;
5. add named presentation-only recipes and an explicit style context;
6. run `theme check`, preview the whole state matrix, and inspect adjustments;
7. diff and package the validated theme; and
8. register and select it through a server-authoritative preference boundary.

Every step produces the same `Theme`/`DesignSystem` authority and can be explained or ejected.

### Typed colors and palette compilation (#633)

Add an immutable `Color` value with bounded constructors and parsing:

```python
Color.parse("oklch(68% 0.18 275)")
Color.oklch(0.68, 0.18, 275)
DesignSystem.brand("acme", accent=Color.oklch(0.68, 0.18, 275))
```

The Supported grammar includes canonical hex, `rgb()`/`rgba()`, `hsl()`/`hsla()`, `hwb()`, Lab/
LCH, and OKLab/OKLCH absolute values. Context-dependent values, relative colors, `var()`, URLs,
system colors, `currentColor`, device profiles not explicitly admitted by the contract, and
selector/declaration syntax reject.

Compilation records original space/value, normalized XYZ/OKLCH working values, gamut mapping,
canonical sRGB fallback, optional wide-gamut enhancement, contrast/focus adjustment, and the
algorithm revision in `hedron.brand-palette/2`. Existing string hex calls remain byte-compatible.

### ThemeSpec, ThemeBuilder, token graphs, and overlays

Add an immutable, serializable `ThemeSpec` as the canonical authoring input. It records finite
groups, explicit semantic tokens, structured token aliases, accessibility maps, declared coverage
profiles, and source provenance. Aliases form a bounded directed graph with missing-reference and
cycle detection; arbitrary `var()` expressions remain rejected. The resolved graph can explain
which base, alias, or overlay supplied every value.

`ThemeBuilder` is a convenience facade over `ThemeSpec`, not a separate authority and not the only
construction path:

```python
spec = (
    ThemeBuilder("acme", base=aurora_theme())
    .brand(accent=Color.oklch(0.68, 0.18, 275))
    .groups(density="comfortable", geometry="soft", typography="system-sans")
    .tokens({"color.info": "#2563eb"})
    .accessibility_mode("more-contrast", {"border.strong": "CanvasText"})
    .build_spec()
)
```

The builder accepts finite groups and validated semantic tokens only. Expert authors may construct
an explicit `ThemeSpec` or `Theme` directly; validation and packaging normalize all paths through
the same specification and resolver. Builder operations are pure and retain field-level
provenance.

`ThemePatch` provides a bounded overlay for tenant, product, sub-brand, or event customization.
Patches may override only registered theme fields and semantic tokens, declare their compatible
base/fingerprint, retain layer provenance, and trigger complete revalidation. Composition order is
explicit and deterministic; patches cannot add selectors, arbitrary declarations, behavior, or
remote assets.

Compilation emits a stable fingerprint over the canonical `ThemeSpec`, ordered patches, compiler
algorithm revisions, and Hedron compatibility identity. Identical inputs must produce identical
resolved graphs, CSS, reports, and package digests; CI treats unexpected drift as a failure.

### Accessibility modes (#634)

`Theme.accessibility_modes` is separate from selected light/dark mode. Initial mode IDs are
`forced-colors` and `more-contrast`. Values are bounded semantic-token remaps and reviewed
component-state mappings, not arbitrary CSS.

Hedron owns the media queries and `forced-color-adjust` policy. Forced colors default to user-agent
system colors; theme input may distinguish focus, border, selected, disabled, status, and
non-text affordances only through allowed semantic roles. Validation detects contradictory tokens,
color-only state, invisible focus, and opted-in incomplete matrices. Unsupported preference media
falls back to the base theme.

### Theme validation and reports

`validate_theme()` and `ThemeValidator` produce the same immutable `ThemeValidationReport` with
schema `hedron.theme-validation/1`. Every themeable component registers one immutable
`ComponentThemeContract` before registry seal. The contract declares required semantic roles,
public parts, states, variants, contrast relationships, accessibility-mode behavior, and fallback
policy. Validation inventories these contracts from the existing registry rather than a
handwritten fleet list, and fails if a public component is unregistered or the two diverge.

Themes declare a coverage profile: `core`, `forms`, `data`, `workflow`, or `complete`. Profiles are
monotonic reviewed sets of component contracts; package metadata and user-facing claims must name
the validated profile. A limited-profile theme is valid for that profile but cannot claim whole-
fleet support. Every first-party built-in must validate as `complete`.

Validation has seven layers:

1. structure and safe values;
2. semantic required/optional token coverage;
3. recipe/family/component compatibility and inheritance;
4. registry-derived component contracts and declared profile coverage;
5. light/dark/accessibility state contrast and non-color affordances;
6. asset, CSP, package, and browser-fallback policy; and
7. applicable-profile DOM/computed-style/visual matrix evidence.

Diagnostics have stable codes, severity, token/component/state/mode context, requested and resolved
values, graph/patch provenance, and remediation. Contrast checks consume registered relationships
such as text/surface, selected foreground/background, focus/surrounding colors, border/surface,
status, and disabled-state cues rather than inspecting colors in isolation. Diagnostics may preview
candidate remediations, but `check` never silently adjusts and `--fix` is limited to canonical
formatting. Brand compilation may adjust within the locked algorithm but must disclose every
change before a theme can package. Results remain categorical; no aggregate score can conceal a
critical error.

### Theme packages and catalog

`ThemePackage` is data plus declared local assets, not executable plugin code. Its manifest
`hedron.theme-package/1` contains package/name/version, Hedron compatibility range, ThemeSpecs,
optional ThemePatches, declared coverage profiles, design-system plans, recipe families, recipes,
local font/image assets with hashes/licenses, validation/fingerprint digests, and optional preview
metadata.

Registration is deterministic, namespace-safe, deny-by-default on conflicts, and sealed with the
existing registry lifecycle. Package loading cannot fetch remote resources, execute source, alter
security policy, or register behavior. A theme remains usable directly without packaging.

The built-in catalog retains `default` and `aurora` and adds no more than three carefully reviewed
theme families in 0.60. Candidate names and visuals are not public until the W0 design review locks
them; platform completeness takes priority over catalog size, and every accepted built-in must
cover light/dark, accessibility modes, the complete fleet, and local asset licensing.

### Theme lifecycle and conformance

Theme/package metadata declares Hedron compatibility, ThemeSpec/report schema support, validated
profiles, and compiler fingerprint inputs. Token, component-contract, and profile changes follow a
documented lifecycle: additive warning first, stable migration/rename map, compatibility window,
then an announced error boundary. Strict validation may adopt new requirements early; compatibility
validation never silently upgrades a package's coverage claim.

The third-party conformance kit generates a zero-application-CSS fixture for the package's declared
profile, renders its registered parts/states/modes, and emits portable JSON plus human-readable
artifacts. Package publication requires a freshly generated report whose registry inventory and
fingerprint match the packaged inputs.

### Extensible recipes and scoped defaults (#631, #632)

Add immutable `RecipeFamily` registration with safe identifiers, finite field vocabularies, and
per-component field bindings. A family field must bind to an existing component presentation prop
or a separately registered public presentation field. Family registration cannot create new CSS
properties or target private selectors.

The issue #632 example's `state` field is explicitly excluded: connector/workflow state is
authoritative application input, not a recipe value. Flow recipes may set presentation such as
appearance, density, background treatment, track treatment, spacing, or emphasis.

`StyleContext` maps public family/semantic roles to registered recipes. `StyleScope(context=...)`
applies it to one visible subtree. Implementation first establishes explicit-authored-value
tracking; explicit component props win, then nested scope context, then outer context, then design
defaults, then component defaults. A static explanation enumerates every affected component role.

Fragment swaps inherit their DOM scope. OOB/overlay hosts outside that subtree require an explicit
context reference or host binding; no ambient process-global mutation is permitted.

### Theme preference and no-flash boot (#635)

`ThemePreference` contains an allowlisted registered theme name and `system|light|dark` color mode.
Applications resolve it from their cookie/session/account boundary and pass the result into page
rendering. Invalid, missing, stale, or unauthorized values fail to an application-selected safe
default.

`ThemePicker` is an accessible ordinary form with optional HTMX enhancement. Hedron documents a
persistence adapter protocol but owns no storage. The server-rendered `<html>` attributes are the
canonical no-flash path. An optional small external, CSP-safe boot asset may read only the bounded
Hedron preference cookie/local record, validate it against server-emitted allowed values, and set
the initial markers before stylesheet evaluation. History restoration, fragments, dialogs, OOB
hosts, and multi-tab changes receive browser coverage.

### Theme Lab and author assistance

Explorer exposes a read-only Theme Lab backed by the same resolver and validator. It supports
side-by-side light/dark/contrast/forced-color rendering, token and component-state inspection,
ThemeSpec/patch diffs, gamut and fallback warnings, keyboard/focus/zoom exercises, and exportable
validation artifacts. It does not execute package code, write target projects, or become a runtime
design authority.

External token-format import, additional built-in families beyond the reviewed cap, automatic
palette suggestions, a visual editor, and remote distribution remain stretch/deferred work. Any
future importer is one-way and experimental until a separately accepted compatibility contract can
prove more; 0.60 makes no round-trip interchange claim.

### Zero-CSS component completion (#627–#630)

- `Brand` gains native stacked copy, safe min sizing, subtitle overflow/density markers and tokens.
  `AppShell.brand` continues accepting arbitrary `NodeLike`; `Brand` itself keeps its current name/
  subtitle constructor contract.
- `ToastHost` gains logical fixed/sticky placement, safe-area insets, width, gap, layer, and narrow-
  viewport behavior while preserving `#hedron-toast`. Announcement ownership is normalized so
  nested live regions do not double-announce. A separate typed error/alert host is admitted only if
  the semantics cannot be expressed safely by the toast host.
- `ConnectorFlow` gains surface-aligned appearance, density, decorative background, overflow, and
  minimum-size intent. Decoration is non-semantic and suppressed in forced colors and print.
- `ScrollRegion` bounds semantic lists/logs/arbitrary children without changing child semantics.
  Axis, size, affordance, and accessible name are finite; focusability is conditional rather than
  unconditional. Print removes clipping and exposes complete content.

## Compatibility

- Existing constructors and default rendering remain accepted.
- `default` and `aurora` keep their names and compatibility snapshots.
- Hexadecimal `DesignSystem.brand` inputs retain normalized output unless a documented contrast
  defect requires a disclosed correction.
- `Theme`, `DesignSystem`, built-in recipes, `DesignSystem.apply`, and existing `StyleScope` calls
  remain valid.
- Theme package/report/palette readers accept the immediately preceding schema where one exists.
- ThemeSpec, patch, profile, component-contract, and fingerprint compatibility follows the
  documented warning/migration/error lifecycle; a package never gains a broader profile silently.
- New placement, context, picker, canvas, and scroll behavior is additive; defaults that materially
  alter shipped layout require explicit compatibility fixtures and release notes.

## Security and trust

All external strings are untrusted. Color, theme, recipe, package, asset, preference, and marker
inputs are bounded before serialization. Theme packages are data-only, paths stay under registered
roots, digests are verified, remote assets/imports reject, diagnostic reports redact absolute paths
and environment data, and no request-provided name becomes a selector or registry lookup without
allowlist validation.

## Accessibility evidence

The whole-fleet matrix crosses theme, light/dark, forced colors, increased contrast, reduced motion,
print, LTR/RTL, narrow reflow, 200%/400% zoom, increased text spacing, long/international content,
keyboard, focus, announcements, and feature-off fallbacks. Automated checks inform but never
replace manual visual review or the bounded human-AT claim governed by #86.

## Delivery and gates

The normative workstream sequence is in
[`THEME_PLATFORM_060.md`](../implementation/THEME_PLATFORM_060.md); execution milestones are in
[`EXECUTION_0_60.md`](../implementation/EXECUTION_0_60.md). Release requires every row in
[`release-gate-0.60.toml`](../acceptance/release-gate-0.60.toml) Verified, all nine owned issues
closed from behavior evidence, zero unowned styling issues, passing upgrade sources, and no
unsupported accessibility or release claim.
