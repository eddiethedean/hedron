"""SQLAlchemy TransformPlan pushdown evidence."""

from __future__ import annotations

import pytest

from hedron_core.diagnostics import HedronError


def test_sqlalchemy_allowlisted_pushdown() -> None:
    pytest.importorskip("sqlalchemy")
    from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, select
    from sqlalchemy.orm import Session

    from hedron_data.sources import DataQuery
    from hedron_data.sqlalchemy_source import SQLAlchemyDataSource

    engine = create_engine("sqlite+pysqlite:///:memory:")
    meta = MetaData()
    items = Table(
        "items",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("value", Integer),
    )
    meta.create_all(engine)
    rows = [
        {"id": 1, "name": "a", "value": 2},
        {"id": 2, "name": "b", "value": 1},
    ]
    with engine.begin() as conn:
        conn.execute(items.insert(), rows)

    def factory() -> Session:
        return Session(engine)

    src = SQLAlchemyDataSource(session_factory=factory, statement=select(items))
    page = src.fetch(
        DataQuery(
            limit=10,
            sort=(("value", "asc"),),
            filters={"name": "b"},
            allowlisted_sort_fields=frozenset({"value"}),
            allowlisted_filter_fields=frozenset({"name"}),
        )
    )
    assert page.total == 1
    assert src.plan_for(DataQuery(limit=1)).steps


def test_sqlalchemy_requires_allowlist() -> None:
    pytest.importorskip("sqlalchemy")
    from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, select
    from sqlalchemy.orm import Session

    from hedron_data.sources import DataQuery
    from hedron_data.sqlalchemy_source import SQLAlchemyDataSource

    engine = create_engine("sqlite+pysqlite:///:memory:")
    meta = MetaData()
    items = Table(
        "items2",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", String),
    )
    meta.create_all(engine)

    def factory() -> Session:
        return Session(engine)

    src = SQLAlchemyDataSource(session_factory=factory, statement=select(items))
    with pytest.raises(HedronError):
        src.fetch(DataQuery(sort=(("name", "asc"),)))
