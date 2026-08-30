import os

from hedron import Hedron, Page, html, swap

app = Hedron(
    title="ConfirmButton demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

row = app.region("confirm-row")


@app.page("/")
def home() -> Page:
    return Page(
        html.div(
            html.div(
                html.strong("Draft report"),
                html.span("Row present until you confirm delete."),
            ),
            html.button(
                "Delete item",
                type="button",
                class_="hedron-button hedron-button-danger hedron-confirm-button",
                **{
                    "hx-confirm": "Delete item?",
                    "hx-delete": "/items/1",
                    "hx-target": row.selector,
                    "hx-swap": "innerHTML",
                },
            ),
            id=row.id,
        ),
        title="ConfirmButton",
    )


@app.action("/items/1", method="DELETE", fragment_regions=(row,))
def delete():
    return swap(
        html.div(
            html.strong("Item deleted"),
            html.span("Row removed after confirm."),
            role="status",
        )
    )
