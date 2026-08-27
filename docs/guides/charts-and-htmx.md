---
description: Build accessible first-party charts, refresh them with HTMX, and export authorized data.
---

# Charts and HTMX

This guide takes the production path from install to a server-rendered chart, then replaces the
chart through an HTMX fragment without losing its accessible fallback.

## Install the current chart line

```bash
pip install "hedron[charts]>=0.66.2,<0.67"
```

This resolves `hedron-charts>=0.2.1,<0.3`. The plugin entry point registers the first-party
`hedron-chart` module and stylesheet automatically; consuming applications do not need Node.js or
a JavaScript build step.

Use an independent install only when the application does not depend on the flagship package:

```bash
pip install "hedron-charts>=0.2.1,<0.3"
```

## Pick an authoring level

| Starting point | Use it when |
|---|---|
| `LineChart`, `AreaChart`, `BarChart`, `ScatterChart` | One x/y series from row mappings is enough |
| `Chart` + `ChartSpec` | You need explicit encodings, transforms, scales, interaction policy, theme, or export policy |
| `MatplotlibChart` | A reviewed static plotting-library figure is the desired output |
| `PlotlyChart` / `AltairChart` | You explicitly accept an Experimental browser adapter |

The beginner components compile to `ChartSpec`; they do not switch to Matplotlib when that extra
is installed.

## Put a beginner chart on a page

```python
from hedron import Hedron, Page
from hedron_charts import LineChart

app = Hedron(title="Charts", security="standard", session_secret="replace-me")

rows = [
    {"month": "Jan", "revenue": 10},
    {"month": "Feb", "revenue": 14},
    {"month": "Mar", "revenue": 18},
]


@app.page("/")
def home() -> Page:
    return Page(
        LineChart(
            rows,
            x="month",
            y="revenue",
            title="Monthly revenue",
            description="Revenue increased throughout the quarter.",
        ),
        title="Revenue",
    )
```

The returned HTML contains both layers:

1. A server-rendered figure, summary, SVG, and bounded table that work without JavaScript.
2. A `hedron-chart` custom element carrying a compiled `ChartPlan`; the local browser module adds
   SVG or Canvas enhancement when it loads.

That fallback-first structure is also the recovery path if the module fails to load.

## Inspect the compiled plan

Convert a beginner call explicitly when tests, caching, or exports need the normalized plan:

```python
from hedron_charts import beginner_to_spec, compile_chart

spec = beginner_to_spec(
    kind="line",
    data=rows,
    x="month",
    y="revenue",
    title="Monthly revenue",
    description="Revenue increased throughout the quarter.",
)
plan = compile_chart(spec)

assert plan.schema_id == "hedron-chart-spec/1"
assert plan.renderer.paint in {"svg", "canvas"}
assert plan.mark_count == len(rows)
```

`ChartPlan` is immutable and records stable spec/data fingerprints, transformed rows, inferred
domains and guides, renderer choice, warnings, accessibility output, assets, and applied limits.

## Author an advanced chart

The public nested model classes are intentionally not required. Pass a mapping through
`parse_chart_spec()` and let the closed schema validate it:

```python
from hedron_charts import Chart, parse_chart_spec

spec = parse_chart_spec(
    {
        "schema_version": 1,
        "data": {
            "rows": rows,
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
        "interaction": {"inspect": True, "focus_navigation": True, "select": True},
        "export": {"svg": True, "png": False, "csv": True, "json": True},
        "accessibility": {
            "title": "Monthly revenue",
            "description": "Revenue increased throughout the quarter.",
            "include_table": True,
        },
    }
)

chart = Chart(spec)
```

!!! note "Schema coverage is not painter coverage"

    The compiler accepts more mark families than the current browser host paints with dedicated
    shapes. `line`, `area`, `bar`, and `point` have family-specific first-party behavior in
    `0.2.0`. For `rect`, `rule`, `box`, `arc`, `ohlc`, or `candlestick`, inspect the generated
    output and prefer a reviewed Matplotlib figure when specialized fidelity is required. See the
    [API coverage matrix](../api/CHART.md#compiler-contract-versus-current-host-coverage).

## Replace a real chart with HTMX

Give the whole replaceable panel a stable region ID. Return that same outer element from the
fragment route so `hx-swap="outerHTML"` leaves no duplicate IDs. The chart module listens to the
HTMX cleanup and load lifecycle, so a replaced chart is disposed and the new one mounts once.

### Try it

=== "Demo"

    Refresh advances a short chart sequence (then wraps). Docs simulation.

    <!-- hedron-sim:charts-htmx -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import Hedron, InteractionResult, Page, Stack, html
    from hedron_charts import LineChart

    app = Hedron(
        title="Charts HTMX",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    panel = app.region("chart-panel", description="Chart panel")


    INITIAL_ROWS = [
        {"month": "Jan", "revenue": 10},
        {"month": "Feb", "revenue": 14},
        {"month": "Mar", "revenue": 18},
    ]
    UPDATED_ROWS = [
        {"month": "Jan", "revenue": 10},
        {"month": "Feb", "revenue": 14},
        {"month": "Mar", "revenue": 21},
    ]


    def chart_panel(rows, *, description: str):
        return html.section(
            LineChart(
                rows,
                x="month",
                y="revenue",
                title="Monthly revenue",
                description=description,
            ),
            id=panel.id,
            aria={"label": "Revenue chart panel"},
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                chart_panel(
                    INITIAL_ROWS,
                    description="Revenue increased throughout the quarter.",
                ),
                html.button(
                    "Refresh chart panel",
                    type="button",
                    **{
                        "hx-get": "/charts/refresh",
                        "hx-target": panel.selector,
                        "hx-swap": "outerHTML",
                    },
                ),
            ),
            title="Charts",
        )


    @app.view("/charts/refresh", fragment_regions=(panel,))
    def refresh() -> InteractionResult:
        return InteractionResult(
            content=chart_panel(
                UPDATED_ROWS,
                description="March revenue increased to 21 after the refresh.",
            ),
            region_id=panel.id,
            trigger="chartRefreshed",
            cache="vary-htmx",
            explanation="Primary fragment refresh for chart panel",
        )
    ```

The runnable example in the **Code** tab returns a real `LineChart` in both the page and fragment
routes. Use `GET` for a safe chart refresh. If the request changes server state, use an action/POST
route, validate CSRF, authorize on the server, and return only the resulting chart region.

## Export after authorization

Compile once and pass the route's authorization decision into each export:

```python
from hedron_charts import export_csv, export_json, export_svg

plan = compile_chart(spec)

svg = export_svg(plan, authorized=user_can_export)
csv_text = export_csv(plan, authorized=user_can_export)
json_text = export_json(plan, authorized=user_can_export)
```

An unauthorized call raises `HED-CHART-0061`; a format disabled by the spec raises
`HED-CHART-0062`. The Python API generates SVG, CSV, JSON, and print bundle output. PNG remains a
browser-host capability in `0.2.0`.

## Accessibility and data safety

- Write a conclusion-oriented description instead of repeating the title.
- Keep `include_table=True` unless an equivalent accessible data route exists.
- Do not rely on hover or color as the only way to understand a value.
- Redact and aggregate before constructing the chart. Automatic redaction only recognizes field
  names containing `secret` or `password`.
- Treat chart events as UI intent, never as authorization.
- Keep rows, payloads, transforms, marks, facets, and exports within the documented
  [bounds](../api/CHART.md#bounds-and-enforcement).

## Test both rendering layers

```python
from hedron import RenderMode, render

result = render(chart, mode=RenderMode.FRAGMENT)

assert "<hedron-chart" in result.html
assert "data-hedron-payload=" in result.html
assert "hedron-chart-fallback" in result.html
assert "Monthly revenue" in result.html
```

In a browser test, wait for `hedron-chart[data-hedron-chart-mounted='1']`, then assert that the host
contains an `svg` or `canvas`. Also keep the server-only assertions above: a successful browser
mount should not be the only evidence that the chart remains useful.

## Troubleshoot quickly

| Symptom | Check |
|---|---|
| `HED-CHART-0001` | Install the named optional backend extra |
| Empty or stale content after a swap | Replace the stable outer region and include the plugin assets |
| `HED-CHART-0020`–`0026` | Fix the schema version, field, mark, encoding, or scale named by the diagnostic |
| `HED-CHART-0061` / `0062` | Pass an explicit authorization decision and enable the requested format |
| Canvas selected unexpectedly | Inspect `plan.renderer.reason`; 2,500 marks triggers Canvas |
| Plotly or Altair host does not mount | Confirm the explicit adapter extra/runtime; both paths are Experimental |

## Next steps

- [Chart API reference](../api/CHART.md)
- [`hedron-charts` package guide](../packages/hedron-charts.md)
- [Chart component pages](../components/charts.md)
- [Responses](../api/RESPONSES.md)
- [Interaction](../api/INTERACTION.md)
- [Testing](testing.md)
