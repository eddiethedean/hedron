# RFC-0092: Integrated styling platform and application CSS

**Status:** Proposed  
**Proposed phase:** 0.65  
**Decision:** D-109  
**Stage 0 contract refine:** D-110  
**Depends on:** RFC-0006, RFC-0022, RFC-0023, RFC-0024, RFC-0057, RFC-0084, RFC-0085,
RFC-0087, RFC-0089, RFC-0090, RFC-0091

## Summary

Phase 0.65 makes application-authored CSS a first-class participant in Hedron's existing
styling authority. Themes, semantic recipes, scoped styles, and ordinary CSS become four
cooperating authoring lanes over one token, manifest, asset, and cascade system.

The phase closes the four open presentation issues from the 0.64 inventory:

- [#690](https://github.com/eddiethedean/hedron/issues/690), named motion recipes and
  reduced-motion fallbacks;
- [#693](https://github.com/eddiethedean/hedron/issues/693), bounded component-part and
  state-style recipes;
- [#694](https://github.com/eddiethedean/hedron/issues/694), semantic data-view and table
  chrome tokens; and
- [#698](https://github.com/eddiethedean/hedron/issues/698), native form-control appearance
  and state theming.

It also adds the missing integration layer for users who need normal CSS: first-class local
stylesheet registration, a documented application cascade layer, stable public component
parts/states, namespaced application tokens, style inspection, and provenance-preserving
ejection and upgrade workflows.

## Problem statement

Hedron's current styling system is strong at framework-owned defaults and bounded semantic
recipes, but the boundary for application authors is incomplete:

- users can choose component props or finite recipes, but cannot easily style a documented
  public part or state with ordinary CSS;
- application stylesheets are not represented as first-class members of the Hedron asset,
  layer, manifest, source-map, and HTMX asset graph;
- custom values can fall outside the theme/token provenance model;
- style failures are difficult to explain when layers, generated classes, tokens, and
  component state markers interact; and
- ejection gives users control but does not yet provide a durable upstream-diff and
  provenance workflow.

The answer is not a second CSS-in-Python language or a client styling runtime. The answer is
to make ordinary CSS observable, scoped where requested, layered predictably, and connected to
the same public metadata that powers recipes and built-in styles.

## Design principles

1. **One styling authority.** Theme resolution, token provenance, component hooks, CSS assets,
   cascade layers, diagnostics, and ejection consume one registry-derived representation.
2. **Ordinary CSS remains valid.** Applications may write standard local CSS, including normal
   selectors and media/container queries within the declared asset policy.
3. **Public hooks are stable; private classes are not.** Parts and states are documented
   contract surface. Generated class names and DOM descendants remain implementation details.
4. **Progressive authoring remains progressive.** Props and recipes are the easiest path;
   ordinary CSS is the expressive path; ejection is the escape hatch.
5. **Safety is explicit.** Local CSS is supported; remote resources, response CSS, inline
   executable content, unsafe URLs, and unbounded runtime values remain rejected or opt-in
   Experimental surfaces.
6. **CSS cannot own behavior.** Styling never changes routes, authorization, state authority,
   DOM order, accessible names, mutation meaning, or server fallbacks.
7. **Fallbacks are part of the contract.** Print, forced-colors, high contrast, reduced motion,
   reduced transparency, narrow widths, coarse pointers, and no-JavaScript paths are designed,
   not implied.
8. **Build-time first.** Production consumes deterministic, fingerprinted assets and manifests;
   runtime CSS compilation is not required.

## Four authoring lanes

| Lane | Best for | Authority | Contract |
|---|---|---|---|
| Semantic props | Common built-in intent | Component API | Finite values and safe defaults |
| Theme and recipes | Product-wide visual language | ThemeSpec / StyleRecipe | Tokens, roles, states, modes, fallbacks |
| Application CSS | Product-specific composition and detail | Registered local stylesheet | Ordinary CSS, explicit layer, public hooks |
| Ejection | Deep first-party customization | Ejected source with provenance | Upgrade diff, source map, compatibility report |

No lane silently changes the authority of another lane. Explicit component props remain stronger
than styling defaults; application CSS may override presentation but not behavior or semantics.

## Proposed contract

The exact Python names are frozen by D-110. The intended contract is:

### First-class application stylesheets

Applications register local CSS through the asset pipeline, conceptually:

```python
app.styles(
    "application",
    "styles/app.css",
    layer="application",
    scope="app",
)
```

The registered asset participates in development reload, production fingerprinting, CSP,
source maps, build manifests, HTMX fragment/page asset planning, and clean-package checks.
Registration metadata declares:

- a stable logical name and local source root;
- the cascade layer and optional scope root;
- declared theme/token dependencies;
- media and container conditions used by the bundle;
- whether global selectors are permitted; and
- package/source provenance.

The phase does not require a Node or npm build. Hedron's existing CSS compiler and asset
pipeline remain the pure-Python reference authority.

### Public parts and states

Supported components publish a stable manifest and emit documented hooks, conceptually:

```html
<nav data-hedron-component="AppShell"
     data-hedron-part="nav-link"
     data-hedron-state="current">
```

The manifest records component identity, public parts, public states, slots, required fallback
behavior, maturity, and the owning package. Private descendants and generated classes are not
promoted by observation alone.

### Application tokens

Applications may register namespaced semantic tokens in the existing theme graph:

```python
ThemeBuilder("acme") \
    .token("app.sidebar.width", "18rem") \
    .token("app.workspace.gap", "1.25rem")
```

Application tokens receive deterministic names, light/dark and accessibility overrides where
declared, fallback values, provenance, export entries, and conformance checks. Runtime data
cannot become CSS; dynamic values still require validated, bounded CSS-variable paths.

### Cascade layers

The phase freezes an application layer in the existing cascade order:

```css
@layer reset, tokens, base, components, application, utilities, overrides;
```

`application` is the normal user layer. `overrides` is an explicit escape hatch and is visible
to diagnostics. Hedron does not require `!important` for ordinary supported customization.

### Inspection and diagnostics

Explorer and CLI services explain the relationship between source CSS and rendered components:

```text
hedron style explain --selector '[data-hedron-part="nav-link"]'
hedron style inspect --component AppShell
hedron style check --custom-css
```

Diagnostics report matching public hooks, winning declarations, layer order, token provenance,
private-selector coupling, missing preference fallbacks, source locations, and upgrade impact.

### Ejection and upgrade

Ejected CSS retains component/source/version provenance and can be compared with a later Hedron
release:

```text
hedron style eject AppShell --out styles/hedron
hedron style diff
hedron style update --check
```

An ejection report identifies changed hooks, removed tokens, altered defaults, and manual merge
points. Ejection never claims automatic semantic migration.

## Styling feature inventory

### Required

- #690 named motion recipes, reduced-motion equivalence, and print behavior;
- #693 public component parts/state recipes backed by the manifest;
- #694 semantic table/data-view chrome and row/selection states;
- #698 native form-control appearance, focus, validation, disabled, and high-contrast states;
- first-class local application stylesheet registration and asset planning;
- documented `application` cascade layer and deterministic layer order;
- public component hooks for parts/states/slots across the supported built-in inventory;
- namespaced application tokens with provenance and export/conformance support;
- style explanation, private-hook diagnostics, and custom-CSS checks;
- provenance-preserving ejection and upgrade-diff metadata;
- focus, navigation, overlay, layout, typography, media, icon, density, print, RTL, and
  preference-state coverage where the existing component inventory exposes those surfaces;
- browser, adapter, package, CSP, accessibility, performance, and no-JavaScript fallback evidence.

### Progressive

- typed selector helpers generated from the public hook manifest;
- Explorer computed-style/cascade visualization and interactive state-matrix previews;
- application token packages shared across projects;
- richer overlay placement and native anchor-positioning enhancements;
- visual regression capture for application-owned CSS;
- automatic suggestions that translate repeated CSS into a semantic recipe.

### Experimental

- third-party package style contracts beyond the first-party supported inventory;
- opt-in CSS Houdini/property registration where a canonical fallback exists;
- source-linked design-token synchronization with external tools;
- application style telemetry or runtime style mutation inspection.

### Excluded

- CSS-in-Python as a second authoring language;
- arbitrary response-provided CSS or script execution;
- remote font, stylesheet, or asset fetching as a default;
- a browser-side styling store, hydration layer, or visual editor runtime;
- private descendant selectors marketed as stable hooks;
- styling that changes DOM order, focus order, authorization, routes, or interaction state;
- automatic WCAG, VPAT, ACR, or legal-compliance certification.

## Security and accessibility boundary

Local application CSS is treated as application code and is subject to the existing registered
root, traversal, symlink, URL, CSP, and production build policies. User data never becomes a
selector, declaration, asset URL, or stylesheet source. Diagnostics and manifests redact secrets
and do not retain application content.

Every Required public hook and style vertical defines keyboard/focus behavior, semantic fallback,
forced-colors, high contrast, reduced motion, reduced transparency, print, zoom/reflow, narrow
viewport, RTL, and no-JavaScript behavior where applicable. Human assistive-technology claims
remain governed by the separate phase 0.21 evidence policy.

## Compatibility and rollback

- Existing `Theme`, `DesignSystem`, `StyleRecipe`, `StyleScope`, scoped CSS, default bundles,
  and `default_styles=False` remain valid.
- Existing private generated classes may change; public hooks are additive and versioned.
- Unregistered CSS remains outside the Hedron asset graph and receives no integration guarantees.
- Removing an application stylesheet registration restores the prior built-in styling path.
- Feature-off and asset-absent rendering retain ordinary server-rendered HTML and HTMX behavior.
- A failed public-hook migration produces a diagnostic and manual merge report; it never rewrites
  application CSS silently.

## Non-goals

This RFC does not create a full design editor, a universal CSS linter, a runtime CSS-in-JS layer,
a token marketplace, a component DOM freeze, a new browser runtime, or a claim that every arbitrary
CSS rule can be made portable across all hosts.

## Acceptance

Phase 0.65 is releasable only when the issue disposition, public hook manifest, application asset
graph, token/layer contract, style diagnostics, ejection provenance, open issue verticals, browser
fallbacks, fleet adoption, upgrade fixtures, and package evidence satisfy [RELEASE_0_65](../acceptance/RELEASE_0_65.md).
