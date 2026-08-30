---
title: ChipInput
description: Free-text chip/tag multivalue input.
---

# `ChipInput`

Free-text chip/tag multivalue input.

| | |
|---|---|
| Import | `from hedron import ChipInput` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ChipInput"><div class="hdc-stage"><div class="hdc-form"><label for="demo-chips">Tags</label><div class="hdc-inline"><span class="hdc-chip">python</span><span class="hdc-chip">htmx</span><input id="demo-chips" type="text" placeholder="Add tag…"></div></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ChipInput

component = ChipInput('tags', values=('a',))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
ChipInput(name: 'str', *, values: 'Sequence[str] | None' = None, id: 'str | None' = None, placeholder: 'str | None' = None, disabled: 'bool' = False, class_: 'str | None' = None, mark: 'str | None' = None, **kwargs: 'object') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Form control `name` submitted with the request. |
| `values` | `Sequence[str] | None` | Selected or seeded multi-values. Default: `None`. |
| `id` | `str | None` | Optional DOM `id`. Default: `None`. |
| `placeholder` | `str | None` | Hint text shown when the control is empty. Default: `None`. |
| `disabled` | `bool` | Whether the control is non-interactive. Default: `False`. |
| `class_` | `str | None` | Optional CSS class string (`class` in HTML). Default: `None`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |

## Composition and backend behavior

Keep `ChipInput` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`ChipInput` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

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
