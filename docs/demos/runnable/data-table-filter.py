import os

from hedron import Hedron, Page, Stack, html, swap

app = Hedron(
    title="People",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

table = app.region("people-table", description="People table")

ROWS = (
    ("1", "Ada", "admin"),
    ("2", "Grace", "member"),
    ("3", "Katherine", "admin"),
    ("4", "Margaret", "member"),
)


def table_panel(filter_role: str | None = None):
    filtered = [r for r in ROWS if filter_role is None or r[2] == filter_role]
    label = "All people" if filter_role is None else f"Role: {filter_role}"
    return html.div(
        html.strong(label),
        html.table(
            html.thead(html.tr(html.th("ID"), html.th("Name"), html.th("Role"))),
            html.tbody(*[html.tr(html.td(a), html.td(b), html.td(c)) for a, b, c in filtered]),
        ),
        id=table.id,
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            table_panel(),
            html.button(
                "All",
                type="button",
                **{"hx-get": "/rows", "hx-target": table.selector, "hx-swap": "outerHTML"},
            ),
            html.button(
                "Admins",
                type="button",
                **{"hx-get": "/rows/admin", "hx-target": table.selector, "hx-swap": "outerHTML"},
            ),
            html.button(
                "Members",
                type="button",
                **{"hx-get": "/rows/member", "hx-target": table.selector, "hx-swap": "outerHTML"},
            ),
        ),
        title="People",
    )


@app.fragment("/rows", region=table)
def all_rows():
    return swap(table_panel())


@app.fragment("/rows/admin", region=table)
def admin_rows():
    return swap(table_panel("admin"))


@app.fragment("/rows/member", region=table)
def member_rows():
    return swap(table_panel("member"))
