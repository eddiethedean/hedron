---
title: GeolocationButton
description: Spoofable geolocation form fields with progressive enhancement.
---

# `GeolocationButton`

Spoofable geolocation form fields with progressive enhancement.

| | |
|---|---|
| Import | `from hedron import GeolocationButton` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="GeolocationButton"><div class="hdc-stage"><button class="hdc-button" type="button">Share location</button><p class="hdc-muted">Spoofable form fields — not authorization.</p></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import GeolocationButton

component = GeolocationButton()
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
GeolocationButton(*, label: 'str' = 'Share location', lat_name: 'str' = 'lat', lon_name: 'str' = 'lon', accuracy_name: 'str' = 'accuracy', class_: 'str | None' = None, mark: 'str | None' = None, **kwargs: 'object') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Accessible label text shown to users. Default: `'Share location'`. |
| `lat_name` | `str` | Form field name for latitude. Default: `'lat'`. |
| `lon_name` | `str` | Form field name for longitude. Default: `'lon'`. |
| `accuracy_name` | `str` | Form field name for reported accuracy. Default: `'accuracy'`. |
| `class_` | `str | None` | Optional CSS class string (`class` in HTML). Default: `None`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |

## Composition and backend behavior

Keep `GeolocationButton` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`GeolocationButton` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

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
