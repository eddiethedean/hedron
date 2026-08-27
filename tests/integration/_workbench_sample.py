"""Sample app for runner import-order tests. Reads HEDRON_ROOT_PATH at construction."""

from __future__ import annotations

from hedron import Hedron, Page, Text
from hedron_posit import HedronPosit

app = Hedron(
    title="sample-imported",
    security="standard",
    explorer="off",
    session_secret="test-secret-ok",
)


@app.page("/")
def _imported_home() -> Page:
    return Page(Text("imported"), title="Home")


def create_app() -> Hedron:
    created = Hedron(
        title="sample-factory",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
    )

    @created.page("/")
    def home() -> Page:
        return Page(Text("factory"), title="Home")

    return created


def create_workbench_app() -> HedronPosit:
    created = HedronPosit(
        title="sample-workbench-factory",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
    )

    @created.page("/")
    def workbench_home() -> Page:
        return Page(Text("workbench-factory"), title="Home")

    return created
