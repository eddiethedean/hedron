# hedron-charts

[![PyPI](https://img.shields.io/pypi/v/hedron-charts.svg)](https://pypi.org/project/hedron-charts/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-charts.svg)](https://pypi.org/project/hedron-charts/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Typed first-party charts, deterministic exports, and optional plotting-library adapters for
Hedron.

Beginner `LineChart` / `BarChart` / `AreaChart` / `ScatterChart`, Matplotlib static
SVG/PNG, Plotly interactive JSON, and Altair/Vega-Lite specifications.

**Package maturity:** Beta · **Package version:** `0.2.0`

Interactive Plotly/Vega **full browser runtimes** remain **experimental**: Hedron
ships host shims that fail closed when `window.Plotly` / `window.vegaEmbed` are
missing. Applications may supply pinned local runtimes; first-party offline
runtime pins exist for **Experimental** interactive hosts and are not Supported
production Auto defaults.

## Phase 0.38 first-party charts

Phase **0.38** ships `hedron-charts` **`0.2.0`** with typed `ChartSpec` / `ChartPlan`, an
ABI-conforming `hedron-chart` Web Component, semantic server fallbacks, SVG by default, Canvas for
dense series, core inspect/focus/select/reset events, deterministic server exports, and bounded
payloads. The current host has dedicated paint behavior for line, area, bar, and point; broader
schema acceptance does not imply a specialized painter. Matplotlib remains Supported;
Plotly/Altair stay Experimental. See
[RFC-0069](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0069-HIGH-FIDELITY-CHARTS.md)
and the
[phase 0.38 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_38.md).

## Install

```bash
# flagship extra:
pip install "hedron[charts]>=0.56.0,<0.57"
# independent satellite:
pip install "hedron-charts>=0.2.0,<0.3"
# Add a backend when needed:
pip install "hedron-charts[matplotlib]>=0.2.0,<0.3"
```

Pin the living charts line at `>=0.2.0,<0.3` on the 0.51 train.
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

## Choose an entry point

| Need | Use | Runtime |
|---|---|---|
| A line, area, bar, or scatter chart from row mappings | `LineChart`, `AreaChart`, `BarChart`, `ScatterChart` | First-party `hedron-chart`; useful server fallback without JavaScript |
| A validated declarative specification | `Chart` + `ChartSpec` | First-party `hedron-chart` |
| A server-rendered Matplotlib figure | `MatplotlibChart` | Static SVG or PNG; no browser plotting runtime |
| An existing Plotly or Altair figure | `PlotlyChart` / `AltairChart` | Vendored browser runtime; Experimental explicit opt-in |

The beginner components do not select Matplotlib automatically. They compile to the first-party
`ChartSpec` / `ChartPlan` path.

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

The response contains a semantic figure, summary, and bounded table fallback. The local
`hedron-chart` module progressively enhances it to SVG or Canvas and remounts after HTMX swaps.

For an explicit Matplotlib figure:

```python
import matplotlib.pyplot as plt
from hedron_charts import MatplotlibChart

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
chart = MatplotlibChart(fig, alt="y = x squared", description="Quadratic growth")
```

## Advanced specification and export

```python
from hedron_charts import Chart, compile_chart, export_csv, parse_chart_spec

spec = parse_chart_spec(
    {
        "data": {
            "rows": [
                {"month": "Jan", "revenue": 10},
                {"month": "Feb", "revenue": 14},
            ]
        },
        "marks": [
            {
                "type": "line",
                "encodings": {
                    "x": {"field": "month", "type": "string"},
                    "y": {"field": "revenue", "type": "number"},
                },
            }
        ],
        "accessibility": {
            "title": "Monthly revenue",
            "description": "Revenue increased from January to February.",
        },
    }
)

chart = Chart(spec)
plan = compile_chart(spec)
csv_text = export_csv(plan, authorized=user_can_export)
```

Unknown schema fields, mark types, encoding channels, scales, and transform operators fail closed
with `HED-CHART-*` diagnostics. Perform export authorization in application code; the default
`authorized=True` argument is intended for already-authorized internal calls.

The compiler also accepts advanced mark families, guide metadata, and interaction flags that the
`0.2.0` browser host does not yet paint or operate with dedicated behavior. Review the
[runtime coverage matrix](https://hedron.readthedocs.io/en/latest/api/CHART/#compiler-contract-versus-current-host-coverage)
before choosing the first-party host for advanced visualizations.

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/hedron-charts/)
- [Chart API](https://hedron.readthedocs.io/en/latest/api/CHART/)
- [Chart components](https://hedron.readthedocs.io/en/latest/components/charts/)
- [Charts and HTMX](https://hedron.readthedocs.io/en/latest/guides/charts-and-htmx/)
- [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-charts/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-charts)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [`hedron-core`](https://pypi.org/project/hedron-core/) ·
  [`hedron`](https://pypi.org/project/hedron/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
