---
title: AmbientCanvas
description: Document-level inert canvas for composing ordered decorative layers.
---

# `AmbientCanvas`

Document-level inert canvas for composing ordered decorative layers.

| | |
|---|---|
| Import | `from hedron import AmbientCanvas` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="AmbientCanvas"><div class="hdc-stage"><div class="hdc-result"><strong>AmbientCanvas</strong><span>Document-level inert canvas for composing ordered decorative layers.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import AmbientCanvas, Text

component = AmbientCanvas(Text('Dashboard'), layers=(AmbientLayer(pattern='mesh', order=1),))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

AmbientCanvas is the document-level composition name for AmbientBackdrop. Its layers are aria-hidden, pointer-inert, theme-tokenized, and removed for print, forced colors, and reduced transparency.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
AmbientCanvas(*nodes, layers=(), id=None, class_=None, mark=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes / children` | `NodeLike` | Semantic page content rendered above the canvas. |
| `layers` | `Sequence[AmbientLayer]` | Ordered bounded ambient layer policies. |

## Composition and backend behavior

Keep `AmbientCanvas` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`AmbientCanvas` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep meaningful content outside the decorative layers and ensure contrast does not depend on the canvas.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not pass arbitrary gradients, CSS, or interactive content as a layer.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
