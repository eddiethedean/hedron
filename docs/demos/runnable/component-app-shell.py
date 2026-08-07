import os

from hedron import AppShell, Hedron, Nav, NavLink, Page, html, swap

app = Hedron(
    title="AppShell demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

panel = app.region("comp-main-panel")


def panel_body(name: str, detail: str):
    return html.div(html.strong(name), html.span(detail))


@app.page("/")
def home() -> Page:
    return Page(
        AppShell(
            nav=Nav(
                NavLink("Home", "/home", target=panel.selector, swap="innerHTML", active=True),
                NavLink("Reports", "/reports", target=panel.selector, swap="innerHTML"),
                NavLink("Settings", "/settings", target=panel.selector, swap="innerHTML"),
            ),
            body=panel_body("Home", "Overview metrics stay in MainPanel."),
            panel_id=panel.id,
        ),
        title="AppShell",
    )


@app.fragment("/home", region=panel)
def home_frag():
    return swap(panel_body("Home", "Overview metrics stay in MainPanel."))


@app.fragment("/reports", region=panel)
def reports_frag():
    return swap(panel_body("Reports", "Reports fragment swapped into the panel."))


@app.fragment("/settings", region=panel)
def settings_frag():
    return swap(panel_body("Settings", "Settings fragment; side nav stays put."))
