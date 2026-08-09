# hedron-charts

Visualization adapters and chart components for Hedron.

**Package maturity:** Alpha · **0.25 status:** source-only / Deferred for adopters
**Flagship extra:** `hedron[charts]` · **Import:** `hedron_charts`  
**Expect churn.** Interactive Plotly/Vega full browser runtimes remain **experimental**.

## Packaging notice

There is currently **no PyPI release compatible with `hedron-core 0.25.x`**. Published
`hedron-charts 0.1.5` requires `hedron-core<0.20`; PyPI's default `0.11.0` requires
`hedron-core==0.11.0`. Do not install `hedron[charts]` or `hedron-charts` into a Hedron
0.25 application. The repository source targets the current workspace and registers
through `hedron.plugins`.

See [Compatibility](../COMPATIBILITY.md#current-025-packaging-limitation-charts-and-sample-kit).

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

Backend extras apply to the repository workspace package; they are not an adopter install
path until a compatible wheel is published.

## When to use

- Beginner line / bar / area / scatter charts over row mappings
- Embedding Matplotlib / Plotly / Altair figures in Hedron pages

Pin local browser runtimes for interactive Plotly/Vega. Host shims **fail closed**
when `window.Plotly` / `window.vegaEmbed` are missing. First-party offline runtime
fingerprinting is not Supported yet.

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
| Installing a published release beside Hedron 0.25 | Resolver conflict; no compatible wheel is published |

## Related docs

- Guide: [Charts and HTMX](../guides/charts-and-htmx.md)
- API: [Charts](../api/CHART.md)
- Components: [Charts overview](../components/charts.md)
- [What’s ready](../guides/whats-ready.md)

## Links

- [PyPI](https://pypi.org/project/hedron-charts/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-charts/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-charts)
