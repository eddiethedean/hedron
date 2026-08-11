# hedron-charts

[![PyPI](https://img.shields.io/pypi/v/hedron-charts.svg)](https://pypi.org/project/hedron-charts/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-charts.svg)](https://pypi.org/project/hedron-charts/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Visualization adapters and chart components for Hedron.

Beginner `LineChart` / `BarChart` / `AreaChart` / `ScatterChart`, Matplotlib static
SVG/PNG, Plotly interactive JSON, and Altair/Vega-Lite specifications.

**Package maturity:** Beta · **0.28-compatible release:** `0.1.10`

Interactive Plotly/Vega **full browser runtimes** remain **experimental**: Hedron
ships host shims that fail closed when `window.Plotly` / `window.vegaEmbed` are
missing. Applications may supply pinned local runtimes; first-party offline
runtime pins exist for **Experimental** interactive hosts and are not Supported
production Auto defaults.

## Install

```bash
pip install "hedron[charts]>=0.28.2,<0.29"
# Add a backend when needed:
pip install "hedron-charts[matplotlib]>=0.1.10,<0.2"
```

Versions through `0.1.6` may target older Hedron cores; keep the `>=0.1.10` floor for
the living 0.28 train. See
[Compatibility](https://hedron.readthedocs.io/en/latest/COMPATIBILITY/#charts-and-sample-kit-compatibility-floor).

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

`LineChart` falls back to SVG without Matplotlib. For an explicit Matplotlib figure:

```python
import matplotlib.pyplot as plt
from hedron_charts import MatplotlibChart

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
chart = MatplotlibChart(fig, alt="y = x squared", description="Quadratic growth")
```

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/hedron-charts/)
- [Charts and HTMX](https://hedron.readthedocs.io/en/latest/guides/charts-and-htmx/)
- [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-charts/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-charts)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [`hedron-core`](https://pypi.org/project/hedron-core/) ·
  [`hedron`](https://pypi.org/project/hedron/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
