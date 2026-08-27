---
title: ToggleSwitch
description: Switch-styled checkbox control.
---

# `ToggleSwitch`

Switch-styled checkbox control.

| | |
|---|---|
| Import | `from hedron import ToggleSwitch` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ToggleSwitch"><div class="hdc-stage"><label class="hdc-choice"><input type="checkbox" role="switch" checked><span><strong>Email digests</strong><small>Weekly summary</small></span></label></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ToggleSwitch

component = ToggleSwitch('notify', checked=True)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
ToggleSwitch(name: 'str', label: 'str', *, id: 'str | None' = None, checked: 'bool' = False, required: 'bool' = False, disabled: 'bool' = False, mark: 'str | None' = None, aria_describedby: 'str | None' = None, aria_invalid: 'str | None' = None, aria_required: 'str | None' = None, **kwargs: 'object') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Form control `name` submitted with the request. |
| `label` | `str` | Accessible label text shown to users. |
| `id` | `str | None` | Optional DOM `id`. Default: `None`. |
| `checked` | `bool` | Whether a boolean control starts checked. Default: `False`. |
| `required` | `bool` | Whether the control must be filled before submit. Default: `False`. |
| `disabled` | `bool` | Whether the control is non-interactive. Default: `False`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |
| `aria_describedby` | `str | None` | Optional `aria-describedby` id reference. Default: `None`. |
| `aria_invalid` | `str | None` | Optional `aria-invalid` value. Default: `None`. |
| `aria_required` | `str | None` | Optional `aria-required` value. Default: `None`. |

## Composition and backend behavior

Keep `ToggleSwitch` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`ToggleSwitch` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

## Accessibility

Keyboard and screen-reader operable; no-JS fallback required where interactive.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not treat client-only hints (geolocation, browser storage) as authorization.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
