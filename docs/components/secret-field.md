---
title: SecretField
description: Write-only password editor with explicit keep, replace, and clear operations.
---

# `SecretField`

Write-only password editor with explicit keep, replace, and clear operations.

| | |
|---|---|
| Import | `from hedron import SecretField` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="SecretField"><div class="hdc-stage"><div class="hdc-result"><strong>SecretField</strong><span>Write-only password editor with explicit keep, replace, and clear operations.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import SecretField
component = SecretField('api_key', 'API key', configured=True, allow_clear=True)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

SecretField renders a password replacement control and a keep operation marker without echoing the stored secret. Applications resolve submitted values with `resolve_secret_update` and keep authorization and persistence server-side.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
SecretField(name, label, *, configured=False, allow_clear=False, id=None, class_=None, mark=None, **kwargs)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Base name used for the replacement, operation, and clear fields. |
| `label` | `str` | Accessible label for the password control. |
| `configured` | `bool` | Whether a value is already configured; plaintext is never rendered. |
| `allow_clear` | `bool` | Show the explicit clear action, including its no-JavaScript submit fallback. |
| `id` | `str | None` | Optional stable control id. |
| `class_` | `str | None` | Additional CSS class on the field wrapper. |
| `mark` | `str | None` | Optional stable test mark. |

## Composition and backend behavior

Keep `SecretField` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`SecretField` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

## Accessibility

Keep the label visible and pair validation feedback with the field id; never expose stored secret material in HTML, diagnostics, or history.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not treat the configured marker as the secret value, and do not persist the replacement until the server validates the request.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
