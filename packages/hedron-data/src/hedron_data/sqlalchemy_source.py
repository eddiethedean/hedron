"""SQLAlchemy / SQLModel data-source adapters (app owns sessions/transactions)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any, Generic, Protocol, TypeVar, cast, runtime_checkable

from hedron_core.diagnostics import error
from hedron_data.plans import TransformPlan, plan_from_query
from hedron_data.sources import (
    ColumnSchema,
    DataChanges,
    DataPage,
    DataQuery,
    DataSaveResult,
    FieldError,
    reject_unsupported_cursor,
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


@runtime_checkable
class _HasAll(Protocol):
    def all(self) -> Iterable[object]: ...


@runtime_checkable
class _HasScalars(Protocol):
    def scalars(self) -> _HasAll: ...


@runtime_checkable
class _HasMappings(Protocol):
    def mappings(self) -> _HasAll: ...


@runtime_checkable
class _HasKeys(Protocol):
    def keys(self) -> Iterable[object]: ...


@runtime_checkable
class _SelectableStatement(Protocol):
    def order_by(self, *args: object) -> _SelectableStatement: ...

    def where(self, *args: object) -> _SelectableStatement: ...

    def with_only_columns(self, *args: object) -> _SelectableStatement: ...

    def offset(self, value: int) -> _SelectableStatement: ...

    def limit(self, value: int) -> _SelectableStatement: ...

    def subquery(self) -> object: ...


@runtime_checkable
class _HasScalarOne(Protocol):
    def scalar_one(self) -> object: ...


@runtime_checkable
class _ColumnElement(Protocol):
    def ilike(self, other: object, escape: str | None = None) -> object: ...


class _PublicRow(dict[str, object]):
    """Mapping/attribute view containing only columns safe for a row codec."""

    def __getattr__(self, name: str) -> object:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


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
    # Empty Protocol: any imported module structurally satisfies the presence check.
    return sqlalchemy


def _fetch_rows(result: object) -> list[object]:
    """Return row objects without collapsing multi-column selects via scalars()."""
    keys: list[object] = []
    keys_ok = False
    if isinstance(result, _HasKeys):
        try:
            keys = list(result.keys())
            keys_ok = True
        except TypeError:
            keys = []
    if keys_ok and len(keys) == 1 and isinstance(result, _HasScalars):
        return list(result.scalars().all())
    if isinstance(result, _HasMappings):
        return list(result.mappings().all())
    if isinstance(result, _HasAll):
        return list(result.all())
    return []


def _column_from_selectable(statement: object, name: str) -> _ColumnElement:
    columns = getattr(statement, "selected_columns", None)
    if columns is not None and name in columns:
        col = columns[name]
        if isinstance(col, _ColumnElement):
            return col
        # Host-selected columns always expose comparison/ilike at runtime.
        return cast(_ColumnElement, col)
    raise error(
        "HED-DATA-0013",
        title="SQLAlchemy column not on selectable",
        explanation=f"Column {name!r} is not present on the Select statement.",
        remediation="Include the column in the Select or remove it from the query allowlist.",
    )


def _as_selectable(statement: object) -> _SelectableStatement:
    if isinstance(statement, _SelectableStatement):
        return statement
    raise error(
        "HED-DATA-0011",
        title="SQLAlchemy statement must be a Select",
        explanation=f"Got {type(statement)!r}; bounded paging requires sqlalchemy.sql.Select.",
        remediation="Pass select(Model) or an equivalent Select statement.",
    )


def _as_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        return int(value)
    return int(str(value))


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
        search_fields: Sequence[str] = (),
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
        self._statement: object = statement
        self._row_key = row_key

        def _identity(row: object) -> T:
            # Default codec: row object is already T when the caller omits to_row.
            return cast(T, row)

        self._to_row = to_row or _identity
        self._has_custom_to_row = to_row is not None
        self._apply_changes = apply_changes
        self._schema = tuple(schema)
        self._secret_fields = frozenset(column.name for column in self._schema if column.secret)
        self._secret_fields_folded = frozenset(name.casefold() for name in self._secret_fields)
        self._search_fields = tuple(search_fields)

    def plan_for(self, query: DataQuery) -> TransformPlan:
        return plan_from_query(query)

    def _apply_query(
        self,
        statement: object,
        query: DataQuery,
        *,
        include_projection: bool = True,
    ) -> _SelectableStatement:
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
            if q.search and not self._search_fields:
                raise error(
                    "HED-DATA-0012",
                    title="SQLAlchemy search requires an allowlist",
                    explanation="Deny-by-default: searchable fields must be allowlisted.",
                    remediation="Set SQLAlchemyDataSource.search_fields.",
                )
        stmt = _as_selectable(statement)
        for name, direction in q.sort:
            col: Any = _column_from_selectable(stmt, name)
            stmt = stmt.order_by(desc(col) if direction == "desc" else asc(col))
        for name, value in q.filters.items():
            col: Any = _column_from_selectable(stmt, name)
            stmt = stmt.where(col == value)
        if q.search:
            clauses: list[Any] = []
            fields = self._search_fields
            # Escape LIKE metacharacters so user % / _ cannot broaden matches.
            escaped = q.search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            pattern = f"%{escaped}%"
            for name in fields:
                col = _column_from_selectable(stmt, name)
                clauses.append(col.ilike(pattern, escape="\\"))
            if clauses:
                stmt = stmt.where(or_(*clauses))
        projection_folded = {name.casefold() for name in q.projection or ()}
        if projection_folded.intersection(self._secret_fields_folded):
            raise error(
                "HED-DATA-0052",
                title="Secret SQLAlchemy fields cannot be projected",
                explanation="ColumnSchema.secret fields are never exposed by projections.",
                remediation="Remove secret fields from projection or use an app-owned bridge.",
            )
        if q.projection and include_projection:
            cols: list[Any] = [_column_from_selectable(stmt, name) for name in q.projection]
            stmt = stmt.with_only_columns(*cols)
        return stmt

    def _without_secret_columns(self, statement: _SelectableStatement) -> _SelectableStatement:
        columns = getattr(statement, "selected_columns", None)
        public: list[object] = []
        if columns is not None:
            for column in columns:
                raw_name = getattr(column, "key", None) or getattr(column, "name", None)
                if (
                    raw_name is not None
                    and str(raw_name).casefold() not in self._secret_fields_folded
                ):
                    public.append(column)
        if not public:
            raise error(
                "HED-DATA-0052",
                title="SQLAlchemy source has no public selectable columns",
                explanation="All selectable columns are secret or cannot be safely identified.",
                remediation="Select at least one named public column for ordinary fetches.",
            )
        return statement.with_only_columns(*public)

    def _public_codec_rows(self, result: object) -> list[object]:
        if not isinstance(result, _HasMappings):
            raise error(
                "HED-DATA-0052",
                title="SQLAlchemy secret redaction requires named rows",
                explanation="The SQLAlchemy result cannot expose a named public-column mapping.",
                remediation="Use a Select with named public columns and a mapping row codec.",
            )
        return [
            _PublicRow(
                {
                    str(key): value
                    for key, value in cast(Mapping[object, object], row).items()
                    if str(key).casefold() not in self._secret_fields_folded
                }
            )
            for row in result.mappings().all()
        ]

    def _sanitize_row(self, row: object) -> object:
        if not self._secret_fields:
            return row
        if isinstance(row, Mapping):
            mapping = cast(Mapping[object, object], row)
            return {
                str(key): value
                for key, value in mapping.items()
                if str(key).casefold() not in self._secret_fields_folded
            }
        # An opaque object may still carry a secret attribute; require a mapping codec so
        # the adapter can prove secret fields were removed before returning the page.
        raise error(
            "HED-DATA-0052",
            title="SQLAlchemy row codec must return a mapping",
            explanation=(
                "A secret-bearing SQLAlchemy source cannot verify redaction for an opaque row."
            ),
            remediation="Configure to_row to return a mapping with public fields only.",
        )

    def fetch(self, query: DataQuery) -> DataPage[T]:
        from sqlalchemy import func, select

        q = query.validated()
        reject_unsupported_cursor(q, source="SQLAlchemyDataSource")
        session = self._session_factory()
        try:
            # A custom codec receives the same unprojected shape for every projection.
            # Secret-bearing sources are narrowed in SQL before any codec can observe them.
            project_after_codec = self._has_custom_to_row or bool(self._secret_fields)
            shaped = self._apply_query(
                self._statement,
                q,
                include_projection=not project_after_codec,
            )
            if self._secret_fields:
                shaped = self._without_secret_columns(shaped)
            paged = shaped.offset(q.offset).limit(q.limit)
            result = session.execute(paged)
            rows = self._public_codec_rows(result) if self._secret_fields else _fetch_rows(result)
            mapped: list[T] = [cast(T, self._sanitize_row(self._to_row(row))) for row in rows]
            if q.projection and project_after_codec:
                if any(not isinstance(row, Mapping) for row in mapped):
                    raise error(
                        "HED-DATA-0052",
                        title="Projected SQLAlchemy rows must be mappings",
                        explanation="Projection is applied after to_row and requires named fields.",
                        remediation="Configure to_row to return a mapping for projected queries.",
                    )
                mapped = cast(
                    list[T],
                    [
                        {
                            name: cast(Mapping[object, object], row).get(name)
                            for name in q.projection
                        }
                        for row in mapped
                    ],
                )
            # subquery() is a FromClause at runtime; accept via Any for select_from stubs.
            count_from: Any = (
                self._apply_query(self._statement, q, include_projection=False)
                .order_by(None)
                .subquery()
            )
            count_stmt = select(func.count()).select_from(count_from)
            count_result = session.execute(count_stmt)
            if isinstance(count_result, _HasScalarOne):
                total = _as_int(count_result.scalar_one())
            else:
                scalar = getattr(count_result, "scalar_one", None)
                total = _as_int(scalar()) if callable(scalar) else 0
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
