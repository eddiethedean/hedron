---
title: Surface
description: Compose a presentation-token surface without application CSS.
---

# `Surface`

Compose a presentation-token surface without application CSS.

| | |
|---|---|
| Import | `from hedron import Surface` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Surface"><div class="hdc-stage"><div class="hdc-container"><strong>Raised surface</strong><p class="hdc-muted">Presentation tokens only — no application CSS.</p></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Surface, Text

component = Surface(Text('Workspace body'), elevation='raised', padding='lg')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Surface is the zero-application-CSS building block for panels. Presentation is marker-driven (`data-hedron-*`) and styled by first-party CSS.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Surface(*nodes, *, elevation='plain', padding='md', shape='rounded', width=None, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Surface body content. |
| `elevation` | `plain | raised` | Named elevation token. |
| `padding` | `none | xs | sm | md | lg | xl` | Named padding token. |
| `shape` | `square | rounded | pill` | Named shape token. |
| `width` | `content | narrow | wide | full | None` | Optional width token. |

## Composition and backend behavior

Keep `Surface` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Surface` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Prefer Surface over ad-hoc div wrappers when you need a raised or padded region.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not pass inline style or arbitrary CSS lengths; use the named token vocabularies.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
