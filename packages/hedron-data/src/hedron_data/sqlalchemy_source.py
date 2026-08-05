"""SQLAlchemy / SQLModel data-source adapters (app owns sessions/transactions)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Generic, Protocol, TypeVar, cast

from hedron_core.diagnostics import error
from hedron_data.sources import (
    ColumnSchema,
    DataChanges,
    DataPage,
    DataQuery,
    DataSaveResult,
    FieldError,
)

T = TypeVar("T")

__all__ = ["SQLAlchemyDataSource", "require_sqlalchemy"]


class _SQLAlchemyModule(Protocol):
    """Minimal surface used for optional-import presence checks."""


class _SessionLike(Protocol):
    def execute(self, statement: object) -> object: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def close(self) -> None: ...


def require_sqlalchemy() -> _SQLAlchemyModule:
    try:
        import sqlalchemy
    except ImportError as exc:
        raise error(
            "HED-DATA-0010",
            title="sqlalchemy extra not installed",
            explanation="SQLAlchemy adapters require SQLAlchemy.",
            remediation='Install with: pip install "hedron-data[sqlalchemy]"',
        ) from exc
    return cast(_SQLAlchemyModule, sqlalchemy)


def _fetch_rows(result: object) -> list[object]:
    """Return row objects without collapsing multi-column selects via scalars()."""
    keys_fn = getattr(result, "keys", None)
    raw_keys = keys_fn() if callable(keys_fn) else ()
    try:
        keys = list(raw_keys)  # type: ignore[arg-type]
    except TypeError:
        keys = []
    if len(keys) <= 1 and hasattr(result, "scalars"):
        scalars = result.scalars()  # type: ignore[union-attr]
        return list(scalars.all())  # type: ignore[arg-type,union-attr]
    mappings = getattr(result, "mappings", None)
    if callable(mappings):
        mapped = mappings()
        all_fn = getattr(mapped, "all", None)
        if callable(all_fn):
            return list(all_fn())  # type: ignore[arg-type]
    all_fn = getattr(result, "all", None)
    if callable(all_fn):
        return list(all_fn())  # type: ignore[arg-type]
    return []


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
        session_factory: Callable[[], _SessionLike],
        statement: object,
        row_key: str = "id",
        to_row: Callable[[object], T] | None = None,
        apply_changes: Callable[[_SessionLike, DataChanges[T]], DataSaveResult[T]] | None = None,
        schema: Sequence[ColumnSchema] = (),
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
            paged = self._statement.offset(q.offset).limit(q.limit)  # type: ignore[union-attr]
            result = session.execute(paged)
            rows = _fetch_rows(result)
            mapped = [self._to_row(row) for row in rows]
            count_stmt = select(func.count()).select_from(self._statement.order_by(None).subquery())  # type: ignore[union-attr]
            total = int(session.execute(count_stmt).scalar_one())  # type: ignore[union-attr]
            next_offset = q.offset + q.limit if q.offset + q.limit < total else None
            return DataPage(
                rows=mapped,
                schema=self._schema,
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
