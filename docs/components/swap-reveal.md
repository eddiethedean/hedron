---
title: SwapReveal
description: Opt-in HTMX after-swap reveal wrapper that respects prefers-reduced-motion.
---

# `SwapReveal`

Opt-in HTMX after-swap reveal wrapper that respects prefers-reduced-motion.

| | |
|---|---|
| Import | `from hedron import SwapReveal` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="SwapReveal"><div class="hdc-stage"><div class="hdc-result"><strong>SwapReveal</strong><span>Opt-in HTMX after-swap reveal wrapper that respects prefers-reduced-motion.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import SwapReveal, Text

component = SwapReveal(Text('Updated region'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

SwapReveal wraps a swapped region. First paint includes `is-revealed` so content is visible; Hedron UI replays the reveal class on `htmx:afterSwap` unless reduced motion is requested.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
SwapReveal(*nodes, children=None, reduced_motion=True)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Content revealed after an HTMX swap. |
| `reduced_motion` | `bool` | Honor prefers-reduced-motion (default True). |

## Composition and backend behavior

Keep `SwapReveal` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`SwapReveal` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

## Accessibility

Keep the wrapper around the swapped region so keyboard focus restoration stays in the same landmark.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use animation as the only status cue; pair with BusyRegion or aria-busy.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
