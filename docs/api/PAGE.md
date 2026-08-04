---
status: shipped
---

# `Page`


!!! note "Stability (0.8 freeze)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted · **Shipped in 0.4**

`Page` represents a complete navigable document and its associated metadata.

```python
from hedron import Page, Text

@app.page("/")
def home() -> Page:
    return Page(
        Text("Dashboard body"),
        title="Dashboard",
        description="Operations home",
    )
```

## Constructor (representative)

| Parameter | Description |
|---|---|
| `*children` | Body content (`NodeLike` values) |
| `title` | Document title |
| `description` | Optional meta description |
| Additional page props | Theme/history/head contributions as supported by the component props model |

Prefer returning `Page(...)` from `@app.page` / `@router.page` routes.

## Contract

- Ordinary navigation produces a valid document including language, head metadata, asset references, and body content.
- An HTMX request produces the declared fragment or layout-aware content rather than duplicating the document shell.
- An HTMX history-restore request (`HX-History-Restore-Request: true`) selects PAGE mode so the browser receives a full document.
- Scripts and styles enter through registered assets, not arbitrary string injection. Bundled HTMX is injected for PAGE responses when `/hedron-static/` is mounted.

Layouts are explicit components or registered policies. Hedron may provide a default layout but does not infer navigation, permissions, or application information architecture.

A page return annotation is an HTML response contract. Returning another component type is a mismatch unless the route declares an accepted union or explicit response.
