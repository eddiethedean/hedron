---
status: shipped
---

# Themes and scoped styles


!!! note "Stability (0.11 train)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted

```python
app = Hedron(theme="default")

return Article(
    class_=styles.root,
    children=[Heading(class_=styles.title)],
)
```

## Scoped style symbols

A component `styles.css` exposes local classes through a typed `styles` binding. Unknown names fail before production. Local classes and keyframes compile to stable identifiers; `:global(...)` is explicit.

## Themes

`Theme` declares semantic CSS variables and component variant defaults. Applications may register themes and select one globally or at supported boundaries. Themes must define required accessibility tokens and may extend, but not silently remove, base contracts.

```python
Theme(
    name="acme",
    tokens={"color.accent": "#..."},
)
```

## Default presentation

`Hedron()` includes a local, responsive baseline stylesheet for typography, spacing,
forms, buttons, cards, tables, navigation, status states, and the built-in layout
components. It supports light and dark system preferences and does not require a build
step or a remote stylesheet.

The baseline lives in the low-priority `base` cascade layer. Application styles,
component styles, semantic theme variables, and the `overrides` layer can all customize
it without copying the stylesheet. To start with an entirely unstyled document, disable
it at the application boundary:

```python
app = Hedron(default_styles=False)
```

This switch disables only Hedron's baseline stylesheet. It does not remove application
CSS, component CSS, or registered theme assets.

Runtime user data cannot become raw CSS. Dynamic presentation uses declared variants, safe attributes, or validated CSS-variable values. Strict mode can reject inline style attributes and remote resources.

Applications override packaged presentation through semantic props, extra classes, custom properties, cascade override layers, or ejected component styles.
