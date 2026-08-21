---
title: GridItem
description: Place one cell with named track and span tokens inside Grid.
---

# `GridItem`

Place one cell with named track and span tokens inside Grid.

| | |
|---|---|
| Import | `from hedron import GridItem` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="GridItem"><div class="hdc-stage"><div class="hdc-grid"><span><small>Span 2</small><strong>Wide cell</strong><em>GridItem</em></span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Card, GridItem, Text

component = GridItem(Card(Text('Wide')), span=2)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

GridItem uses presentation markers for CSP-safe placement without inline style.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
GridItem(*nodes, *, span=1, align='stretch', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Cell content. |
| `span` | `int | breakpoint map` | Column span (1–6), optionally responsive. |
| `align` | `start | center | end | stretch` | Cell alignment within the track. |

## Composition and backend behavior

Keep `GridItem` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`GridItem` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep reading order sensible when spans change the visual grid.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not invent arbitrary CSS track names outside the supported token set.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
