---
title: FormErrors
description: Summarize one or more form-level validation errors.
---

# `FormErrors`

Summarize one or more form-level validation errors.

| | |
|---|---|
| Import | `from hedron import FormErrors` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="FormErrors"><div class="hdc-stage"><div class="hdc-errors" role="alert"><strong>Check the form</strong><ul><li>Email is required.</li><li>Choose a billing plan.</li></ul></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import FormErrors

component = FormErrors(['Email is required.', 'Choose a billing plan.'])
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

An empty sequence renders nothing. Otherwise errors become a list inside an alert region so a failed response is announced.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
FormErrors(errors)
```

| Parameter | Type | Meaning |
|---|---|---|
| `errors` | `Sequence[str]` | Ordered human-readable error messages. |

## Composition and backend behavior

Keep `FormErrors` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Put the summary before the fields and also attach each field-specific error with FormField.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not include raw exception messages or sensitive submitted values.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
