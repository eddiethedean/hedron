---
status: shipped
---

# Themes, variants, and scoped styles


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted

```python
from hedron import Hedron

app = Hedron(
    title="Themed app",
    theme="aurora",
    security="standard",
    session_secret="replace-in-production",
)

return Article(
    class_=styles.root,
    children=[Heading(class_=styles.title)],
)
```

## Scoped style symbols

A component `styles.css` exposes local classes through a typed `styles` binding. Unknown names fail before production. Local classes and keyframes compile to stable identifiers; `:global(...)` is explicit.

## Themes

`Theme` declares semantic CSS variables and component variant defaults. Applications may register
themes and select one globally or at supported boundaries. Themes must define required accessibility
tokens and may extend, but not silently remove, base contracts.

In 0.59, `Theme.variants` is an explicit finite mapping of token overrides. Variants are additive,
validated, and emitted only when selected; they do not create a private selector API or change
component behavior.

Hedron ships two complete themes. `default` is the quiet blue product baseline;
`aurora` uses a more expressive violet palette, tighter geometry, richer depth, and a
two-tone ambient background. Both include explicit light and dark palettes and follow
the browser preference when no color mode is forced.

```python
app = Hedron(theme="aurora")

# An individual page can override the app selection for previews or mounted surfaces.
return Page(content, data_hedron_theme="default", data_theme="dark")
```

Use `StyleScope(variant=...)` for a subtree:

```python
from hedron import StyleScope, Text

StyleScope(Text("Dense review surface"), theme="aurora", variant="dense")
```

Unknown variant names fail closed. The base theme remains the fallback when no variant is selected.

```python
Theme(
    name="acme",
    tokens={"color.accent": "#..."},
)
```

## Built-in presentation

`Hedron()` includes a local, responsive stylesheet for typography, spacing,
forms, buttons, cards, tables, navigation, status states, and the built-in layout
components. It supports light and dark system preferences and does not require a build
step or a remote stylesheet.

The baseline lives in the low-priority `base` cascade layer. Application styles,
component styles, semantic theme variables, and the `overrides` layer can all customize
it without copying the stylesheet. To start with an entirely unstyled document, disable
it at the application boundary:

```python
app = Hedron(
    title="Unstyled shell",
    default_styles=False,
    security="standard",
    session_secret="replace-in-production",
)
```

This switch disables only Hedron's baseline stylesheet. It does not remove application
CSS, component CSS, or registered theme assets.

Runtime user data cannot become raw CSS. Dynamic presentation uses declared variants, safe attributes, or validated CSS-variable values. Strict mode can reject inline style attributes and remote resources.

0.59 also adds tested modern-color fallbacks, preference-aware tokens, and selected Progressive
`light-dark()` / `@property` enhancements. Every enhanced declaration has a canonical fallback;
remote font and asset fetching remains outside the Supported path.

Applications override packaged presentation through semantic props, extra classes, custom properties, cascade override layers, or ejected component styles.
