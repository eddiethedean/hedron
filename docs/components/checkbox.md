---
title: Checkbox
description: Collect one boolean choice with its visible label.
---

# `Checkbox`

Collect one boolean choice with its visible label.

| | |
|---|---|
| Import | `from hedron import Checkbox` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Checkbox"><div class="hdc-stage"><label class="hdc-choice hdc-choice-card"><input type="checkbox"><span><strong>Service terms</strong><small>I agree to the acceptable-use and data policies.</small></span></label></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Checkbox

component = Checkbox('terms', 'I agree to the service terms', required=True)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Checkbox emits the input and its associated label in a wrapper. Unchecked HTML checkboxes submit no value, so the server model must define the false/default behavior.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Checkbox(name, label, *, id=None, checked=False, required=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Submitted field name. |
| `label` | `str` | Visible label next to the box. |
| `id` | `str | None` | Control ID. |
| `checked` | `bool` | Current checked state. |
| `required` | `bool` | Require the box to be checked. |

## Composition and backend behavior

Keep `Checkbox` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Checkbox` participates in interaction markup. Pair it with an explicit `@action` / `@component` POST (and CSRF) when the control mutates state.

## Accessibility

Use positive, unambiguous wording that makes the checked state clear.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use a single checkbox for mutually exclusive choices; use RadioGroup.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
