"""SQLAlchemy / SQLModel data-source adapters (app owns sessions/transactions)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Generic, TypeVar

from hedron_core.diagnostics import error
from hedron_data.sources import (
    DataChanges,
    DataPage,
    DataQuery,
    DataSaveResult,
    FieldError,
)

T = TypeVar("T")

__all__ = ["SQLAlchemyDataSource", "require_sqlalchemy"]


def require_sqlalchemy() -> Any:
    try:
        import sqlalchemy
    except ImportError as exc:
        raise error(
            "HED-DATA-0010",
            title="sqlalchemy extra not installed",
            explanation="SQLAlchemy adapters require SQLAlchemy.",
            remediation='Install with: pip install "hedron-data[sqlalchemy]"',
        ) from exc
    return sqlalchemy


def _fetch_rows(result: Any) -> list[Any]:
    """Return row objects without collapsing multi-column selects via scalars()."""
    keys_fn = getattr(result, "keys", None)
    raw_keys: Any = keys_fn() if callable(keys_fn) else ()
    keys = list(raw_keys)
    if len(keys) <= 1 and hasattr(result, "scalars"):
        return list(result.scalars().all())
    mappings = getattr(result, "mappings", None)
    if callable(mappings):
        mapped: Any = mappings()
        all_fn = getattr(mapped, "all", None)
        if callable(all_fn):
            rows: Any = all_fn()
            return list(rows)
    return list(result.all())


class SQLAlchemyDataSource(Generic[T]):
    """Explicit adapter: caller supplies session factory and row codecs.

    ``statement`` must be a SQLAlchemy 2.x ``Select``. Paging is applied with
    ``OFFSET``/``LIMIT`` in SQL — rows are not collected then sliced in Python.

    ``sort`` / ``filters`` / ``search`` on :class:`DataQuery` are not translated
    to SQL yet; non-empty values raise ``HED-DATA-0012``.
    """

    def __init__(
        self,
        *,
        session_factory: Callable[[], Any],
        statement: Any,
        row_key: str = "id",
        to_row: Callable[[Any], T] | None = None,
        apply_changes: Callable[[Any, DataChanges[T]], DataSaveResult[T]] | None = None,
        schema: Sequence[Any] = (),
    ) -> None:
        require_sqlalchemy()
        from sqlalchemy.sql import Select

        if not isinstance(statement, Select):
            raise error(
                "HED-DATA-0011",
                title="SQLAlchemy statement must be a Select",
                explanation=(
                    f"Got {type(statement)!r}; bounded paging requires sqlalchemy.sql.Select."
                ),
                remediation="Pass select(Model) or an equivalent Select statement.",
            )
        self._session_factory = session_factory
        self._statement = statement
        self._row_key = row_key
        self._to_row = to_row or (lambda r: r)  # type: ignore[assignment]
        self._apply_changes = apply_changes
        self._schema = tuple(schema)

    def fetch(self, query: DataQuery) -> DataPage[T]:
        from sqlalchemy import func, select

        q = query.validated()
        if q.sort or q.filters or q.search or q.projection:
            raise error(
                "HED-DATA-0012",
                title="SQLAlchemyDataSource does not support sort/filters/search/projection yet",
                explanation=(
                    "DataQuery.sort, filters, search, and projection would silently return "
                    "unscoped pages; they are rejected instead."
                ),
                remediation=(
                    "Apply sorting/filtering/projection in the Select statement, or use "
                    "InMemoryDataSource for client-side query features."
                ),
            )
        session = self._session_factory()
        try:
            paged = self._statement.offset(q.offset).limit(q.limit)
            result = session.execute(paged)
            rows = _fetch_rows(result)
            mapped = [self._to_row(row) for row in rows]
            count_stmt = select(func.count()).select_from(self._statement.order_by(None).subquery())
            total = int(session.execute(count_stmt).scalar_one())
            next_offset = q.offset + q.limit if q.offset + q.limit < total else None
            return DataPage(
                rows=mapped,
                schema=self._schema,  # type: ignore[arg-type]
                total=total,
                next_offset=next_offset,
            )
        finally:
            close = getattr(session, "close", None)
            if callable(close):
                close()

    def apply(self, changes: DataChanges[T]) -> DataSaveResult[T]:
        if self._apply_changes is None:
            return DataSaveResult(
                ok=False,
                errors=(
                    FieldError(
                        row_key=None,
                        field=None,
                        message="SQLAlchemyDataSource.apply_changes was not provided",
                    ),
                ),
            )
        session = self._session_factory()
        try:
            result = self._apply_changes(session, changes)
            commit = getattr(session, "commit", None)
            rollback = getattr(session, "rollback", None)
            if result.ok:
                if callable(commit):
                    commit()
            elif callable(rollback):
                rollback()
            return result
        except Exception:
            rollback = getattr(session, "rollback", None)
            if callable(rollback):
                rollback()
            raise
        finally:
            close = getattr(session, "close", None)
            if callable(close):
                close()

    def load(self, query: DataQuery) -> DataPage[T]:
        return self.fetch(query)
