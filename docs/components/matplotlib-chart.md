---
title: MatplotlibChart
description: Render a Matplotlib figure as reviewed static SVG or image output.
---

# `MatplotlibChart`

Render a Matplotlib figure as reviewed static SVG or image output.

| | |
|---|---|
| Import | `from hedron_charts import MatplotlibChart` |
| Distribution | `hedron-charts[matplotlib]` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="MatplotlibChart"><div class="hdc-stage"><figure class="hdc-chart hdc-chart-bars"><figcaption><strong>MatplotlibChart output</strong><span>Accessible static preview with a text conclusion.</span></figcaption><div class="hdc-chart-art" role="img" aria-label="Sample chart showing a clear upward pattern"><i></i><i></i><i></i><i></i><i></i></div></figure></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

Install the optional provider before importing this component:

```bash
pip install "hedron-charts[matplotlib]>=0.1.8,<0.2"
```

## Basic use

```python
from hedron_charts import MatplotlibChart

component = MatplotlibChart(fig, title='Latency distribution', description='Most requests complete below 200 ms.')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The adapter compiles the figure server-side and renders inert output, avoiding a browser plotting runtime. SVG passes active-content rejection and output limits.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
MatplotlibChart(figure, *, title=None, description=None, alt=None, waiver=None, fmt='svg')
```

| Parameter | Type | Meaning |
|---|---|---|
| `figure` | `Matplotlib Figure` | Completed figure. |
| `title / description / alt` | `str | None` | Accessible metadata. |
| `waiver` | `str | None` | Reviewed exception. |
| `fmt` | `str` | Static output format. |

## Composition and backend behavior

Keep `MatplotlibChart` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`MatplotlibChart` renders data the server already prepared. Keep queries, authorization, and redaction on the route or data source — do not treat the component as a place for side effects.

## Accessibility

Do not rely only on labels embedded in a dense plot; provide a description and data summary.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Close figures after use in long-running processes and bound image dimensions and complexity.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
