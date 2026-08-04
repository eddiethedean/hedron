---
title: Form
description: Compose a native GET or POST form with validated action URLs and optional HTMX attributes.
---

# `Form`

Compose a native GET or POST form with validated action URLs and optional HTMX attributes.

| | |
|---|---|
| Import | `from hedron import Form` |
| Distribution | `hedron` |
| Backend activity | On submit |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Form"><div class="hdc-stage"><form class="hdc-form" data-hdc-form><label>Email address<input name="email" type="email" required placeholder="ada@example.com"></label><button class="hdc-button hdc-primary" type="submit">Submit</button></form><p role="status" aria-live="polite" data-hdc-status>Nothing submitted yet.</p></div><div class="hdc-request" data-hdc-request hidden><span>Simulated HTMX</span><code>GET /fragment → 200</code></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Form, FormField, SubmitButton, TextInput

component = Form(FormField(name='email', label='Email', control=TextInput('email', type='email')), SubmitButton('Subscribe'), action='/subscribe')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

Form is progressively enhanced: ordinary browser submission remains the baseline, while `hx-post`, targets, swaps, sync, and indicators can be added for fragment updates.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Form(*nodes, children=None, action=None, method='post', **native_or_hx_attrs)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional labels, fields, errors, and controls. |
| `children` | `NodeLike | sequence | None` | Keyword child list; combines with positional nodes. |
| `action` | `SafeUrl | str | None` | Validated form endpoint. |
| `method` | `'get' | 'post'` | Native submission method. |
| `**attrs` | `Any` | Validated native or HTMX form attributes. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Form` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Every control needs a label, errors must be associated with controls, and successful submission should produce a perceivable status.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Server-side validation and CSRF checks remain mandatory even when the browser reports validity.
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
