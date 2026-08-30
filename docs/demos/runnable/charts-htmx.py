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
