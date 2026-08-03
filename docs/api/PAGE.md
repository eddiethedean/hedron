# `Page`

**Status:** Accepted

`Page` represents a complete navigable document and its associated metadata.

```python
@app.page("/")
def home() -> Page:
    return Page(
        title="Dashboard",
        children=[Dashboard()],
    )
```

## Contract

- Ordinary navigation produces a valid document including language, head metadata, asset references, and body content.
- An HTMX request produces the declared fragment or layout-aware content rather than duplicating the document shell.
- Page metadata may include title, description, canonical URL, viewport, selected theme, history policy, and approved head contributions.
- Scripts and styles enter through registered assets, not arbitrary string injection.

Layouts are explicit components or registered policies. Hedron may provide a default layout but does not infer navigation, permissions, or application information architecture.

A page return annotation is an HTML response contract. Returning another component type is a mismatch unless the route declares an accepted union or explicit response.

