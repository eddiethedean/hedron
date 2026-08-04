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

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Alert, Fragment, Text

component = Fragment(Alert('Saved', tone='success'), Text('The record is current.'))
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

A fragment flattens its children into the render stream. It is ideal for targeted HTMX responses because it does not change the target's surrounding layout or introduce an accidental DOM node.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Fragment(*nodes, children=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional renderable sibling nodes. |
| `children` | `NodeLike | sequence | None` | Keyword alternative; combines with positional nodes. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Fragment` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

After a swap, focus and live-region behavior still belong to the response content; a wrapper-free result does not announce itself.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Do not rely on a fragment to carry an `id`, class, or HTMX target—there is no wrapper on which to place attributes.
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
