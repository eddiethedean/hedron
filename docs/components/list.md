---
title: List
description: Render ordered or unordered items from child values.
---

# `List`

Render ordered or unordered items from child values.

| | |
|---|---|
| Import | `from hedron import List` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="List"><div class="hdc-stage"><ol class="hdc-list"><li><span>Create a branch</span><small>Keep the change isolated</small></li><li><span>Add the component</span><small>Compose native semantics</small></li><li><span>Run checks</span><small>Verify behavior and output</small></li></ol></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import List

component = List('Create a branch', 'Add the component', 'Run checks', ordered=True)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Each supplied item becomes one native `li` inside `ul` or `ol`. Nested structure should be built explicitly so list hierarchy remains inspectable.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
List(*items, ordered=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `items` | `NodeLike` | Values wrapped in list items. |
| `ordered` | `bool` | Use `<ol>` when sequence matters. |

## Composition and backend behavior

Keep `List` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`List` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Choose ordered lists only when changing the sequence changes the meaning.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not type bullet characters into Text; use List so assistive technology receives list semantics.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
