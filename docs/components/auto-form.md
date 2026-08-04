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

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import AutoForm

component = AutoForm(InviteMember, action='/invite', csrf_token=csrf_token, submit_label='Send invite')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

AutoForm derives field labels and required state from model metadata, adds error and CSRF nodes, and uses normal form submission as its baseline. Obtain `csrf_token` with `csrf_token_for_request(request, policy)` after a safe GET. For HTMX-targeted POSTs, prefer the explicit Form loop in the [forms and actions guide](../guides/forms-and-actions.md).

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

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

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `AutoForm` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Review generated labels and add model titles that make domain-specific fields understandable.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Generation does not replace authorization, CSRF validation, or server-side model validation. Do not leave `csrf_token` undefined.
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
