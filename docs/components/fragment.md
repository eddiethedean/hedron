---
title: Fragment
description: Return several sibling nodes without adding a wrapper element.
---

# `Fragment`

Return several sibling nodes without adding a wrapper element.

| | |
|---|---|
| Import | `from hedron import Fragment` |
| Distribution | `hedron` |
| Backend activity | Common for HTMX |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Fragment"><div class="hdc-stage"><div class="hdc-fragment"><span class="hdc-badge">Saved</span><span><strong>Profile updated</strong><small>The record is current.</small></span></div><p class="hdc-muted">Two sibling nodes; no wrapper is added by Fragment.</p></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Alert, Fragment, Text

component = Fragment(Alert('Saved', tone='success'), Text('The record is current.'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

A fragment flattens its children into the render stream. It is ideal for targeted HTMX responses because it does not change the target's surrounding layout or introduce an accidental DOM node.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Fragment(*nodes, children=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional renderable sibling nodes. |
| `children` | `NodeLike | sequence | None` | Keyword alternative; combines with positional nodes. |

## Composition and backend behavior

Keep `Fragment` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

After a swap, focus and live-region behavior still belong to the response content; a wrapper-free result does not announce itself.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not rely on a fragment to carry an `id`, class, or HTMX target—there is no wrapper on which to place attributes.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
