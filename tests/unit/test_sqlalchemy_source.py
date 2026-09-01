"""Bounded SQLAlchemy paging for 0.6 closure."""

from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import Session, declarative_base

from hedron_core.diagnostics import HedronError
from hedron_data.sources import ColumnSchema, DataQuery
from hedron_data.sqlalchemy_source import SQLAlchemyDataSource

Base = declarative_base()


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String)


@pytest.fixture()
def session_factory():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all([Item(id=i, name=f"n{i}") for i in range(1, 21)])
        session.commit()

    def factory() -> Session:
        return Session(engine)

    return factory


def test_fetch_applies_limit_offset(session_factory) -> None:
    src = SQLAlchemyDataSource(
        session_factory=session_factory,
        statement=select(Item),
        to_row=lambda r: {"id": r.id, "name": r.name},
    )
    page = src.fetch(DataQuery(offset=5, limit=3))
    assert len(page.rows) == 3
    assert page.rows[0]["id"] == 6
    assert page.total == 20
    assert page.next_offset == 8


def test_rejects_non_select(session_factory) -> None:
    with pytest.raises(HedronError) as exc:
        SQLAlchemyDataSource(
            session_factory=session_factory,
            statement="SELECT 1",  # type: ignore[arg-type]
        )
    assert exc.value.diagnostic.code == "HED-DATA-0011"


def test_sql_contains_limit(session_factory, monkeypatch) -> None:
    """Ensure OFFSET/LIMIT are pushed into the executed statement."""
    executed: list[str] = []
    real_factory = session_factory

    class TrackingSession:
        def __init__(self) -> None:
            self._inner = real_factory()

        def execute(self, statement):
            compiled = statement.compile(compile_kwargs={"literal_binds": True})
            executed.append(str(compiled))
            return self._inner.execute(statement)

        def close(self) -> None:
            self._inner.close()

    src = SQLAlchemyDataSource(
        session_factory=TrackingSession,
        statement=select(Item),
        to_row=lambda r: {"id": r.id},
    )
    src.fetch(DataQuery(offset=2, limit=4))
    assert any("LIMIT" in sql.upper() and "OFFSET" in sql.upper() for sql in executed)


@pytest.mark.parametrize("projection", [("name",), ("id", "name")])
def test_orm_converter_keeps_model_shape_for_projection(session_factory, projection) -> None:
    src = SQLAlchemyDataSource(
        session_factory=session_factory,
        statement=select(Item),
        to_row=lambda r: {"id": r.id, "name": r.name},
    )
    page = src.fetch(
        DataQuery(
            projection=projection,
            allowlisted_projection_fields=frozenset({"id", "name"}),
        )
    )
    assert set(page.rows[0]) == set(projection)


def test_default_converter_preserves_scalar_projection(session_factory) -> None:
    src = SQLAlchemyDataSource(
        session_factory=session_factory,
        statement=select(Item),
    )
    page = src.fetch(
        DataQuery(
            projection=("name",),
            allowlisted_projection_fields=frozenset({"name"}),
        )
    )
    assert page.rows[0] == "n1"


def test_secret_projection_is_rejected_even_when_allowlisted(session_factory) -> None:
    src = SQLAlchemyDataSource(
        session_factory=session_factory,
        statement=select(Item),
        schema=(ColumnSchema("name", "Name", secret=True),),
        to_row=lambda r: {"id": r.id, "name": r.name},
    )
    with pytest.raises(HedronError, match="Secret SQLAlchemy fields"):
        src.fetch(
            DataQuery(
                projection=("name",),
                allowlisted_projection_fields=frozenset({"name"}),
            )
        )


def test_secret_columns_are_removed_before_and_after_codec(session_factory) -> None:
    src = SQLAlchemyDataSource(
        session_factory=session_factory,
        statement=select(Item),
        schema=(ColumnSchema("name", "Name", secret=True),),
        to_row=lambda row: {"id": row.id, "renamed": row.get("name"), "NAME": "blocked"},
    )
    page = src.fetch(DataQuery(limit=1))
    assert page.rows == [{"id": 1, "renamed": None}]


def test_secret_schema_default_converter_returns_public_mapping(session_factory) -> None:
    src = SQLAlchemyDataSource(
        session_factory=session_factory,
        statement=select(Item),
        schema=(ColumnSchema("name", "Name", secret=True),),
    )
    page = src.fetch(DataQuery(limit=1))
    assert page.rows == [{"id": 1}]


def test_secret_schema_rejects_opaque_codec_output(session_factory) -> None:
    src = SQLAlchemyDataSource(
        session_factory=session_factory,
        statement=select(Item),
        schema=(ColumnSchema("name", "Name", secret=True),),
        to_row=lambda row: row.id,
    )
    with pytest.raises(HedronError, match="must return a mapping"):
        src.fetch(DataQuery(limit=1))
