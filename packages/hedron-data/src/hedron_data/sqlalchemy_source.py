"""SQLAlchemy / SQLModel data-source adapters (app owns sessions/transactions)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Generic, Protocol, TypeVar, cast

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


def _column_from_selectable(statement: object, name: str) -> object:
    columns = getattr(statement, "selected_columns", None)
    if columns is not None and name in columns:
        return columns[name]
    raise error(
        "HED-DATA-0013",
        title="SQLAlchemy column not on selectable",
        explanation=f"Column {name!r} is not present on the Select statement.",
        remediation="Include the column in the Select or remove it from the query allowlist.",
    )


class SQLAlchemyDataSource(Generic[T]):
    """Explicit adapter: caller supplies session factory and row codecs.

    ``statement`` must be a SQLAlchemy 2.x ``Select``. Paging is applied with
    ``OFFSET``/``LIMIT`` in SQL — rows are not collected then sliced in Python.

    Sort/filter/search/projection require deny-by-default allowlists and are
    pushed down through an inspectable :class:`TransformPlan`.
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

    def plan_for(self, query: DataQuery) -> TransformPlan:
        return plan_from_query(query)

    def _apply_query(self, statement: object, query: DataQuery) -> object:
        from sqlalchemy import asc, desc, or_

        q = query.validated()
        if q.sort or q.filters or q.search or q.projection:
            if q.sort and q.allowlisted_sort_fields is None:
                raise error(
                    "HED-DATA-0012",
                    title="SQLAlchemy sort requires an allowlist",
                    explanation="Deny-by-default: sort fields must be allowlisted.",
                    remediation="Set DataQuery.allowlisted_sort_fields.",
                )
            if q.filters and q.allowlisted_filter_fields is None:
                raise error(
                    "HED-DATA-0012",
                    title="SQLAlchemy filters require an allowlist",
                    explanation="Deny-by-default: filter fields must be allowlisted.",
                    remediation="Set DataQuery.allowlisted_filter_fields.",
                )
            if (
                q.projection
                and q.allowlisted_projection_fields is None
                and q.allowlisted_filter_fields is None
            ):
                raise error(
                    "HED-DATA-0012",
                    title="SQLAlchemy projection requires an allowlist",
                    explanation="Deny-by-default: projection fields must be allowlisted.",
                    remediation=(
                        "Set DataQuery.allowlisted_projection_fields or allowlisted_filter_fields."
                    ),
                )
            if q.projection:
                allowed = (
                    q.allowlisted_projection_fields or q.allowlisted_filter_fields or frozenset()
                )
                for name in q.projection:
                    if name not in allowed:
                        raise error(
                            "HED-DATA-0012",
                            title="SQLAlchemy projection field not allowlisted",
                            explanation=f"Projection field {name!r} is not allowlisted.",
                            remediation="Add the field to allowlisted_projection_fields.",
                        )
            if q.search and q.allowlisted_filter_fields is None:
                raise error(
                    "HED-DATA-0012",
                    title="SQLAlchemy search requires an allowlist",
                    explanation="Deny-by-default: searchable fields must be allowlisted.",
                    remediation="Set DataQuery.allowlisted_filter_fields.",
                )
        stmt = statement
        for name, direction in q.sort:
            col = _column_from_selectable(stmt, name)
            stmt = stmt.order_by(desc(col) if direction == "desc" else asc(col))  # type: ignore[union-attr]
        for name, value in q.filters.items():
            col = _column_from_selectable(stmt, name)
            stmt = stmt.where(col == value)  # type: ignore[union-attr]
        if q.search:
            clauses = []
            fields = q.allowlisted_filter_fields or frozenset()
            for name in fields:
                col = _column_from_selectable(stmt, name)
                clauses.append(col.ilike(f"%{q.search}%"))  # type: ignore[union-attr]
            if clauses:
                stmt = stmt.where(or_(*clauses))  # type: ignore[union-attr]
        if q.projection:
            cols = [_column_from_selectable(stmt, name) for name in q.projection]
            stmt = stmt.with_only_columns(*cols)  # type: ignore[union-attr]
        return stmt

    def fetch(self, query: DataQuery) -> DataPage[T]:
        from sqlalchemy import func, select

        q = query.validated()
        session = self._session_factory()
        try:
            shaped = self._apply_query(self._statement, q)
            paged = shaped.offset(q.offset).limit(q.limit)  # type: ignore[union-attr]
            result = session.execute(paged)
            rows = _fetch_rows(result)
            mapped = [self._to_row(row) for row in rows]
            count_stmt = select(func.count()).select_from(
                self._apply_query(self._statement, q).order_by(None).subquery()  # type: ignore[union-attr]
            )
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
