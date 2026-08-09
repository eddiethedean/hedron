---
title: BarChart
description: Plot categorical bars from row mappings with an accessible fallback.
---

# `BarChart`

Plot categorical bars from row mappings with an accessible fallback.

| | |
|---|---|
| Import | `from hedron import BarChart` |
| Distribution | `hedron[charts]` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="BarChart"><div class="hdc-stage"><figure class="hdc-chart hdc-chart-bars"><figcaption><strong>BarChart output</strong><span>Accessible static preview with a text conclusion.</span></figcaption><div class="hdc-chart-art" role="img" aria-label="Sample chart showing a clear upward pattern"><i></i><i></i><i></i><i></i><i></i></div></figure></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

!!! danger "Source-only on Hedron 0.25"

    No published `hedron-charts` release accepts `hedron-core 0.25.x`. This page documents the in-repository workspace package; do not install an older chart release into a 0.25 application. See [Compatibility](../COMPATIBILITY.md#current-025-packaging-limitation-charts-and-sample-kit).

## Basic use

```python
from hedron import BarChart

component = BarChart(rows, x='region', y='requests', title='Requests by region', description='US East handles the largest share.')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

BarChart prefers the Matplotlib adapter when installed and otherwise produces a reviewed accessible SVG bar chart plus a redacted table fallback.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
BarChart(data, *, x, y, title, description=None, alt=None, waiver=None, limits=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `data` | `Sequence[Mapping]` | Bounded rows. |
| `x / y` | `str` | Source field names. |
| `title` | `str` | Required chart title. |
| `description / alt` | `str | None` | Text equivalents. |
| `waiver` | `str | None` | Reviewed accessibility exception. |
| `limits` | `VisualizationLimits | None` | Complexity bounds. |

## Composition and backend behavior

Keep `BarChart` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Supply a conclusion-oriented description and keep the tabular fallback available to users who cannot perceive the plot.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Bound data and never insert raw labels into active SVG or bypass the accessibility contract.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
