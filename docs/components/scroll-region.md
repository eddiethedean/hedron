---
title: ScrollRegion
description: Bound a semantic list, log, or arbitrary child region without changing its children.
---

# `ScrollRegion`

Bound a semantic list, log, or arbitrary child region without changing its children.

| | |
|---|---|
| Import | `from hedron import ScrollRegion` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ScrollRegion"><div class="hdc-stage"><div class="hdc-result"><strong>ScrollRegion</strong><span>Bound a semantic list, log, or arbitrary child region without changing its children.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ScrollRegion, Text

component = ScrollRegion(Text('Recent events'), axis='block', size='md', label='Recent events')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

ScrollRegion owns bounded overflow markers while preserving the child tree and its semantics. Use `label=` when the region needs an accessible name.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
ScrollRegion(*nodes: 'NodeLike', children: 'NodeLike' = None, axis: "Literal['block', 'inline', 'both']" = 'block', size: "Literal['sm', 'md', 'lg']" = 'md', affordance: "Literal['auto', 'always']" = 'auto', label: 'str | None' = None, id: 'str | None' = None, class_: 'str | None' = None, mark: 'str | None' = None, **kwargs: 'Any') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `*nodes` | `NodeLike` | Positional child nodes. |
| `children` | `NodeLike` | Keyword alternative for child nodes; combines with positional children. Default: `None`. |
| `axis` | `Literal['block', 'inline', 'both']` | Spacer axis (`block`, `inline`, or `both`). Default: `'block'`. |
| `size` | `Literal['sm', 'md', 'lg']` | Spacer size (CSS length). Default: `'md'`. |
| `affordance` | `Literal['auto', 'always']` | Constructor parameter. Default: `'auto'`. |
| `label` | `str | None` | Accessible label text shown to users. Default: `None`. |
| `id` | `str | None` | Optional DOM `id`. Default: `None`. |
| `class_` | `str | None` | Optional CSS class string (`class` in HTML). Default: `None`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |

## Composition and backend behavior

Keep `ScrollRegion` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`ScrollRegion` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use a meaningful label for multiple scrollable regions and keep keyboard focus on the actual interactive children.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use ScrollRegion to hide required content in print or to replace semantic list/table elements.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
