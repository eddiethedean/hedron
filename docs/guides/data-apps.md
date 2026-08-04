# Data applications

Render common Python objects with core `Auto`, then install the data extra for
tabular `DataTable` / `DataEditor`. Charts are **Alpha** — see
[Charts and HTMX](charts-and-htmx.md).

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

## In-memory DataTable (requires `hedron[data]`)

```bash
pip install "hedron[data]"
# optional backends
pip install "hedron-data[pandas]"
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
pip install "hedron-data[sqlalchemy]"
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

Install `hedron[charts]` (**Alpha** — pin and expect churn) and follow
[Charts and HTMX](charts-and-htmx.md).

## See also

- [Data API](../api/DATA.md) · [Data sources](../api/DATA_SOURCE.md)
- [What’s ready](whats-ready.md) (Supported vs Alpha)
