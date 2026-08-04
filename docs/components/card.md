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

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Card, Link, Text

component = Card(Text('Build completed in 42 seconds.'), title='Latest deployment', footer=Link('View logs', '/logs'))
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

Card emits an addressable article with distinct header, body, and optional footer wrappers. The convenience `title` becomes an h3; use the `header` slot when the surrounding document requires another heading level or richer content. Its body accepts ordinary nested components, including layouts and forms, through the same renderer pipeline.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

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

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Card` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Choose a custom Heading in `header` when an automatic h3 would skip or repeat levels.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Do not make an entire complex card clickable when it contains other interactive controls.
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
