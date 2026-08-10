# Charts and HTMX

A short path from install → chart → Markdown → typed fragment response.

## Availability

```bash
pip install "hedron[charts]>=0.26.0,<0.27"
```

This enforces `hedron-charts>=0.1.6,<0.2`; older satellite releases target older cores.
See [Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).

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

=== "Demo"

    Refresh advances a short chart sequence (then wraps). Docs simulation.

    <!-- hedron-sim:charts-htmx -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import Hedron, InteractionResult, Page, Stack, html

    app = Hedron(
        title="Charts HTMX",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    panel = app.region("chart-panel", description="Chart panel")


    def chart_panel(label: str):
        return html.div(
            html.strong(label),
            html.span("Simple panel stand-in for a chart fragment."),
            id=panel.id,
            role="status",
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                chart_panel("Chart panel"),
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


    @app.component("/charts/refresh", fragment_regions=(panel,))
    def refresh() -> InteractionResult:
        return InteractionResult(
            content=chart_panel("Chart panel updated"),
            region_id=panel.id,
            trigger="chartRefreshed",
            cache="vary-htmx",
            explanation="Primary fragment refresh for chart panel",
        )
    ```

See [Responses](../api/RESPONSES.md), [Interaction](../api/INTERACTION.md), and
[Charts](../api/CHART.md). The [reference application](https://github.com/eddiethedean/hedron/tree/main/examples/reference-app)
includes a phase-06 section and `/charts/*` routes.
