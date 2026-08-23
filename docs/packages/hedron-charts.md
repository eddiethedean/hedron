---
description: Typed first-party charts, deterministic exports, and optional plotting-library adapters.
---

# `hedron-charts`

`hedron-charts` provides Hedron's first-party declarative chart path, four beginner components,
deterministic server exports, and explicit adapters for established Python plotting libraries.

**Package maturity:** Beta · Compatible with published Hedron train `0.60.x`
(`v0.60.0` in-tree; PyPI `v0.59.0` until upload) · **Package version:** `0.2.0`
(pin `>=0.2.0,<0.3`)

**Flagship extra:** `hedron[charts]` · **Import:** `hedron_charts`

First-party `ChartSpec` / `ChartPlan` / `hedron-chart` and the Matplotlib static path are
Supported capabilities. Plotly, Altair, and the wider optional-adapter catalog remain
Experimental explicit opt-ins.

## Install

```bash
pip install "hedron[charts]>=0.60.0,<0.61"

# Or install the independently versioned satellite:
pip install "hedron-charts>=0.2.0,<0.3"
```

Add only the plotting backend your application uses:

```bash
pip install "hedron-charts[matplotlib]>=0.2.0,<0.3"
pip install "hedron-charts[plotly]>=0.2.0,<0.3"
pip install "hedron-charts[altair]>=0.2.0,<0.3"
```

| Extra | Backend |
|---|---|
| `matplotlib` | Matplotlib static SVG/PNG |
| `plotly` | Plotly figure JSON and vendored browser host |
| `altair` | Altair/Vega-Lite and `vl-convert-python` |
| `pydeck` / `folium` | Map adapters |
| `graphviz` / `networkx` | Graph adapters |
| `bokeh` / `holoviews` / `pygal` / `datashader` / `great_tables` | Additional Experimental adapters |
| `all` | Union of all optional backends |

The previous `hedron-charts>=0.1.10,<0.2` line targets older Hedron trains. See
[Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).

## Choose the right surface

| Goal | Surface | Capability status |
|---|---|---|
| Render row mappings as line, area, bar, or scatter | `LineChart`, `AreaChart`, `BarChart`, `ScatterChart` | Supported first-party path |
| Validate and render a declarative chart | `Chart` + `ChartSpec` | Beta API; first-party host |
| Inspect or cache deterministic compilation | `compile_chart` → `ChartPlan` | Beta API |
| Produce authorized SVG, CSV, JSON, or print output | `export_svg`, `export_csv`, `export_json`, `plan_export_bundle` | Beta API |
| Render a Matplotlib figure on the server | `MatplotlibChart` | Supported static path |
| Reuse Plotly or Altair | `PlotlyChart`, `AltairChart` | Experimental explicit opt-in |
| Discover a wider plotting backend | `optional_adapters()` | Adapter-specific; generally Experimental |

The beginner components compile to the first-party `ChartSpec` path. Installing Matplotlib does
not change their renderer implicitly.

## Beginner chart

```python
from hedron_charts import LineChart

chart = LineChart(
    [
        {"month": "Jan", "revenue": 10},
        {"month": "Feb", "revenue": 14},
        {"month": "Mar", "revenue": 18},
    ],
    x="month",
    y="revenue",
    title="Monthly revenue",
    description="Revenue increased throughout the quarter.",
)
```

The server response includes a semantic figure, conclusion, and bounded table fallback. The local
`hedron-chart` module progressively enhances the fallback to SVG or Canvas and remounts after HTMX
swaps. A missing browser module does not erase the server-rendered content.

## Declarative `ChartSpec`

Use a mapping when a chart needs explicit encodings, scales, transforms, interaction policy,
theme, or exports:

```python
from hedron_charts import Chart, compile_chart, parse_chart_spec

spec = parse_chart_spec(
    {
        "schema_version": 1,
        "data": {
            "rows": [
                {"month": "Jan", "revenue": 10},
                {"month": "Feb", "revenue": 14},
                {"month": "Mar", "revenue": 18},
            ],
            "fields": [
                {"name": "month", "type": "string", "key": True},
                {"name": "revenue", "type": "number"},
            ],
        },
        "marks": [
            {
                "type": "line",
                "identity": "monthly-revenue",
                "encodings": {
                    "x": {"field": "month", "type": "string"},
                    "y": {"field": "revenue", "type": "number"},
                },
            }
        ],
        "theme": {"mode": "light", "density": "ordinary"},
        "accessibility": {
            "title": "Monthly revenue",
            "description": "Revenue increased throughout the quarter.",
            "include_table": True,
        },
    }
)

plan = compile_chart(spec)
chart = Chart(spec)
```

`parse_chart_spec()` validates structure. `compile_chart()` additionally applies transforms,
infers domains and guides, chooses a paint mode, builds accessibility output, redacts secret-like
fields, records applied limits, and produces stable spec/data fingerprints.

### Grammar coverage versus paint coverage

The compiler accepts `line`, `area`, `bar`, `point`, `rect`, `rule`, `box`, `arc`, `ohlc`, and
`candlestick` mark types. The current first-party browser host has dedicated family-specific paint
behavior for `line`, `area`, `bar`, and `point`—the four beginner families. Other accepted marks
still compile into a `ChartPlan`, but authors should not assume a specialized browser shape for
them in `0.2.0`; use a reviewed Matplotlib path or an explicit adapter when that visual fidelity is
required.

SVG is the default below 2,500 compiled marks. Canvas is selected at or above that threshold, or
when explicitly requested. The current Canvas host is optimized for dense series; verify the
rendered result for non-series mark families.

The schema records all interaction flags, while the current first-party host directly emits
`hedron-chart-inspect`, `hedron-chart-focus`, `hedron-chart-select`, and
`hedron-chart-reset`. Treat selection and drill intent as user interface signals only—server
authorization and CSRF checks remain mandatory.

## Matplotlib, Plotly, and Altair

```python
from hedron_charts import AltairChart, MatplotlibChart, PlotlyChart

static_chart = MatplotlibChart(
    matplotlib_figure,
    title="Latency distribution",
    description="Most requests complete below 200 ms.",
)

plotly_chart = PlotlyChart(
    plotly_figure,
    title="Requests by region",
    description="US East handles the largest share.",
)

altair_chart = AltairChart(
    altair_chart_object,
    title="Deployments per week",
    description="Deployments peaked in week four.",
)
```

Matplotlib compiles server-side to inert SVG or PNG. Plotly and Altair serialize bounded,
non-executable JSON; their vendored browser hosts are Experimental and fail closed when required
runtimes are unavailable. Callback-shaped values, active SVG, and unapproved remote URLs are
rejected.

## Authorized deterministic exports

```python
from hedron_charts import compile_chart, export_csv, export_json, export_svg

plan = compile_chart(spec)

svg = export_svg(plan, authorized=user_can_export)
csv_text = export_csv(plan, authorized=user_can_export)
json_text = export_json(plan, authorized=user_can_export)
```

Authorize before exporting. The functions default to `authorized=True` for already-authorized
internal calls; route handlers should pass their explicit authorization result. The specification
can disable individual export kinds. `plan_export_bundle()` adds print HTML for enabled plans;
there is no public Python `export_png()` function in `0.2.0`.

## Accessibility checklist

- Supply a useful title and conclusion-oriented description for every chart.
- Keep the tabular fallback unless an equivalent accessible data path exists.
- Do not encode essential distinctions with color alone.
- Make values exposed on hover available through focus, labels, a table, or export.
- Review generated summaries; Hedron does not claim automated insight correctness.

## Security and bounds

| Bound | Default | Enforced by |
|---|---:|---|
| Rows | 10,000 | Compiler, beginner components, and adapters |
| Serialized payload | 1,000,000 bytes | Beginner components and adapters; the advanced compiler records but does not separately measure it |
| Declared fields | 64 | Compiler |
| Transforms | 32 | Compiler |
| Facets | 16 | Compiler when `composition.facet` is a list |
| Compiled marks | 10,000 | Compiler |
| Labels | 500 | Recorded in the plan; no separate label counter yet |
| Export width/height | 4,096 px | Python SVG export |

Unknown schema fields, marks, encodings, scales, and operators fail closed. Prototype-pollution
keys, executable callbacks, remote asset URLs, and active SVG are rejected. Aggregate or redact
application data before constructing a chart; the package only automatically redacts field names
containing `secret` or `password`.

## Test a chart

```python
from hedron import RenderMode, render
from hedron_charts import compile_chart

result = render(chart, mode=RenderMode.FRAGMENT)
assert "<hedron-chart" in result.html
assert "hedron-chart-fallback" in result.html

plan_again = compile_chart(spec)
assert plan.spec_fingerprint == plan_again.spec_fingerprint
```

For browser tests, wait for `hedron-chart[data-hedron-chart-mounted='1']`. For no-JavaScript tests,
assert that the figure, summary, and fallback table remain present before enhancement.

## Errors and failure modes

| Condition | Diagnostic / behavior |
|---|---|
| Missing optional backend | `HED-CHART-0001` with a bounded install command |
| Row or payload limit exceeded | `HED-CHART-0002` / `HED-CHART-0003` |
| Callback, remote URL, or active SVG | `HED-CHART-0004`–`HED-CHART-0006` |
| Unsupported schema, field, mark, encoding, or scale | `HED-CHART-0020`–`HED-CHART-0026` |
| Invalid transform or domain | `HED-CHART-0030`–`HED-CHART-0033` |
| Export unauthorized, disabled, or oversized | `HED-CHART-0061`–`HED-CHART-0063` |
| Prototype-pollution key or structural bound | `HED-CHART-0070`–`HED-CHART-0072` |
| Remote URL in an export bundle | `HED-CHART-0073` |

## Related documentation

- [Charts and HTMX tutorial](../guides/charts-and-htmx.md)
- [Chart API reference](../api/CHART.md)
- [Chart components](../components/charts.md)
- [What’s ready](../guides/whats-ready.md)
- [What’s new in 0.38](../guides/whats-new-0.38.md)
- [RFC-0069](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0069-HIGH-FIDELITY-CHARTS.md)
- [PyPI](https://pypi.org/project/hedron-charts/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-charts/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-charts)
