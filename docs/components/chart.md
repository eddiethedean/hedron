---
title: Chart
description: Render a validated ChartSpec through the first-party hedron-chart host.
---

# `Chart`

Render a validated ChartSpec through the first-party hedron-chart host.

| | |
|---|---|
| Import | `from hedron_charts import Chart` |
| Distribution | `hedron[charts]` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Chart"><div class="hdc-stage"><figure class="hdc-chart"><figcaption><strong>Monthly revenue</strong><span>Revenue rose from January through June.</span></figcaption><svg viewBox="0 0 360 150" role="img" aria-label="Revenue climbs from 18 to 42 thousand dollars"><path d="M20 125 L82 111 L144 91 L206 99 L268 55 L340 24" fill="none" stroke="currentColor" stroke-width="4"/><g fill="currentColor"><circle cx="20" cy="125" r="4"/><circle cx="82" cy="111" r="4"/><circle cx="144" cy="91" r="4"/><circle cx="206" cy="99" r="4"/><circle cx="268" cy="55" r="4"/><circle cx="340" cy="24" r="4"/></g></svg></figure></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

Install the optional provider before importing this component:

```bash
pip install "hedron[charts]>=0.43.0,<0.44"
```

## Basic use

```python
from hedron_charts import Chart

component = Chart(spec)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Chart validates and compiles the specification into a deterministic ChartPlan, emits a semantic figure/summary/table fallback, and serializes the plan into the local `hedron-chart` custom element for progressive SVG or Canvas enhancement.

The server-rendered figure, summary, and table remain useful without JavaScript. When the `hedron_charts` plugin assets load, the local `hedron-chart` module progressively enhances that fallback and remounts safely after HTMX swaps.

## Constructor and parameters

```python
Chart(spec=None, *, class_=None, **kwargs)
```

| Parameter | Type | Meaning |
|---|---|---|
| `spec` | `ChartSpec | Mapping[str, Any] | None` | Schema-versioned chart specification; rendering without one raises `ValueError`. |
| `class_` | `str | None` | Optional class on the `hedron-chart` host. |
| `kwargs` | `object` | Forwarded to `ChartProps`; unknown keys are rejected. |

## Composition and backend behavior

Keep `Chart` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Chart` renders data the server already prepared. Keep queries, authorization, and redaction on the route or data source — do not treat the component as a place for side effects.

## Accessibility

Provide a useful title and description in `spec.accessibility`; keep the generated summary and table fallback unless an equivalent accessible path is supplied.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not pass vendor Plotly/Vega dictionaries as ChartSpec or treat chart selection events as authorization.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[Charts guide](../guides/charts-and-htmx.md) · [Charts API](../api/CHART.md) · [hedron-charts package](../packages/hedron-charts.md)
