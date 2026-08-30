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
component = Button('Archive project', type='button', variant='danger', size='sm', width='full')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Button retains native keyboard activation and form behavior and maps the selected variant to stable theme markers. In 0.59, `size`, `appearance`, `emphasis`, and `width` share the presentation vocabulary, while `attrs=` provides a validated seam for integration attributes. Use a higher-level action binding when the command calls the server.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Button(label, *, type='button', disabled=False, variant='primary', size=None, appearance=None, emphasis=None, width=None, leading_icon=None, id=None, class_=None, attrs=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Visible command label. |
| `type` | `button | submit | reset` | Native button behavior. |
| `disabled` | `bool` | Prevent activation. |
| `variant` | `primary | secondary | danger` | Finite semantic styling variant. |
| `size` | `sm | md | lg | None` | Shared control size marker. |
| `appearance` | `solid | outline | soft | ghost | plain | raised | None` | Treatment independent of meaning. |
| `emphasis` | `primary | secondary | danger | neutral | None` | Semantic meaning independent of treatment. |
| `width` | `content | field | full | None` | Shared width intent. |
| `leading_icon` | `str | None` | Optional registered icon name. |
| `attrs` | `Mapping[str, HtmlAttrValue] | None` | Validated global, ARIA, data, approved HTMX, and popover/dialog-trigger attributes. |

## Composition and backend behavior

Keep `Button` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Button` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

## Accessibility

Use a verb that states the result. Disabled controls need nearby explanation when the reason is not obvious.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Use Link or LinkButton for navigation; a button should perform an action. `attrs=` does not allow `style`, `on*`, `hx-on*`, component-owned `type`/`disabled`/`id`/`class`, malformed ARIA/data names, or non-allowlisted HTMX attributes.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
