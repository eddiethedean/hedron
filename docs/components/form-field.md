---
title: FormField
description: Bind a label, help text, required state, and field error to one control.
---

# `FormField`

Bind a label, help text, required state, and field error to one control.

| | |
|---|---|
| Import | `from hedron import FormField` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="FormField"><div class="hdc-stage"><div class="hdc-form"><label for="demo-email">Email address <b>Required</b></label><input id="demo-email" type="email" aria-describedby="demo-email-help"><small id="demo-email-help">We only use this for receipts.</small></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import FormField, TextInput
component = FormField(name='email', label='Email address', control=TextInput('email', type='email'), help='We only use this for receipts.', required=True)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The component copies compatible controls before binding IDs and ARIA attributes, so shared component instances are not mutated. The bound component remains in the normal renderer tree and therefore keeps validation, identity tracking, diagnostics, and nesting behavior. Help and error nodes receive collision-free IDs and are connected with `aria-describedby`; pass `id=` when tests or external markup require a fixed value.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
FormField(*, name, label, control, id=None, help=None, required=False, error=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Stable field key used to derive IDs. |
| `label` | `str` | Visible label. |
| `control` | `NodeLike` | Required control slot. |
| `id` | `str | None` | Optional explicit control ID; otherwise a collision-free request-local ID is generated. |
| `help` | `str | None` | Associated instructions. |
| `required` | `bool` | Required state propagated to compatible controls. |
| `error` | `str | None` | Associated inline error. |

## Composition and backend behavior

Keep `FormField` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`FormField` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

## Accessibility

Write errors as actionable corrections and keep instructions available before an error occurs.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Use the same `name` on the field and its control; avoid hand-authoring conflicting IDs.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
