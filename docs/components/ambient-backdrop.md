---
title: AmbientBackdrop
description: Finite decorative backdrop that never owns interaction or content semantics.
---

# `AmbientBackdrop`

Add a restrained, deterministic decorative treatment behind page or surface content.

| | |
|---|---|
| Import | `from hedron import AmbientBackdrop` |
| Distribution | `hedron-core` / `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

```python
from hedron import AmbientBackdrop, Container, Text

component = AmbientBackdrop(
    Container(Text("Dashboard"), max_width="lg"),
    pattern="mesh",
    tone="accent",
    intensity="subtle",
)
```

The decoration is a separate `aria-hidden` layer with `pointer-events: none`; content remains
in normal document order. Patterns are finite CSS treatments (`radial`, `dots`, `grid`, and
`mesh`) and are not animated. The default theme hides the layer in print, forced-colors, and
reduced-transparency contexts.

Use it as a page/surface wrapper, not as a replacement for a landmark or a source of contrast.
Keep headings, status, and focusable controls in the child content.

[All component demos](index.md) · [Presentation API](../api/PRESENTATION.md)
