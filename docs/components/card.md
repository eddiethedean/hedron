---
title: Card
description: Group a titled piece of related content in a styled surface.
---

# `Card`

Group a titled piece of related content in a styled surface.

| | |
|---|---|
| Import | `from hedron import Card` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Card"><div class="hdc-stage"><article class="hdc-card"><header><span>Latest deployment</span><span class="hdc-badge hdc-success">Ready</span></header><p><strong>api-production</strong><br><span class="hdc-muted">Build completed in 42 seconds.</span></p><footer><a href="#">View deployment →</a></footer></article></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Card, Link, Text

component = Card(Text('Build completed in 42 seconds.'), title='Latest deployment', footer=Link('View logs', '/logs'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Card emits an addressable article with distinct header, body, and optional footer wrappers. The convenience `title` becomes an h3; use the `header` slot when the surrounding document requires another heading level or richer content. Its body accepts ordinary nested components, including layouts and forms, through the same renderer pipeline.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Card(*nodes, children=None, title=None, header=None, footer=None, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional card body content. |
| `children` | `NodeLike | sequence | None` | Keyword body content; combines with positional nodes. |
| `title` | `str | None` | Convenience title rendered as an `h3` when no header slot is supplied. |
| `header` | `NodeLike | None` | Custom header slot; takes precedence over title. |
| `footer` | `NodeLike | None` | Actions or supporting content. |
| `id` | `str | None` | Stable ID when the complete card is a swap target. |
| `class_` | `str | None` | Application class appended to `hedron-card`. |

## Composition and backend behavior

Keep `Card` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Card` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Choose a custom Heading in `header` when an automatic h3 would skip or repeat levels.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not make an entire complex card clickable when it contains other interactive controls.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
