---
title: Grid
description: Lay out explicit child components in a responsive grid.
---

# `Grid`

Lay out explicit child components in a responsive grid.

| | |
|---|---|
| Import | `from hedron import Grid` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Grid"><div class="hdc-stage"><div class="hdc-grid"><span><small>Latency</small><strong>184 ms</strong><em>↓ 12%</em></span><span><small>Errors</small><strong>0.08%</strong><em>↓ 4%</em></span><span><small>Traffic</small><strong>28.4k</strong><em>↑ 9%</em></span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Card, Grid, Text

component = Grid(Card(Text('Latency')), Card(Text('Errors')), Card(Text('Traffic')), columns=3)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Grid is declarative composition: it returns one component, not mutable positional column handles. The theme reads column and gap data attributes and may collapse columns responsively.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Grid(*nodes, children=None, columns=2, gap='1rem', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional grid cells in reading order. |
| `children` | `NodeLike | sequence | None` | Keyword child list; combines with positional nodes. |
| `columns` | `int` | Requested column count; must be at least one. |
| `gap` | `CSS length` | Validated row and column gap. |
| `id` | `str | None` | Stable DOM target for the grid region. |
| `class_` | `str | None` | Optional class appended to `hedron-grid`. |

## Composition and backend behavior

Keep `Grid` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Source order must remain the intended reading order at every breakpoint.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not hold a column handle and mutate it later; construct every cell as a child.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
