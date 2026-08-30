---
title: Image
description: Render an image with a validated source and required alternative text.
---

# `Image`

Render an image with a validated source and required alternative text.

| | |
|---|---|
| Import | `from hedron import Image` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Image"><div class="hdc-stage"><figure class="hdc-image"><div role="img" aria-label="Abstract teal landscape used as a documentation placeholder"><span>Image preview</span></div><figcaption>Meaningful alternative: “The platform team at the meetup.”</figcaption></figure></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Image
component = Image('/static/team.jpg', alt='The platform team at the 2026 meetup', width=960, height=540)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Image applies the SafeUrl asset policy and always writes the supplied alternative. Supplying intrinsic dimensions lets the browser reserve space before the asset arrives. Loading strategy is not a constructor option on this built-in.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Image(src, *, alt, width=None, height=None, allow_external=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `src` | `SafeUrl | str` | Validated asset URL. |
| `alt` | `str` | Required text alternative; use an empty string for decorative images. |
| `width / height` | `int | None` | Intrinsic dimensions to reduce layout shift. |
| `allow_external` | `bool` | Permit a validated external asset origin. |

## Composition and backend behavior

Keep `Image` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Image` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Describe the image's purpose in context; use `alt=''` only when nearby content already conveys everything.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not enable external assets casually: review privacy, CSP, availability, and tracking implications.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
