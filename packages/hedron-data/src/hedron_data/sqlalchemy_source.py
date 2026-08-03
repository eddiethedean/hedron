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


class SQLAlchemyDataSource(Generic[T]):
    """Explicit adapter: caller supplies session factory and row codecs."""

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
        self._session_factory = session_factory
        self._statement = statement
        self._row_key = row_key
        self._to_row = to_row or (lambda r: r)  # type: ignore[assignment]
        self._apply_changes = apply_changes
        self._schema = tuple(schema)

    def fetch(self, query: DataQuery) -> DataPage[T]:
        q = query.validated()
        session = self._session_factory()
        try:
            result = session.execute(self._statement)
            rows = list(result.scalars().all() if hasattr(result, "scalars") else result.all())
            mapped = [self._to_row(row) for row in rows]
            page = mapped[q.offset : q.offset + q.limit]
            next_offset = q.offset + q.limit if q.offset + q.limit < len(mapped) else None
            return DataPage(
                rows=page,
                schema=self._schema,  # type: ignore[arg-type]
                total=len(mapped),
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
            return self._apply_changes(session, changes)
        finally:
            close = getattr(session, "close", None)
            if callable(close):
                close()

    def load(self, query: DataQuery) -> DataPage[T]:
        return self.fetch(query)
