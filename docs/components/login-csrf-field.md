---
title: LoginCsrfField
description: Hidden input for pre-auth login CSRF (issue_login_csrf / validate_login_csrf).
---

# `LoginCsrfField`

Hidden input for pre-auth login CSRF (issue_login_csrf / validate_login_csrf).

| | |
|---|---|
| Import | `from hedron import LoginCsrfField` |
| Distribution | `hedron` |
| Backend activity | On submit |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="LoginCsrfField"><div class="hdc-stage"><div class="hdc-result"><strong>LoginCsrfField</strong><span>Hidden input for pre-auth login CSRF (issue_login_csrf / validate_login_csrf).</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import LoginCsrfField

component = LoginCsrfField(session=request.session)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Use on login forms only. Plain CsrfField embeds the post-auth strategy token and will not validate against the login CSRF store.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
LoginCsrfField(*, token=None, session=None, name=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `token` | `str | None` | Explicit login CSRF token. |
| `session` | `MutableMapping | None` | Optional session store for issue_login_csrf. |
| `name` | `str | None` | Field name; defaults to hedron_login_csrf. |

## Composition and backend behavior

Keep `LoginCsrfField` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Pair with validate_login_csrf on POST.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not reuse login tokens after authentication succeeds.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
