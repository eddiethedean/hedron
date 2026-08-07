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
