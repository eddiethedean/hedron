---
title: CircularProgress
description: Circular determinate/indeterminate progress with status text.
---

# `CircularProgress`

Circular determinate/indeterminate progress with status text.

| | |
|---|---|
| Import | `from hedron import CircularProgress` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="CircularProgress"><div class="hdc-stage"><div class="hdc-progress" role="status" aria-label="Upload 50 percent"><svg viewBox="0 0 36 36" width="48" height="48" aria-hidden="true"><circle cx="18" cy="18" r="15" fill="none" stroke="currentColor" stroke-opacity="0.2" stroke-width="3"/><circle cx="18" cy="18" r="15" fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="47 94" transform="rotate(-90 18 18)"/></svg><span>50%</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import CircularProgress

component = CircularProgress(value=50)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
CircularProgress(value: 'float | None' = None, *, maximum: 'float' = 100, label: 'str | None' = None, indeterminate: 'bool' = False, id: 'str | None' = None, class_: 'str | None' = None, mark: 'str | None' = None, **kwargs: 'Any') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `value` | `float | None` | Current control value. Default: `None`. |
| `maximum` | `float` | Upper bound for progress or rating scales. Default: `100`. |
| `label` | `str | None` | Accessible label text shown to users. Default: `None`. |
| `indeterminate` | `bool` | Whether progress is indeterminate (ignores `value`). Default: `False`. |
| `id` | `str | None` | Optional DOM `id`. Default: `None`. |
| `class_` | `str | None` | Optional CSS class string (`class` in HTML). Default: `None`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |

## Composition and backend behavior

Keep `CircularProgress` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`CircularProgress` is primarily presentational; keep any mutation on an explicit action or component route.

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
