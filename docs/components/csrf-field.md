---
title: CsrfField
description: Hidden CSRF input wired to the active strategy or an explicit token.
---

# `CsrfField`

Hidden CSRF input wired to the active strategy or an explicit token.

| | |
|---|---|
| Import | `from hedron import CsrfField` |
| Distribution | `hedron` |
| Backend activity | On submit |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="CsrfField"><div class="hdc-stage"><div class="hdc-result"><strong>CsrfField</strong><span>Hidden CSRF input wired to the active strategy or an explicit token.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import CsrfField

component = CsrfField(token=csrf_token_for_request(request, policy))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Use inside Form for POST/HTMX mutations. Prefer explicit token= in portable/offline renders. Not for login CSRF — use LoginCsrfField.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
CsrfField(*, name=None, token=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str | None` | Form field name; defaults to the strategy / RenderContext field. |
| `token` | `str | None` | Token value; when omitted, uses RenderContext.csrf_token on FastAPI pages. |

## Composition and backend behavior

Keep `CsrfField` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

The field is aria-hidden by nature as a hidden input; pair with visible validation feedback on failure.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Never log or display the token value in diagnostics.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
