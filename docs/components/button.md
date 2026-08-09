---
title: Button
description: Trigger an in-page or server command with a native button.
---

# `Button`

Trigger an in-page or server command with a native button.

| | |
|---|---|
| Import | `from hedron import Button` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Button"><div class="hdc-stage"><button class="hdc-button hdc-primary" type="button" data-hdc-action="count">Archive project <span data-hdc-count>0</span></button><p role="status" data-hdc-status>Ready.</p></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Button

component = Button('Archive project', type='button', variant='danger')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Button retains native keyboard activation and form behavior and maps the selected variant to a stable theme class. Use a higher-level action binding when the command calls the server.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Button(label, *, type='button', disabled=False, variant='primary')
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Visible command label. |
| `type` | `button | submit | reset` | Native button behavior. |
| `disabled` | `bool` | Prevent activation. |
| `variant` | `primary | secondary | danger` | Finite semantic styling variant. |

## Composition and backend behavior

Keep `Button` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Button` participates in interaction markup. Pair it with an explicit `@action` / `@component` POST (and CSRF) when the control mutates state.

## Accessibility

Use a verb that states the result. Disabled controls need nearby explanation when the reason is not obvious.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Use Link or LinkButton for navigation; a button should perform an action.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
