---
title: Stack
description: Arrange children vertically with a validated, consistent gap.
---

# `Stack`

Arrange children vertically with a validated, consistent gap.

| | |
|---|---|
| Import | `from hedron import Stack` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Stack"><div class="hdc-stage"><div class="hdc-stack"><span><b>Build completed</b><small>42 seconds ago</small></span><span><b>Preview deployed</b><small>Environment ready</small></span><span><b>Review requested</b><small>2 teammates notified</small></span></div></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Button, Heading, Stack, Text

component = Stack(Heading('Settings', level=2), Text('Profile'), Button('Save'), gap='1.25rem')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

`Stack` writes layout intent and the validated gap to data attributes consumed by the theme; the shipped theme applies that exact gap without requiring an unsafe inline style. Its built-in class is retained when you add an application class. DOM order is unchanged, so the visual sequence matches reading and keyboard order.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Stack(*nodes, children=None, gap='1rem', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional items in visual and DOM order. |
| `children` | `NodeLike | sequence | None` | Keyword child list; combines with positional nodes. |
| `gap` | `CSS length` | Validated `rem`, `em`, `px`, or `%` spacing. |
| `id` | `str | None` | Stable DOM target for the stack region. |
| `class_` | `str | None` | Optional class appended to `hedron-stack`. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Stack` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep DOM order meaningful and never use CSS reordering to change the task sequence.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Values such as `calc(...)`, viewport units, and arbitrary CSS are rejected; use a supported length token.
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
