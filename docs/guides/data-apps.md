# Data applications

Render common Python objects with core `Auto`, then install the data extra for
tabular `DataTable` / `DataEditor`. On **0.39**, `DataEditor` renders as ABI
`<hedron-data-editor>` with SSR fallback retained after upgrade; bounded
`OptimisticMutation` covers collection/cell edits only (deny-by-default for other
risk classes). See [DATA.md](../api/DATA.md) and [What’s new in 0.40](whats-new-0.41.md).
The charts package is **Beta**: Matplotlib/static is Supported, while Plotly and Altair
browser hosts remain Experimental. See [Charts and HTMX](charts-and-htmx.md).

## Auto (core — no extra)

```python
from hedron import Auto, Hedron, Page, Stack

app = Hedron(title="Data", security="standard", session_secret="replace-me")


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Auto({"name": "Ada", "role": "admin"}),
            Auto([1, 2, 3]),
        ),
        title="Auto",
    )
```

`Auto` picks an inspectable renderer; override or register renderers when you need
control ([Auto API](../api/AUTO.md)).

## HTMX filter demo (html.table — no `hedron[data]` required)

Simulates swapping a region with filter chips. For the real `DataTable` component, install
`hedron[data]` and use the section below.

### Try it (simulated)

=== "Demo"

    Filter chips swap the declared table region. Docs simulation.

    <!-- hedron-sim:data-table-filter -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
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
    ```

## In-memory DataTable (requires `hedron[data]`)

```bash
pip install "hedron[data]>=0.61.0,<0.62"
# optional backends
pip install "hedron-data[pandas]>=0.61.0,<0.62"
```

```python
from hedron import Hedron, Page
from hedron_data import Column, DataTable

app = Hedron(title="Table", security="standard", session_secret="replace-in-production")


@app.page("/")
def home() -> Page:
    return Page(
        DataTable(
            rows=(
                {"id": "1", "name": "Ada"},
                {"id": "2", "name": "Grace"},
            ),
            columns=(Column("id", label="ID"), Column("name", label="Name")),
        ),
        title="People",
    )
```

`InMemoryDataSource` (re-exported from `hedron` when `hedron[data]` is installed) wraps
row sequences behind the same `DataQuery` / `DataPage` protocol used by editors:

```python
from hedron import InMemoryDataSource
from hedron_data import Column, DataEditor, DataQuery

source = InMemoryDataSource(
    rows=[{"id": "1", "name": "Ada"}, {"id": "2", "name": "Grace"}],
    key_field="id",
)
page = source.fetch(DataQuery(page=1, page_size=25))
```

## SQLAlchemy / SQLModel (app-owned sessions)

Install the SQLAlchemy extra. **Your app owns the engine, sessions, and transactions** —
Hedron does not invent an ORM lifecycle.

```bash
pip install "hedron-data[sqlalchemy]>=0.61.0,<0.62"
```

Minimal read-only table over a SQLAlchemy 2.x `Select` (paging uses SQL `OFFSET`/`LIMIT`;
`sort` / `filters` / `search` on `DataQuery` are **not** translated yet and raise
`HED-DATA-0012` if set):

```python
from collections.abc import Iterator
from contextlib import contextmanager

from fastapi import Depends
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from hedron import Hedron, Page
from hedron_data import Column, DataTable
from hedron_data.sqlalchemy_source import SQLAlchemyDataSource

engine = create_engine("sqlite:///./demo.db", future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)


class Base(DeclarativeBase):
    pass


class Person(Base):
    __tablename__ = "people"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]


@contextmanager
def session_scope() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_people_source() -> SQLAlchemyDataSource[dict[str, str]]:
    return SQLAlchemyDataSource(
        session_factory=SessionLocal,
        statement=select(Person),
        row_key="id",
        to_row=lambda row: {"id": row.id, "name": row.name},
    )


app = Hedron(title="People DB", security="standard", session_secret="replace-in-production")


@app.page("/")
def home(source: SQLAlchemyDataSource[dict[str, str]] = Depends(get_people_source)) -> Page:
    from hedron_data import DataQuery

    page = source.fetch(DataQuery(page=1, page_size=25))
    return Page(
        DataTable(
            page=page,
            columns=(Column("id", label="ID"), Column("name", label="Name")),
        ),
        title="People",
    )
```

For editable grids, supply `apply_changes` on `SQLAlchemyDataSource` (or an
`InMemoryDataSource` / custom `DataEditorSource`) and wire CSRF-backed saves as in
[Data](../api/DATA.md) and the [reference app](../examples/reference-app.md).

## Charts

Install `hedron[charts]>=0.61.0,<0.62`; the flagship extra resolves the compatible
`hedron-charts>=0.2.1,<0.3` satellite.
See [Charts and HTMX](charts-and-htmx.md) and
[Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).

## See also

- [Data API](../api/DATA.md) · [Data sources](../api/DATA_SOURCE.md)
- [What’s ready](whats-ready.md) (Supported vs Experimental)
