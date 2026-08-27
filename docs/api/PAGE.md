---
status: shipped
---

# `Page`

!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Accepted · **Shipped** (introduced in 0.4; current train **0.66.x**)

`Page` represents a complete navigable document and its associated metadata.

```python
from hedron import Page, Text

@app.page("/")
def home() -> Page:
    return Page(
        Text("Dashboard body"),
        title="Dashboard",
        lang="en",
    )
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `*body` / `children=` | `NodeLike` | — | Body content (required slot) |
| `title` | `str` \| `None` | `None` | Document `<title>` when set |
| `lang` | `str` | `"en"` | Root `html` lang attribute |
| `head` | `NodeLike` \| `None` | `None` | Optional extra head nodes |
| `data_theme` | `str` \| `None` | `None` | Optional `data-theme` on `<html>` |
| `data_hedron_theme` | `str` \| `None` | `None` | Optional named Hedron theme on `<html>`; overrides the app theme for this page |
| `**kwargs` | — | — | Additional `PageProps` / component kwargs when declared |

## Returns

| Context | Result |
|---|---|
| `@app.page` navigation | Full HTML document (PAGE mode) |
| Same route with `HX-Request` | Fragment / layout-aware content (not a duplicate shell) |
| `HX-History-Restore-Request: true` | PAGE mode full document |

## Errors

| Condition | Typical outcome |
|---|---|
| Returning a non-`Page` from a page route without an accepted union | Response / typing mismatch |
| Missing production build when gated | `HED-BUILD-*` at startup (see [error codes](../guides/error-codes.md)) |

## Contract

- Ordinary navigation produces a valid document including language, head metadata, asset references, and body content.
- An HTMX request produces the declared fragment or layout-aware content rather than duplicating the document shell.
- Scripts and styles enter through registered assets, not arbitrary string injection. Bundled HTMX is injected for PAGE responses when `/hedron-static/` is mounted.

Layouts are explicit components or registered policies. Hedron may provide a default layout but does not infer navigation, permissions, or application information architecture.

## See also

- [Hedron](HEDRON.md) · [Rendering](RENDERING.md) · [Quickstart](../getting-started/quickstart.md)
- Autodoc: [Autodoc](AUTODOC.md)
