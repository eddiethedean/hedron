---
description: What's new in Hedron 0.59 modern CSS and typed presentation.
search:
  boost: 1.4
---

# What's new in 0.59

Hedron 0.59 is the modern CSS platform release. It keeps the 0.58 public markers and
responsive defaults while adding explicit, opt-in capabilities for component-width layouts,
theme variants, typed control attributes, logical overlay placement, print, and preference-aware
presentation.

## Highlights

- CSS compiler format 2 with v1 manifest readers and stable v1 symbol hashing.
- Explicit `Container(query="inline-size", name=...)` boundaries and named markers.
- Theme variants through `StyleScope(variant=...)`, with additive output and validation.
- Typed `Button` / `LinkButton` size and width contracts plus safe ARIA/data/HTMX attributes.
- Bounded popover placement/collision markers and CSS anchor-positioning enhancement hooks.
- Print, dynamic viewport, safe-area, reduced-motion, contrast, forced-colors, transparency,
  hover, and pointer fallbacks in the default stylesheet.
- Reproducible compiler, browser, performance, package, and Data Mover migration evidence.

## Compatibility

Existing 0.58 classes, `data-hedron-*` markers, default theme behavior, viewport-responsive maps,
and `default_styles=False` remain valid. New container behavior and theme variants are opt-in.
Applications should review the [upgrade guide](upgrade.md) and run the phase evidence commands
before changing their dependency pin to `hedron>=0.59.0,<0.60`.

The release packet remains truthful about evidence status in
[release-gate-0.59.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/release-gate-0.59.toml).
