---
title: Text
description: Render escaped text with an explicit paragraph or inline text element.
---

# `Text`

Render escaped text with an explicit paragraph or inline text element.

| | |
|---|---|
| Import | `from hedron import Text` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Text"><div class="hdc-stage"><div class="hdc-type"><p><strong>Changes saved.</strong> This text is a paragraph that carries the primary message.</p><span class="hdc-muted">Updated just now · inline supporting text</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Stack, Text
component = Stack(Text('Changes saved.'), Text('Updated now', as_='small'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Text defaults to a paragraph and can render a span, strong, emphasis, or small element when those semantics are intentional. Content is serialized as text, so HTML-looking user input is displayed rather than executed.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Text(content='', *, as_='p')
```

| Parameter | Type | Meaning |
|---|---|---|
| `content` | `str` | Escaped text content. |
| `as_` | `p | span | strong | em | small` | Exact permitted native text element. |

## Composition and backend behavior

Keep `Text` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Text` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Choose `strong` and `em` for meaning rather than appearance, and use real list, heading, label, and link components when those semantics apply.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use a collection of spans to imitate a paragraph or use `strong` merely to obtain bold styling.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
