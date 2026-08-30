---
title: Pills
description: Pill-styled segmented choice group.
---

# `Pills`

Pill-styled segmented choice group.

| | |
|---|---|
| Import | `from hedron import Pills` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Pills"><div class="hdc-stage"><div class="hdc-inline"><span class="hdc-chip">All</span><span class="hdc-chip">Active</span><span class="hdc-chip">Archived</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Pills
component = Pills('tone', 'Tone', options=(('a','A'),))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Pills(name: 'str', legend: 'str', options: 'Sequence[tuple[str, str]]', *, id: 'str | None' = None, value: 'str | None' = None, required: 'bool' = False, class_: 'str | None' = None, mark: 'str | None' = None, **kwargs: 'object') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Form control `name` submitted with the request. |
| `legend` | `str` | Accessible group legend for related controls. |
| `options` | `Sequence[tuple[str, str]]` | Choice list as `(value, label)` pairs (or plain strings where accepted). |
| `id` | `str | None` | Optional DOM `id`. Default: `None`. |
| `value` | `str | None` | Current control value. Default: `None`. |
| `required` | `bool` | Whether the control must be filled before submit. Default: `False`. |
| `class_` | `str | None` | Optional CSS class string (`class` in HTML). Default: `None`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |

## Composition and backend behavior

Keep `Pills` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Pills` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

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
