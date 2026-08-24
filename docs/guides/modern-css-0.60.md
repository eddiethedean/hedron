---
description: Modern CSS and custom-theme behavior in Hedron 0.60.
search:
  boost: 1.1
---

# Modern CSS in 0.60

The 0.60 checkout completes the 0.59 modern CSS authority with the custom theme platform. The
existing compiler, cascade, token markers, and `default_styles=False` behavior remain authoritative.

## Styling completion

0.60 adds absolute colors with deterministic sRGB fallbacks, immutable `ThemeSpec` and
`ThemePatch` authoring, registry-derived validation profiles, accessibility mappings, bounded recipe
families, server-first theme preference markers, and a read-only Explorer Theme Lab. `Brand`,
`ToastHost`, `ConnectorFlow`, and `ScrollRegion` expose finite presentation contracts that work
without application CSS and retain print, reduced-motion, forced-color, and feature-off fallbacks.

See [What's new in 0.60](whats-new-0.60.md) and the [upgrade guide](upgrade.md) for the public
authoring and compatibility path.
