---
title: PlotlyChart
description: Render a Plotly figure through Hedron's bounded adapter pipeline.
---

# `PlotlyChart`

Render a Plotly figure through Hedron's bounded adapter pipeline.

| | |
|---|---|
| Import | `from hedron import PlotlyChart` |
| Distribution | `hedron-charts[plotly]` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="PlotlyChart"><div class="hdc-stage"><figure class="hdc-chart hdc-chart-donut"><figcaption><strong>PlotlyChart output</strong><span>Accessible static preview with a text conclusion.</span></figcaption><div class="hdc-chart-art" role="img" aria-label="Sample chart showing a clear upward pattern"><i></i><i></i><i></i><i></i><i></i></div></figure></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

Install the optional provider before importing this component:

```bash
pip install "hedron-charts[plotly]"
```

## Basic use

```python
from hedron import PlotlyChart

component = PlotlyChart(fig, title='Requests by region', description='US East handles the largest share.')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The adapter compiles the figure into the supported static or browser representation, enforces visualization limits, and attaches accessible metadata and fallback content.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
PlotlyChart(figure, *, title=None, description=None, alt=None, waiver=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `figure` | `Plotly figure` | Figure specification. |
| `title / description / alt` | `str | None` | Accessible metadata. |
| `waiver` | `str | None` | Reviewed exception. |

## Composition and backend behavior

Keep `PlotlyChart` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Make hover-only values available through labels or a table and ensure keyboard users can reach any enabled controls.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not pass untrusted custom HTML, JavaScript callbacks, or unbounded traces.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
