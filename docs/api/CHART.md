---
status: shipped
---

# Chart APIs


!!! note "Stability (0.10 train)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Shipped in `0.6.0`

## Install

```bash
pip install "hedron[charts]"
# backends (pick one or more):
pip install "hedron-charts[matplotlib]"
pip install "hedron-charts[plotly]"
pip install "hedron-charts[altair]"
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

!!! note "Plotly / Vega runtimes (deferred)"

    Full offline pin/fingerprint/serve of Plotly.js and Vega/vega-embed is
    **Deferred / experimental**. Host scripts fail closed when the globals are
    missing. Supply a local runtime yourself, or use Matplotlib / `LineChart`
    for supported static charts.

Adapters implement a public `VisualizationAdapter` capability contract but may keep backend compilation types internal. Missing optional dependencies produce a precise installation command. Payload limits and server-transform policies are explicit and visible in Explorer.

Walkthrough: [Charts and HTMX](../guides/charts-and-htmx.md).
