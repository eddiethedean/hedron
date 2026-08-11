---
title: AreaChart
description: Plot a filled x/y area series from row mappings with an accessible fallback.
---

# `AreaChart`

Plot a filled x/y area series from row mappings with an accessible fallback.

| | |
|---|---|
| Import | `from hedron_charts import AreaChart` |
| Distribution | `hedron[charts]` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="AreaChart"><div class="hdc-stage"><figure class="hdc-chart"><figcaption><strong>Monthly revenue</strong><span>Revenue rose from January through June.</span></figcaption><svg viewBox="0 0 360 150" role="img" aria-label="Revenue climbs from 18 to 42 thousand dollars"><path d="M20 125 L82 111 L144 91 L206 99 L268 55 L340 24" fill="none" stroke="currentColor" stroke-width="4"/><g fill="currentColor"><circle cx="20" cy="125" r="4"/><circle cx="82" cy="111" r="4"/><circle cx="144" cy="91" r="4"/><circle cx="206" cy="99" r="4"/><circle cx="268" cy="55" r="4"/><circle cx="340" cy="24" r="4"/></g></svg></figure></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

Install the optional provider before importing this component:

```bash
pip install "hedron[charts]>=0.28.2,<0.29"
```

## Basic use

```python
from hedron_charts import AreaChart

component = AreaChart(rows, x='month', y='revenue', title='Monthly revenue', description='Revenue rose from January through June.')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

AreaChart prefers the Matplotlib adapter when installed and otherwise produces a reviewed accessible SVG area plus a redacted table fallback.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
AreaChart(data, *, x, y, title, description=None, alt=None, waiver=None, limits=None)
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

Keep `AreaChart` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`AreaChart` renders data the server already prepared. Keep queries, authorization, and redaction on the route or data source — do not treat the component as a place for side effects.

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
