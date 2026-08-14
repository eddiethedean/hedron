# hedron-charts

Visualization adapters and chart components for Hedron.

**Package maturity:** Beta · **Current compatible release:** `0.1.11` (floor `>=0.1.10`)
**Flagship extra:** `hedron[charts]` · **Import:** `hedron_charts`  
**Expect churn.** Interactive Plotly/Vega full browser runtimes remain **experimental**.

## Planned phase 0.38 upgrade

[RFC-0069](../rfcs/RFC-0069-HIGH-FIDELITY-CHARTS.md) / D-066 defines a substantial
`hedron-charts` `0.2.0` phase after 0.37: typed `ChartSpec` / `ChartPlan`, an ABI-conforming
`hedron-chart` Web Component, a pinned modular D3 renderer, publication-quality SVG/Canvas output,
keyboard/pointer/touch interactions, accessible summaries/tables, responsive themes, deterministic
exports, reviewed visual fixtures, and hard performance/security/lifecycle gates. It is **Planned**,
not available on the current `0.1.11` release. See the
[0.38 acceptance packet](../acceptance/RELEASE_0_38.md).

## Install

```bash
pip install "hedron[charts]>=0.36.0,<0.37"
# Add a backend when needed:
pip install "hedron-charts[matplotlib]>=0.1.10,<0.2"
```

Versions through `0.1.6` target older Hedron cores; keep the `>=0.1.10` floor. See
[Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).

### Optional backends

| Extra | Backend |
|---|---|
| `matplotlib` | Matplotlib static SVG/PNG |
| `plotly` | Plotly figure JSON |
| `altair` | Altair / Vega-Lite (+ vl-convert) |
| `pydeck` / `folium` | Map layers |
| `graphviz` / `networkx` | Graph layouts |
| `bokeh` / `holoviews` / `pygal` / `datashader` / `great_tables` | Additional adapters |
| `all` | Union of the above |

Backend extras are optional and should be installed only for the adapter in use.

## When to use

- Beginner line / bar / area / scatter charts over row mappings
- Embedding Matplotlib / Plotly / Altair figures in Hedron pages

Pin local browser runtimes for interactive Plotly/Vega. Host shims **fail closed**
when `window.Plotly` / `window.vegaEmbed` are missing. First-party offline runtime
pins exist for **Experimental** interactive hosts (`RUNTIME_PINS`); they are not
Supported production Auto defaults.

## Quick start

```python
from hedron_charts import LineChart

chart = LineChart(
    [{"month": "Jan", "revenue": 10}, {"month": "Feb", "revenue": 14}],
    x="month",
    y="revenue",
    title="Monthly revenue",
    description="Revenue increased during the period.",
)
```

`LineChart` falls back to SVG without Matplotlib. Explicit Matplotlib figure:

```python
import matplotlib.pyplot as plt
from hedron_charts import MatplotlibChart

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
chart = MatplotlibChart(fig, alt="y = x squared", description="Quadratic growth")
```

## Surfaces

| Surface | Role |
|---|---|
| `LineChart` / `AreaChart` / `BarChart` / `ScatterChart` | Beginner backend-neutral charts |
| `MatplotlibChart` / `PlotlyChart` / `AltairChart` | Figure / spec wrappers |
| `MatplotlibAdapter` / `PlotlyAdapter` / `AltairAdapter` | Lower-level adapters |
| `compile_figure` / `apply_annotations` | Figure helpers |
| `RUNTIME_PINS` / `pinned_runtime` / `verify_pin` | Optional runtime pin helpers |

Accessibility: charts require title / description / alt (or waiver) contracts —
see [Charts API](../api/CHART.md).

## Errors and failure modes

| Condition | Behavior |
|---|---|
| Missing Plotly / Vega browser runtime | Fail closed (no silent blank interactive chart) |
| Missing a11y title/description/alt | Raise / refuse render per accessibility contract |
| Installing a release older than `0.1.7` beside Hedron 0.27 | Resolver conflict with the older core requirement |

## Related docs

- Guide: [Charts and HTMX](../guides/charts-and-htmx.md)
- API: [Charts](../api/CHART.md)
- Components: [Charts overview](../components/charts.md)
- [What’s ready](../guides/whats-ready.md)
- Planned architecture: [RFC-0069](../rfcs/RFC-0069-HIGH-FIDELITY-CHARTS.md)

## Links

- [PyPI](https://pypi.org/project/hedron-charts/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-charts/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-charts)
