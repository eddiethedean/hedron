---
title: TextInput
description: Collect a single line of typed text using a constrained input type.
---

# `TextInput`

Collect a single line of typed text using a constrained input type.

| | |
|---|---|
| Import | `from hedron import TextInput` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="TextInput"><div class="hdc-stage"><div class="hdc-form"><label for="demo-text">Email</label><input id="demo-text" type="email" autocomplete="email" placeholder="ada@example.com"></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import TextInput

component = TextInput('email', type='email', autocomplete='email', required=True)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

TextInput uses native constraints and preserves a supplied value during validation re-renders. The finite type set avoids accidentally exposing unsafe or poorly supported input modes.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
TextInput(name, *, id=None, value='', placeholder=None, required=False, type='text', autocomplete=None, disabled=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Submitted field name. |
| `id` | `str | None` | Control ID; defaults from name. |
| `value` | `str` | Current value for re-rendering. |
| `placeholder` | `str | None` | Optional hint. |
| `required` | `bool` | Native required constraint. |
| `type` | `text | email | password | search | tel | url` | Constrained browser input mode. |
| `autocomplete` | `str | None` | Browser autofill token. |
| `disabled` | `bool` | Disable and omit from submission. |

## Composition and backend behavior

Keep `TextInput` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Provide a Label or FormField and use an accurate autocomplete token to help keyboard and assistive-technology users.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Never echo passwords back through `value`, and remember disabled controls are not submitted.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
