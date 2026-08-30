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

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Button, Heading, Stack, Text
component = Stack(Heading('Settings', level=2), Text('Profile'), Button('Save'), gap='lg')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

`Stack` writes layout intent and the validated gap to data attributes consumed by the theme; the shipped theme applies that exact gap without requiring an unsafe inline style. Its built-in class is retained when you add an application class. DOM order is unchanged, so the visual sequence matches reading and keyboard order.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Stack(*nodes, children=None, gap='1rem', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional items in visual and DOM order. |
| `children` | `NodeLike | sequence | None` | Keyword child list; combines with positional nodes. |
| `gap` | `CSS length` | Validated `rem`, `em`, `px`, or `%` spacing. |
| `id` | `str | None` | Stable DOM target for the stack region. |
| `class_` | `str | None` | Optional class appended to `hedron-stack`. |

## Composition and backend behavior

Keep `Stack` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Stack` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep DOM order meaningful and never use CSS reordering to change the task sequence.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Values such as `calc(...)`, viewport units, and arbitrary CSS are rejected; use a supported length token.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
