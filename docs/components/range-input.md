---
title: RangeInput
description: Native range slider input.
---

# `RangeInput`

Native range slider input.

| | |
|---|---|
| Import | `from hedron import RangeInput` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="RangeInput"><div class="hdc-stage"><div class="hdc-form"><label for="demo-range">Volume</label><input id="demo-range" type="range" min="0" max="100" value="40"></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import RangeInput

component = RangeInput('vol', value=50)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
RangeInput(name: 'str', *, id: 'str | None' = None, value: 'float | int | str | None' = None, min: 'float | int | str' = 0, max: 'float | int | str' = 100, step: 'float | int | str | None' = 1, markers: 'Sequence[float | int | str] | None' = None, required: 'bool' = False, disabled: 'bool' = False, mark: 'str | None' = None, aria_describedby: 'str | None' = None, aria_invalid: 'str | None' = None, aria_required: 'str | None' = None, **kwargs: 'object') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Form control `name` submitted with the request. |
| `id` | `str | None` | Optional DOM `id`. Default: `None`. |
| `value` | `float | int | str | None` | Current control value. Default: `None`. |
| `min` | `float | int | str` | Minimum allowed value. Default: `0`. |
| `max` | `float | int | str` | Maximum allowed value. Default: `100`. |
| `step` | `float | int | str | None` | Stepping interval for numeric / temporal inputs. Default: `1`. |
| `markers` | `Sequence[float | int | str] | None` | Marker specs, mappings, or range tick markers. Default: `None`. |
| `required` | `bool` | Whether the control must be filled before submit. Default: `False`. |
| `disabled` | `bool` | Whether the control is non-interactive. Default: `False`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |
| `aria_describedby` | `str | None` | Optional `aria-describedby` id reference. Default: `None`. |
| `aria_invalid` | `str | None` | Optional `aria-invalid` value. Default: `None`. |
| `aria_required` | `str | None` | Optional `aria-required` value. Default: `None`. |

## Composition and backend behavior

Keep `RangeInput` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`RangeInput` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

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
