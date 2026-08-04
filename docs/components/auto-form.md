---
title: AutoForm
description: Generate a labelled form from a typed FormModel and optionally submit it through HTMX.
---

# `AutoForm`

Generate a labelled form from a typed FormModel and optionally submit it through HTMX.

| | |
|---|---|
| Import | `from hedron import AutoForm` |
| Distribution | `hedron` |
| Backend activity | On submit |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="AutoForm"><div class="hdc-stage"><form class="hdc-form" data-hdc-form><label>Email address<input name="email" type="email" required placeholder="ada@example.com"></label><button class="hdc-button hdc-primary" type="submit">Submit</button></form><p role="status" aria-live="polite" data-hdc-status>Nothing submitted yet.</p></div><div class="hdc-request" data-hdc-request hidden><span>Simulated HTMX</span><code>GET /fragment → 200</code></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import AutoForm

component = AutoForm(InviteMember, action='/invite', csrf_token=csrf_token, submit_label='Send invite')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

AutoForm derives field labels and required state from model metadata, adds error and CSRF nodes, and uses normal form submission as its baseline. Obtain `csrf_token` with `csrf_token_for_request(request, policy)` after a safe GET. For HTMX-targeted POSTs, prefer the explicit Form loop in the [forms and actions guide](../guides/forms-and-actions.md).

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
AutoForm(model, *, action, method='post', csrf_token=None, values=None, errors=(), submit_label='Submit', target=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `model` | `type[FormModel] | FormModel` | Field schema or populated instance. |
| `action` | `SafeUrl | str` | Validated endpoint. |
| `method` | `str` | GET or POST behavior. |
| `csrf_token` | `str | None` | Hidden CSRF value from `csrf_token_for_request`; required for POST. |
| `values` | `Mapping` | Values restored after validation. |
| `errors` | `Sequence[str]` | Form-level errors. |
| `submit_label` | `str` | Primary action label. |
| `target` | `safe CSS selector | None` | HTMX response target (prefer explicit Form composition when using hx-target). |

## Composition and backend behavior

Keep `AutoForm` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Review generated labels and add model titles that make domain-specific fields understandable.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Generation does not replace authorization, CSRF validation, or server-side model validation. Do not leave `csrf_token` undefined.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
