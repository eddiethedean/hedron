---
title: ScatterChart
description: Plot an x/y scatter series from row mappings with an accessible fallback.
---

# `ScatterChart`

Plot an x/y scatter series from row mappings with an accessible fallback.

| | |
|---|---|
| Import | `from hedron_charts import ScatterChart` |
| Distribution | `hedron[charts]` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ScatterChart"><div class="hdc-stage"><figure class="hdc-chart hdc-chart-scatter"><figcaption><strong>ScatterChart output</strong><span>Accessible static preview with a text conclusion.</span></figcaption><div class="hdc-chart-art" role="img" aria-label="Sample chart showing a clear upward pattern"><i></i><i></i><i></i><i></i><i></i></div></figure></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

Install the optional provider before importing this component:

```bash
pip install "hedron[charts]>=0.50.0,<0.51"
```

## Basic use

```python
from hedron_charts import ScatterChart

component = ScatterChart(rows, x='latency', y='errors', title='Latency vs errors', description='Higher latency correlates with elevated error rates.')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

ScatterChart converts the beginner call to a point-mark ChartSpec and renders it through the first-party hedron-chart host with a reviewed SVG fallback and redacted table. It does not select Matplotlib implicitly.

The server-rendered figure, summary, and table remain useful without JavaScript. When the `hedron_charts` plugin assets load, the local `hedron-chart` module progressively enhances that fallback and remounts safely after HTMX swaps.

## Constructor and parameters

```python
ScatterChart(data, *, x, y, title, description=None, alt=None, waiver=None, limits=None)
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

Keep `ScatterChart` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`ScatterChart` renders data the server already prepared. Keep queries, authorization, and redaction on the route or data source — do not treat the component as a place for side effects.

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

[Charts guide](../guides/charts-and-htmx.md) · [Charts API](../api/CHART.md) · [hedron-charts package](../packages/hedron-charts.md)
