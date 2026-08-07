# Charts and HTMX

A short path from install → chart → Markdown → typed fragment response.

## Install

```bash
pip install "hedron[charts]>=0.1.0,<0.2" "hedron[markdown]>=0.19.0,<0.20"
# optional backends:
pip install "hedron-charts[matplotlib]"   # or plotly / altair
```

## LineChart on a page

```python
from hedron import Hedron, Page, Text
from hedron_charts import LineChart

app = Hedron(title="Charts", security="standard", session_secret="replace-me")

rows = [
    {"month": "Jan", "revenue": 10},
    {"month": "Feb", "revenue": 14},
]


@app.page("/")
def home() -> Page:
    return Page(
        LineChart(
            rows,
            x="month",
            y="revenue",
            title="Monthly revenue",
            description="Revenue increased during the period.",
        ),
        title="Charts",
    )
```

## Markdown beside charts

```python
from hedron import Markdown

Markdown("## Notes\n\nFigures update from the server; no client charting stack required.")
```

## `InteractionResult` fragment

```python
from hedron import InteractionResult, Text

@app.page("/charts/refresh")
def refresh() -> InteractionResult:
    return InteractionResult(
        content=Text("Chart panel updated"),
        trigger="chartRefreshed",
        cache="vary-htmx",
        explanation="Primary fragment refresh for chart panel",
    )
```

Point an HTMX control at `/charts/refresh` with `HX-Request: true` to receive the fragment.

### Try it (simulated)

Refresh swaps a simple chart panel (not a charting library).

<!-- hedron-sim:charts-htmx -->


See [Responses](../api/RESPONSES.md), [Interaction](../api/INTERACTION.md), and
[Charts](../api/CHART.md). The [reference application](https://github.com/eddiethedean/hedron/tree/main/examples/reference-app)
includes a phase-06 section and `/charts/*` routes.
