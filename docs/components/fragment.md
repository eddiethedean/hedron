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

<!-- hedron-sim:component-fragment -->

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Alert, Fragment, Text

component = Fragment(Alert('Saved', tone='success'), Text('The record is current.'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

A fragment flattens its children into the render stream. It is ideal for targeted HTMX responses because it does not change the target's surrounding layout or introduce an accidental DOM node.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

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
