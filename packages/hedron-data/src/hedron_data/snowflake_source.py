"""Snowflake-backed bounded data source."""

from __future__ import annotations

import importlib
from collections.abc import Callable, Sequence
from typing import Any, Generic, TypeVar

from hedron_core.diagnostics import error
from hedron_data.plans import TransformPlan, plan_from_query
from hedron_data.sources import (
    ColumnSchema,
    DataChanges,
    DataPage,
    DataQuery,
    DataSaveResult,
    FieldError,
)

T = TypeVar("T")

__all__ = ["SnowflakeDataSource", "require_snowflake"]


def require_snowflake() -> Any:
    try:
        return importlib.import_module("snowflake.connector")
    except ImportError as exc:
        raise error(
            "HED-DATA-0060",
            title="snowflake extra not installed",
            explanation="SnowflakeDataSource requires snowflake-connector-python.",
            remediation='Install with: pip install "hedron-data[snowflake]"',
        ) from exc


class SnowflakeDataSource(Generic[T]):
    """Execute app-owned parameterized SQL with LIMIT/OFFSET budgets."""

    def __init__(
        self,
        *,
        connection_factory: Callable[[], Any],
        statement: str,
        schema: Sequence[ColumnSchema] = (),
        to_row: Callable[[dict[str, Any]], T] | None = None,
        max_page_size: int = 100,
        params: Sequence[Any] | None = None,
    ) -> None:
        if "select" not in statement.lower():
            raise error(
                "HED-DATA-0061",
                title="Snowflake statement must be a SELECT",
                explanation="Mutating SQL is not accepted through the data source.",
                remediation="Pass a SELECT and apply mutations through an app-owned bridge.",
            )
        self._connection_factory = connection_factory
        self._statement = statement
        self._schema = tuple(schema)
        self._to_row = to_row or (lambda r: r)  # type: ignore[assignment]
        self._max_page_size = max_page_size
        self._params = tuple(params or ())

    def plan_for(self, query: DataQuery) -> TransformPlan:
        return plan_from_query(query, max_rows=self._max_page_size)

    def fetch(self, query: DataQuery) -> DataPage[T]:
        q = query.validated(max_page_size=self._max_page_size)
        sql = f"SELECT * FROM ({self._statement}) AS hedron_src LIMIT %s OFFSET %s"
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            try:
                cur.execute(sql, (*self._params, q.limit, q.offset))
                colnames = [col[0] for col in (cur.description or [])]
                raw_rows = cur.fetchmany(q.limit)
                rows = [
                    self._to_row({colnames[i]: value for i, value in enumerate(row)})
                    for row in raw_rows
                ]
                count_sql = f"SELECT COUNT(*) FROM ({self._statement}) AS hedron_src"
                cur.execute(count_sql, self._params)
                total = int(cur.fetchone()[0])  # type: ignore[index]
            finally:
                cur.close()
        finally:
            close = getattr(conn, "close", None)
            if callable(close):
                close()
        return DataPage(
            rows=rows,
            schema=self._schema,
            total=total,
            next_offset=q.offset + q.limit if q.offset + q.limit < total else None,
        )

    def apply(self, changes: DataChanges[T]) -> DataSaveResult[T]:
        return DataSaveResult(
            ok=False,
            errors=(
                FieldError(
                    row_key=None,
                    field=None,
                    message="SnowflakeDataSource.apply requires an app-owned mutation bridge",
                ),
            ),
        )

    def load(self, query: DataQuery) -> DataPage[T]:
        return self.fetch(query)
