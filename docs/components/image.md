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

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Image

component = Image('/static/team.jpg', alt='The platform team at the 2026 meetup', width=960, height=540)
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

Image applies the SafeUrl asset policy and always writes the supplied alternative. Supplying intrinsic dimensions lets the browser reserve space before the asset arrives. Loading strategy is not a constructor option on this built-in.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Image(src, *, alt, width=None, height=None, allow_external=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `src` | `SafeUrl | str` | Validated asset URL. |
| `alt` | `str` | Required text alternative; use an empty string for decorative images. |
| `width / height` | `int | None` | Intrinsic dimensions to reduce layout shift. |
| `allow_external` | `bool` | Permit a validated external asset origin. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Image` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Describe the image's purpose in context; use `alt=''` only when nearby content already conveys everything.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Do not enable external assets casually: review privacy, CSP, availability, and tracking implications.
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
