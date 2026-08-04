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

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Card, Grid, Text

component = Grid(Card(Text('Latency')), Card(Text('Errors')), Card(Text('Traffic')), columns=3)
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

Grid is declarative composition: it returns one component, not mutable positional column handles. The theme reads column and gap data attributes and may collapse columns responsively.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

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

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Grid` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Source order must remain the intended reading order at every breakpoint.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Do not hold a column handle and mutate it later; construct every cell as a child.
- Do not copy docs-preview JavaScript into an application server; demos simulate HTMX locally.
- Choose components for semantics first, then theme them.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

For interactive flows, assert method, URL, headers, fragment body, and status with a framework test client. Add a browser test when keyboard or HTMX swap behavior is material.

[All component demos](index.md) · [Built-in API baseline](../api/BUILT_INS.md) · [Testing UI](../guides/testing.md) · [Forms and actions](../guides/forms-and-actions.md)
