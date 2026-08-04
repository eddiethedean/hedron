---
title: RadioGroup
description: Choose exactly one option from a labelled set.
---

# `RadioGroup`

Choose exactly one option from a labelled set.

| | |
|---|---|
| Import | `from hedron import RadioGroup` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="RadioGroup"><div class="hdc-stage"><fieldset class="hdc-choices"><legend>Billing plan</legend><label><input type="radio" name="demo-plan" checked> Free</label><label><input type="radio" name="demo-plan"> Pro</label></fieldset></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import RadioGroup

component = RadioGroup('plan', 'Billing plan', [('free', 'Free'), ('pro', 'Pro')], value='free')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

A native fieldset and legend name the group; every option gets a collision-free ID, shared name, value, and associated label. Pass `id=` only when outside markup must use a predictable prefix.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
RadioGroup(name, legend, options, *, id=None, value=None, required=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Shared submitted field name. |
| `legend` | `str` | Group label. |
| `options` | `Sequence[tuple[str, str]]` | Value/label pairs. |
| `id` | `str | None` | Optional option-ID prefix; generated collision-free by default. |
| `value` | `str | None` | Selected option. |
| `required` | `bool` | Require one selection. |

## Composition and backend behavior

Keep `RadioGroup` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep option labels parallel and make the legend a complete question or category.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Use Select when the option set is long or screen space is constrained.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
