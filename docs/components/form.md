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

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Form, FormField, SubmitButton, TextInput

component = Form(FormField(name='email', label='Email', control=TextInput('email', type='email')), SubmitButton('Subscribe'), action='/subscribe')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Form is progressively enhanced: ordinary browser submission remains the baseline, while `hx-post`, targets, swaps, sync, and indicators can be added for fragment updates.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

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

## Composition and backend behavior

Keep `Form` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Every control needs a label, errors must be associated with controls, and successful submission should produce a perceivable status.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Server-side validation and CSRF checks remain mandatory even when the browser reports validity.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
