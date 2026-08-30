import os

from fastapi import Request

from hedron import Hedron, Page, Pagination, Stack, html, swap

app = Hedron(
    title="Pagination demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

results = app.region("page-results")
PAGES = {
    1: ("Results 1–3", "Alpha · Bravo · Charlie"),
    2: ("Results 4–6", "Delta · Echo · Foxtrot"),
    3: ("Results 7–9", "Golf · Hotel · India"),
}


def panel(page: int):
    title, detail = PAGES[page]
    return html.div(html.strong(title), html.span(detail), id=results.id)


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            panel(1),
            Pagination(
                page=1,
                page_size=3,
                total=9,
                base_path="/results",
                target=results.selector,
            ),
        ),
        title="Pagination",
    )


@app.view("/results", fragment_regions=(results,))
def page_frag(request: Request):
    page = int(request.query_params.get("page", "1"))
    page = page if page in PAGES else 1
    return swap(panel(page))
