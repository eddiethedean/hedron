---
title: Modern CSS in 0.59
description: The 0.59 styling contract, capability tiers, fallbacks, and authoring patterns.
search:
  boost: 1.5
---

# Modern CSS in 0.59

Hedron 0.59 upgrades the styling path without adding a second theme registry, CSS runtime,
client-side style injector, or mandatory Node toolchain. Python expresses finite semantic intent;
component `styles.css` remains the escape hatch for standards-based CSS.

The release has one styling authority:

```text
Theme / DesignSystem → semantic markers and tokens → default CSS + scoped CSS → deterministic assets
```

Existing 0.58 constructors, classes, `data-hedron-*` markers, theme names, token aliases, and
`default_styles=False` remain valid. New 0.59 behavior is opt-in where it changes responsive
context or presentation scope.

## Capability tiers

Do not read “modern CSS” as “every browser must implement every feature.” Hedron assigns each
capability a tier:

| Tier | Meaning | Documentation rule |
|---|---|---|
| **Required** | Supported path with a tested native or static fallback | Safe for ordinary product UI |
| **Progressive** | Feature-detected enhancement with an independently usable fallback | Treat the fallback as the contract |
| **Experimental** | Opt-in, decorative, and excluded from unqualified support claims | Label it in product documentation |
| **Deferred** | Outside the 0.59 styling contract | Do not build adoption guidance around it |

## What changed in 0.59

### Scoped CSS compiler and cascade

Component stylesheets now target compiler format 2. The compiler preserves CSS grammar boundaries
for selectors, declarations, descriptors, strings, comments, URLs, nesting, conditional rules,
and safe unknown at-rules. It reads format-1 manifests and preserves v1 symbol hashes by default.

```css
/* components/Callout/styles.css */
.root {
  display: grid;
  gap: var(--hedron-space-unit);

  & > .title {
    text-wrap: balance;
  }
}

@supports (container-type: inline-size) {
  .root {
    container-type: inline-size;
  }
}
```

Use local imports and registered local assets only. Quoted imports, `url()`, `@font-face`,
`image-set()`, traversal, remote URLs, ambiguous rewrites, unsafe globals, and malformed CSS are
resolved or rejected during the build. Production does not compile CSS at runtime.

The generated stylesheet has one deterministic layer order:

```text
reset → tokens → base → components → utilities → overrides
```

Use semantic props and tokens before increasing specificity. `@scope`, `:scope`, `:is()`,
`:where()`, `:not()`, and `:has()` are available according to their tier and fallback rules;
private selector theming is not part of the public contract.

### Container-aware and intrinsic layout

`Container` can opt a boundary into inline-size queries. Its existing viewport behavior remains
the default.

```python
from hedron import Container, Grid, Text

panel = Container(
    Grid(Text("Details"), Text("Activity"), columns={"base": 1, "md": 2}),
    query="inline-size",
    name="workspace-panel",
)
```

The component emits validated `data-hedron-container-query` and
`data-hedron-container-name` markers. The 0.59 layout contract covers:

- `@container`, `cqi`, `cqb`, `cqmin`, and `cqmax` with viewport/static fallbacks;
- intrinsic sizing through `min()`, `max()`, `clamp()`, `minmax()`, `fit-content()`, and
  `aspect-ratio`;
- dynamic viewport units (`svh`, `lvh`, `dvh`) and safe-area insets;
- logical properties and values across LTR, RTL, mixed direction, and selected vertical writing;
- `subgrid` as a Progressive alignment enhancement over ordinary `Grid`/`FormGrid` tracks; and
- complete-content behavior at narrow widths, zoom, and increased text spacing.

Style queries and nested container behavior remain feature-detected. They must not become hidden
application state or change DOM order.

### Tokens, themes, variants, color, and typography

`Theme` and `DesignSystem` remain the source of semantic values. 0.59 adds explicit finite theme
variants, additive output, modern color fallbacks, and stronger typography guidance.

```python
from hedron import StyleScope, Text

StyleScope(
    Text("Compact review mode", role="title"),
    theme="aurora",
    variant="dense",
    color_mode="dark",
    density="compact",
)
```

Variants emit `data-hedron-variant` and are validated as finite safe names. An unknown variant
fails closed; no arbitrary CSS selector or user value becomes a theme variant.

The color contract includes parsed absolute CSS Color 4 input, canonical sRGB fallbacks, optional
wide-gamut declarations, deterministic gamut mapping, contrast/focus checks, and provenance in the
brand plan. `color-mix()` is safe for generated presentation. Remote fonts and automatic remote
asset fetching remain outside the Supported path.

Typography roles cover fluid sizing, balanced and pretty wrapping, hyphenation, code and numeric
content, long/international text, variable fonts, and explicit local font assets. Prefer roles and
local fallback stacks over arbitrary font-size overrides.

`light-dark()` and `color-scheme` are Progressive enhancements. Explicit light/dark markers and
the existing system-preference rules remain the fallback. Selected bounded custom properties may
use `@property`; ordinary custom properties remain the fallback.

### Overlays and motion

Native dialog/popover/top-layer semantics remain the authority. `Popover` exposes finite logical
placement and collision behavior:

```python
from hedron import Popover, Text

Popover(
    Text("Filters"),
    label="Open filters",
    placement="block-end",
    collision="flip",
)
```

Supported static/details/native paths remain usable when popover support is absent. Anchor
positioning is a Progressive enhancement; the fallback is logical document flow or bounded
existing placement. Entry/exit transitions use `@starting-style` and discrete transitions only
when supported, otherwise the state changes immediately and remains stable.

View Transitions are an opt-in Progressive navigation/surface enhancement. They must preserve
focus, title/history, HTMX swap semantics, and server state. Scroll-driven animations are
Experimental and decorative only: never use them for authorization, validation, task progress,
or other semantic state.

### Media, preferences, and print

The default stylesheet includes first-party rules for print and preference conditions:

- `prefers-reduced-motion` removes nonessential motion;
- `forced-colors` preserves usable contrast and focus;
- `prefers-contrast` and `prefers-reduced-transparency` adjust presentation where supported;
- `hover` and `pointer` avoid assuming a precise pointing device;
- logical direction and writing-mode paths preserve content and focus; and
- `@media print`, page breaks, links, forms, data, statuses, disclosures, and shell landmarks
  remain readable in source order.

The non-enhanced path must remain complete, keyboard-usable, and non-color-dependent. Styling
cannot hide authoritative content or change semantics.

### Typed controls and product surfaces

`Button` and `LinkButton` share the 0.59 `size` and `width` vocabulary and accept a bounded
`attrs=` seam for global, `aria-*`, `data-*`, approved HTMX, and popover/dialog-trigger
attributes:

```python
from hedron import Button, LinkButton

Button(
    "Save",
    size="sm",
    width="full",
    attrs={"hx-post": "/save", "aria-describedby": "save-help"},
)
LinkButton("Review", "/review", size="sm", width="full", attrs={"data-track": "review"})
```

The seam rejects component-owned structural attributes, `on*`, inline `style`, `hx-on*`,
malformed ARIA/data names, and non-allowlisted HTMX attributes. The component still owns `type`,
`disabled`, `href`, `class`, and `id`.

The same tokens power composable AppShell chrome and provider-neutral workflow presentation:
brand/account/footer/auth states, responsive pipeline connectors, explicit run states, logs, and
compact history. These surfaces do not own authentication, transfer execution, polling, logs, or
authorization; they render typed state supplied by the application.

## 0.59 feature matrix

| Area | Capability | Tier | Fallback or boundary |
|---|---|---|---|
| Compiler | Grammar-aware selectors, declarations, descriptors, strings, comments, URLs, custom identifiers | Required | Invalid or unsafe syntax is rejected diagnostically |
| Compiler | CSS nesting and nested conditional rules | Required | Browser-valid scoped CSS |
| Compiler | `@media`, `@supports`, `@container`, `@scope`, `@starting-style`, safe unknown at-rules | Required | Preserve safe syntax; reject ambiguous/unsafe rewrites |
| Compiler | Local imports, font sources, `image-set()`, nested URLs | Required | Resolve bounded local assets or reject; no remote imports |
| Cascade | `@layer`, `:where()`, `:is()`, specificity normalization | Required | One deterministic layer output |
| Cascade | Native `@scope` / `:scope` | Progressive | Public-marker selector boundary |
| Layout | Size/style container queries | Required / Progressive | Base layout and viewport maps |
| Layout | `subgrid` | Progressive | Ordinary Grid/FormGrid tracks |
| Layout | Logical layout, writing modes, intrinsic and viewport sizing | Required | Documented physical exceptions and ordinary units |
| Theme | Modern color and finite theme variants | Required | Canonical sRGB and base theme tokens |
| Theme | `light-dark()`, `color-scheme`, selected `@property` tokens | Progressive | Explicit mode selectors and ordinary custom properties |
| Content | Modern typography, wrapping, hyphenation, variable/local fonts | Required | System fallback stacks and ordinary wrapping |
| Overlay | Popover/top layer/dialog and logical placement | Required / Progressive | Details/static/native flow and bounded placement |
| Motion | Starting/discrete transitions and View Transitions | Progressive | Immediate stable state or ordinary navigation/swap |
| Motion | Scroll-driven animation | Experimental | Static complete presentation |
| Media | Preference media and print | Required | Non-motion, non-color, semantic source-order presentation |
| Performance | `content-visibility` and containment | Progressive | Fully rendered content |
| Product surfaces | Typed controls, shell chrome, pipeline presentation | Required | Existing native/built-in compositions |

The machine-readable source of truth is
[`modern-css-inventory-059.toml`](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/modern-css-inventory-059.toml). It records the
exact gate, fallback, and package disposition for every capability.

## Tooling and review

Use static, redacted tooling during design review and CI:

```bash
hedron theme check
hedron --app app:app style explain --format human
hedron --app app:app style preview --output .artifacts/styling --mode all
hedron --app app:app style diff --base default --candidate aurora
hedron style check --zero-app-css PATH
```

`explain`, `preview`, and `diff` do not execute application callbacks or expose application data.
`eject` is reviewable and no-overwrite by default. Inspect source locations, winning layers,
variants, aliases, fallbacks, assets, and budgets before accepting a visual change.

For upgrades, run the 0.58-to-0.59 fixtures before changing a pin. Existing application CSS is
not silently rewritten. See [the upgrade guide](upgrade.md), [Presentation APIs](../api/PRESENTATION.md),
and [Themes](../api/THEME.md).

## Explicit non-goals

0.59 does not add free-form CSS-in-Python, a utility-string framework, a second compiler/cascade/
theme registry, runtime style injection, mandatory Node, remote font auto-fetch, CSS masonry,
paint/layout worklets, private-selector theming, visual DOM reordering, or styling-owned behavior.
