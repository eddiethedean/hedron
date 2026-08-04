---
title: Header
description: Render the semantic `header` landmark for introductory content.
---

# `Header`

Render the semantic `header` landmark for introductory content.

| | |
|---|---|
| Import | `from hedron import Header` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Header"><div class="hdc-stage"><header class="hdc-landmark"><span>&lt;header&gt;</span><strong>Header content</strong><p>Render the semantic `header` landmark for introductory content.</p></header></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Header, Heading, Text

component = Header(Heading('Acme', level=1), Text('Workspace overview'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

`Header` emits a native `<header>`, preserving semantic navigation instead of using a generic div. Children may be passed individually or as one non-string sequence.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Header(*nodes, children=None, class_=None, id=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional content belonging to this semantic region. |
| `children` | `NodeLike | sequence | None` | Keyword alternative; combines with positional nodes. |
| `class_` | `str | None` | Optional authored class name. |
| `id` | `str | None` | Stable fragment or target identifier. |

## Composition and backend behavior

Keep `Header` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Do not nest a page-level header inside main; a section may have its own header when it labels that section.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- A header is not automatically a banner landmark when nested. Choose placement intentionally.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
