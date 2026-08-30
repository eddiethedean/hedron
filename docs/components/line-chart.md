---
title: LineChart
description: Plot one x/y series from row mappings with an accessible fallback.
---

# `LineChart`

Plot one x/y series from row mappings with an accessible fallback.

| | |
|---|---|
| Import | `from hedron_charts import LineChart` |
| Distribution | `hedron[charts]` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="LineChart"><div class="hdc-stage"><figure class="hdc-chart"><figcaption><strong>Monthly revenue</strong><span>Revenue rose from January through June.</span></figcaption><svg viewBox="0 0 360 150" role="img" aria-label="Revenue climbs from 18 to 42 thousand dollars"><path d="M20 125 L82 111 L144 91 L206 99 L268 55 L340 24" fill="none" stroke="currentColor" stroke-width="4"/><g fill="currentColor"><circle cx="20" cy="125" r="4"/><circle cx="82" cy="111" r="4"/><circle cx="144" cy="91" r="4"/><circle cx="206" cy="99" r="4"/><circle cx="268" cy="55" r="4"/><circle cx="340" cy="24" r="4"/></g></svg></figure></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

Install the optional provider before importing this component:

```bash
pip install "hedron[charts]>=1.0.0,<1.1"
```

## Basic use

```python
from hedron_charts import LineChart
component = LineChart([{'month': 'Jan', 'revenue': 100}, {'month': 'Feb', 'revenue': 140}], x='month', y='revenue', title='Monthly revenue', description='Revenue rose from January through June.')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

LineChart converts the beginner call to ChartSpec, compiles a deterministic ChartPlan, emits the semantic fallback, and uses the first-party hedron-chart host. It does not select Matplotlib implicitly. Numeric and categorical x values are accepted.

The server-rendered figure, summary, and table remain useful without JavaScript. When the `hedron_charts` plugin assets load, the local `hedron-chart` module progressively enhances that fallback and remounts safely after HTMX swaps.

## Constructor and parameters

```text
LineChart(data, *, x, y, title, description=None, alt=None, waiver=None, limits=None)
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

Keep `LineChart` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`LineChart` renders data the server already prepared. Keep queries, authorization, and redaction on the route or data source — do not treat the component as a place for side effects.

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
