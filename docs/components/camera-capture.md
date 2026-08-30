---
title: CameraCapture
description: Camera capture file input (capture=environment).
---

# `CameraCapture`

Camera capture file input (capture=environment).

| | |
|---|---|
| Import | `from hedron import CameraCapture` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="CameraCapture"><div class="hdc-stage"><label class="hdc-file"><span class="hdc-file-icon" aria-hidden="true">C</span><strong>Camera capture</strong><small>capture=environment · permission/retention policy required</small><input type="file" accept="image/*" capture="environment"></label></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import CameraCapture
component = CameraCapture(name='photo')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
CameraCapture(*, name: 'str' = 'camera', label: 'str' = 'Capture media', accept: 'str' = 'video/*', capture: "Literal['user', 'environment']" = 'environment', class_: 'str | None' = None, **kwargs: 'object') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Form control `name` submitted with the request. Default: `'camera'`. |
| `label` | `str` | Accessible label text shown to users. Default: `'Capture media'`. |
| `accept` | `str` | File `accept` filter (MIME / extension list). Default: `'video/*'`. |
| `capture` | `Literal['user', 'environment']` | Media capture facing mode (`user` or `environment`). Default: `'environment'`. |
| `class_` | `str | None` | Optional CSS class string (`class` in HTML). Default: `None`. |

## Composition and backend behavior

Keep `CameraCapture` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`CameraCapture` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

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
