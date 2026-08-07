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

<!-- hedron-sim:component-form-errors -->

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import FormErrors

component = FormErrors(['Email is required.', 'Choose a billing plan.'])
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

An empty sequence renders nothing. Otherwise errors become a list inside an alert region so a failed response is announced.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

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

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

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
