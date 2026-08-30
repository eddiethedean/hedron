---
title: MultiSelect
description: Native multi-select control.
---

# `MultiSelect`

Native multi-select control.

| | |
|---|---|
| Import | `from hedron import MultiSelect` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="MultiSelect"><div class="hdc-stage"><div class="hdc-form"><label for="demo-multi">Teams</label><select id="demo-multi" multiple size="3"><option selected>Platform</option><option selected>Research</option><option>Design</option></select></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import MultiSelect
component = MultiSelect('roles', options=(('a','A'),))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
MultiSelect(name: 'str', options: 'Sequence[tuple[str, str]]', *, id: 'str | None' = None, values: 'Sequence[str] | None' = None, required: 'bool' = False, disabled: 'bool' = False, mark: 'str | None' = None, aria_describedby: 'str | None' = None, aria_invalid: 'str | None' = None, aria_required: 'str | None' = None, **kwargs: 'object') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Form control `name` submitted with the request. |
| `options` | `Sequence[tuple[str, str]]` | Choice list as `(value, label)` pairs (or plain strings where accepted). |
| `id` | `str | None` | Optional DOM `id`. Default: `None`. |
| `values` | `Sequence[str] | None` | Selected or seeded multi-values. Default: `None`. |
| `required` | `bool` | Whether the control must be filled before submit. Default: `False`. |
| `disabled` | `bool` | Whether the control is non-interactive. Default: `False`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |
| `aria_describedby` | `str | None` | Optional `aria-describedby` id reference. Default: `None`. |
| `aria_invalid` | `str | None` | Optional `aria-invalid` value. Default: `None`. |
| `aria_required` | `str | None` | Optional `aria-required` value. Default: `None`. |

## Composition and backend behavior

Keep `MultiSelect` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`MultiSelect` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

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
