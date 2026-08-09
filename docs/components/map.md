---
title: Map
description: Policy-bounded map with required table alternative.
---

# `Map`

Policy-bounded map with required table alternative.

| | |
|---|---|
| Import | `from hedron import Map` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Map"><div class="hdc-stage"><div class="hdc-result"><strong>Map</strong><span>Policy-bounded map with required table alternative.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Map

component = Map(center=(37.77,-122.42), zoom=10, markers=())
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Map(*, center: 'tuple[float, float]' = (0.0, 0.0), zoom: 'float' = 2.0, width: 'int | None' = None, height: 'int | None' = 360, tile_allowlist: 'Sequence[str]' = (), tiles: 'str | None' = None, attribution: 'str' = '', markers: 'Sequence[MarkerSpec | Mapping[str, Any]]' = (), geojson: 'Mapping[str, Any] | GeoJSONLayer | None' = None, max_features: 'int' = 500, id: 'str | None' = None, class_: 'str | None' = None, mark: 'str | None' = None, **kwargs: 'object') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `center` | `tuple[float, float]` | Map center as `(lat, lon)`. Default: `(0.0, 0.0)`. |
| `zoom` | `float` | Initial map zoom level. Default: `2.0`. |
| `width` | `int | None` | Optional width hint (CSS length or pixels). Default: `None`. |
| `height` | `int | None` | Optional height hint (CSS length or pixels). Default: `360`. |
| `tile_allowlist` | `Sequence[str]` | Allowed tile URL prefixes / hosts. Default: `()`. |
| `tiles` | `str | None` | Optional tile URL template (must pass allowlist checks). Default: `None`. |
| `attribution` | `str` | Map attribution text. Default: `''`. |
| `markers` | `Sequence[MarkerSpec | Mapping[str, Any]]` | Marker specs, mappings, or range tick markers. Default: `()`. |
| `geojson` | `Mapping[str, Any] | GeoJSONLayer | None` | GeoJSON mapping or `GeoJSONLayer` (feature-capped). Default: `None`. |
| `max_features` | `int` | Maximum GeoJSON features rendered. Default: `500`. |
| `id` | `str | None` | Optional DOM `id`. Default: `None`. |
| `class_` | `str | None` | Optional CSS class string (`class` in HTML). Default: `None`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |

## Composition and backend behavior

Keep `Map` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Map` is primarily presentational; keep any mutation on an explicit action or component route.

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
