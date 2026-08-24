---
description: What's new in Hedron 0.59 modern CSS and presentation.
search:
  boost: 1.4
---

# What's new in 0.59

Hedron 0.59 is the modern CSS platform release. It keeps the 0.58 public markers and responsive
defaults while adding explicit, opt-in capabilities for component-width layouts, theme variants,
control attributes, logical overlay placement, print, and preference-aware presentation.

## Highlights

- CSS compiler format 2 with v1 manifest readers and stable v1 symbol hashing.
- Grammar-aware nesting, conditional rules, local imports/assets, deterministic cascade layers,
  source maps, and diagnostic rejection of unsafe or ambiguous CSS.
- Explicit `Container(query="inline-size", name=...)` boundaries and named markers.
- Intrinsic and dynamic viewport sizing, logical layout, RTL/writing-mode paths, and Progressive
  `subgrid` alignment with Grid/FormGrid fallbacks.
- Theme variants through `StyleScope(variant=...)`, with additive output and validation.
- Modern absolute-color parsing with canonical sRGB fallback, typography/content roles, and
  Progressive `light-dark()` / selected `@property` enhancements.
- `Button` / `LinkButton` size and width contracts plus safe ARIA/data/HTMX attributes.
- Bounded popover placement/collision markers and CSS anchor-positioning enhancement hooks.
- Native top-layer semantics, Progressive entry/exit and View Transitions, and Experimental
  decorative scroll-driven animation kept outside semantic state.
- Print, dynamic viewport, safe-area, reduced-motion, contrast, forced-colors, transparency,
  hover, and pointer fallbacks in the default stylesheet.
- Container/viewport-responsive AppShell chrome and provider-neutral pipeline, run-state, log, and
  operational-history presentation.
- Static `theme check`, `style explain`, `style preview`, `style diff`, and zero-application-CSS
  checks with redacted, reviewable output.
- Reproducible compiler, browser, performance, package, and Data Mover migration evidence.

## Compatibility

Existing 0.58 classes, `data-hedron-*` markers, default theme behavior, viewport-responsive maps,
and `default_styles=False` remain valid. New container behavior and theme variants are opt-in.
Applications should review the [upgrade guide](upgrade.md) and pin the published train with
`hedron>=0.62.0,<0.63`.

The release packet remains truthful about evidence status in
[release-gate-0.59.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/release-gate-0.59.toml).
