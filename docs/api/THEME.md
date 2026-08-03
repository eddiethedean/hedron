---
status: shipped
---

# Themes and scoped styles

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

Runtime user data cannot become raw CSS. Dynamic presentation uses declared variants, safe attributes, or validated CSS-variable values. Strict mode can reject inline style attributes and remote resources.

Applications override packaged presentation through semantic props, extra classes, custom properties, cascade override layers, or ejected component styles.

