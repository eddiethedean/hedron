---
title: Inline
description: Arrange related children in a wrapping horizontal row.
---

# `Inline`

Arrange related children in a wrapping horizontal row.

| | |
|---|---|
| Import | `from hedron import Inline` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Inline"><div class="hdc-stage"><div class="hdc-inline"><span class="hdc-chip">Python</span><span class="hdc-chip">HTMX</span><span class="hdc-chip">FastAPI</span></div></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Button, Inline, LinkButton

component = Inline(Button('Save'), LinkButton('Cancel', '/account'), gap='0.75rem')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

`Inline` expresses one-dimensional horizontal composition while allowing the theme to wrap items at narrow widths. It emits data attributes rather than unsafe inline style.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Inline(*nodes, children=None, gap='0.5rem', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional inline items in DOM order. |
| `children` | `NodeLike | sequence | None` | Keyword child list; combines with positional nodes. |
| `gap` | `CSS length` | Validated spacing token. |
| `id` | `str | None` | Stable DOM target for the row. |
| `class_` | `str | None` | Optional class appended to `hedron-inline`. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Inline` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Ensure controls remain understandable when the row wraps and do not communicate meaning using position alone.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Do not assume an Inline will stay on one physical line on small screens.
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
