---
title: ToastHost
description: Frozen out-of-band toast sink at `#hedron-toast`.
---

# `ToastHost`

Frozen out-of-band toast sink at `#hedron-toast`.

| | |
|---|---|
| Import | `from hedron import ToastHost` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ToastHost"><div class="hdc-stage"><div class="hdc-result"><strong>ToastHost</strong><span>Frozen out-of-band toast sink at `#hedron-toast`.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ToastHost

component = ToastHost()
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

ToastHost mounts the reserved `#hedron-toast` live region. Queue, TTL, and danger dismiss live in both `hedron-ui.mjs` copies (`hedron-core` static and `hedron/static`); authors do not write `hx-on` listeners.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
ToastHost(*, placement: "Literal['top-start', 'top-end', 'bottom-start', 'bottom-end', 'center']" = 'top-end', width: "Literal['content', 'field', 'full']" = 'content', max_width: "Literal['sm', 'md', 'lg']" = 'md', gap: "Literal['xs', 'sm', 'md']" = 'sm', **kwargs: 'Any') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `placement` | `Literal['top-start', 'top-end', 'bottom-start', 'bottom-end', 'center']` | Layout placement for the dock. Default: `'top-end'`. |
| `width` | `Literal['content', 'field', 'full']` | Optional width hint (CSS length or pixels). Default: `'content'`. |
| `max_width` | `Literal['sm', 'md', 'lg']` | Constructor parameter. Default: `'md'`. |
| `gap` | `Literal['xs', 'sm', 'md']` | Constructor parameter. Default: `'sm'`. |

## Composition and backend behavior

Keep `ToastHost` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`ToastHost` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep one ToastHost in the document shell so OOB toasts survive panel swaps.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not invent a second toast host id or attach `hx-on` handlers for queueing.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
