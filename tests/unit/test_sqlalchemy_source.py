"""Bounded SQLAlchemy paging for 0.6 closure."""

from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import Session, declarative_base

from hedron_core.diagnostics import HedronError
from hedron_data.sources import DataQuery
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

        def execute(self, statement):  # noqa: ANN001
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
