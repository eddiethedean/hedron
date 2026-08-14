---
status: beta
---

# Chart APIs


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Shipped in `0.6.0`; high-fidelity first-party line in **`0.38` / `hedron-charts` `0.2.0`**

!!! info "Phase 0.38 first-party charts"

    [RFC-0069](../rfcs/RFC-0069-HIGH-FIDELITY-CHARTS.md) / D-066: typed `ChartSpec` / `ChartPlan`,
    ABI-conforming `hedron-chart`, SVG/Canvas rendering, accessible fallbacks, and deterministic
    export. Beginner `LineChart` / `AreaChart` / `BarChart` / `ScatterChart` compile to the new
    grammar. `MatplotlibChart` remains Supported; Plotly/Altair stay Experimental.

## Availability

Install `hedron[charts]>=0.38.0,<0.39` (or `hedron-charts>=0.2.0,<0.3`). See
[Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).

### Advanced `Chart(spec=...)`

```python
from hedron_charts import Chart, ChartSpec

spec = {
    "schema_version": 1,
    "data": {"rows": [{"x": 1, "y": 2}, {"x": 2, "y": 5}]},
    "marks": [{"type": "line", "encodings": {"x": {"field": "x"}, "y": {"field": "y"}}}],
    "accessibility": {"title": "Trend", "description": "Demo line"},
}
page_chart = Chart(spec)
```

## Beginner `LineChart`

```python
from hedron import Hedron, Page
from hedron_charts import LineChart

app = Hedron(title="Demo", security="standard", session_secret="replace-me")

data = [
    {"month": "Jan", "revenue": 10},
    {"month": "Feb", "revenue": 14},
    {"month": "Mar", "revenue": 18},
]


@app.page("/")
def home() -> Page:
    return Page(
        LineChart(
            data,
            x="month",
            y="revenue",
            title="Monthly revenue",
            description="Revenue increased during the period.",
        ),
        title="Revenue",
    )
```

## Familiar-library adapters

```python
from hedron_charts import AltairChart, MatplotlibChart, PlotlyChart

PlotlyChart(figure, description="Revenue by region")
MatplotlibChart(figure, alt="Revenue by month")
AltairChart(chart, description="Declarative Vega-Lite figure")
```

Every chart declares title, description or alt text, output mode, data policy, and optional tabular fallback. Interactive adapters register host shims and serialize specifications as non-executable data. Raw JavaScript callbacks and unapproved remote assets are rejected by default.

!!! note "Plotly / Vega runtimes (Experimental)"

    Interactive Plotly.js and Vega/vega-embed runtimes ship as **vendored,
    fingerprinted Experimental** assets under `hedron-charts` (`RUNTIME_PINS`).
    Host scripts fail closed when `window.Plotly` / `vegaEmbed` are missing.
    They are **not** production Auto defaults (`INTERACTIVE-028`); opt in with
    `Auto(..., as_="plotly")` / explicit `PlotlyChart` / `AltairChart`.
    Supported production charts remain Matplotlib / beginner static charts.

Adapters implement a public `VisualizationAdapter` capability contract but may keep backend compilation types internal. Missing optional backend extras produce a precise installation command for the **workspace** package — not a PyPI `hedron[charts]` pin on 0.25. Payload limits and server-transform policies are explicit and visible in Explorer.

Walkthrough: [Charts and HTMX](../guides/charts-and-htmx.md). For PyPI dashboards without charts, see [Streamlit migration](../guides/streamlit-migration.md).
