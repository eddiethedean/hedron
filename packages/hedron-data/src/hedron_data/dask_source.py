"""Bounded Dask/distributed data source adapter."""

from __future__ import annotations

import importlib
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Generic, Protocol, TypeVar, cast

from typing_extensions import TypeIs

from hedron_core.diagnostics import error
from hedron_core.typing_aliases import JsonValue
from hedron_data.plans import TransformPlan, apply_plan_in_memory, plan_from_query
from hedron_data.sources import (
    ColumnSchema,
    DataChanges,
    DataPage,
    DataQuery,
    DataSaveResult,
    FieldError,
)

T = TypeVar("T")

__all__ = ["DaskDataSource", "require_dask"]


class _DaskFrame(Protocol):
    """Minimal Dask/pandas dataframe surface used by the adapter."""

    def sort_values(self, *, by: list[str], ascending: list[bool]) -> _DaskFrame: ...

    def __getitem__(self, key: object) -> _DaskFrame: ...

    @property
    def shape(self) -> tuple[Any, ...]: ...

    def head(self, n: int | float, npartitions: int = ...) -> Any: ...


def require_dask() -> Any:
    try:
        return importlib.import_module("dask.dataframe")
    except ImportError as exc:
        raise error(
            "HED-DATA-0050",
            title="dask extra not installed",
            explanation="DaskDataSource requires dask[dataframe].",
            remediation='Install with: pip install "hedron-data[dask]"',
        ) from exc


def _is_json_value(value: object) -> TypeIs[JsonValue]:
    if value is None or isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, list):
        return all(_is_json_value(item) for item in cast(list[object], value))
    if isinstance(value, dict):
        mapping = cast(dict[object, object], value)
        return all(isinstance(key, str) and _is_json_value(item) for key, item in mapping.items())
    return False


def _row_mapping(row: object) -> Mapping[str, JsonValue]:
    if isinstance(row, Mapping):
        mapping = cast(Mapping[object, object], row)
        return {
            str(key): (value if _is_json_value(value) else str(value))
            for key, value in mapping.items()
        }
    return {}


class DaskDataSource(Generic[T]):
    """Page a Dask dataframe without collecting the full partition set."""

    def __init__(
        self,
        frame: object,
        *,
        schema: Sequence[ColumnSchema] = (),
        to_row: Callable[[Mapping[str, object]], T] | None = None,
        max_compute_rows: int = 500,
        allowlisted_sort_fields: frozenset[str] | None = None,
        allowlisted_filter_fields: frozenset[str] | None = None,
        allowlisted_projection_fields: frozenset[str] | None = None,
        search_fields: Sequence[str] = (),
    ) -> None:
        require_dask()
        self._frame = cast(_DaskFrame, frame)
        self._schema = tuple(schema)
        self._secret_fields = frozenset(column.name for column in self._schema if column.secret)

        def _default_row(row: Mapping[str, object]) -> T:
            # Default codec treats each record mapping as T (caller opts into typed rows).
            return cast(T, dict(row))

        self._to_row = to_row or _default_row
        self._max_compute_rows = max_compute_rows
        # Deny-by-default: omitted allowlists become empty frozensets.
        self._sort_allow: frozenset[str] = (
            frozenset() if allowlisted_sort_fields is None else frozenset(allowlisted_sort_fields)
        )
        self._filter_allow: frozenset[str] = (
            frozenset()
            if allowlisted_filter_fields is None
            else frozenset(allowlisted_filter_fields)
        )
        self._projection_allow: frozenset[str] = (
            frozenset()
            if allowlisted_projection_fields is None
            else frozenset(allowlisted_projection_fields)
        )
        self._search_fields = tuple(search_fields)

    def plan_for(self, query: DataQuery) -> TransformPlan:
        return plan_from_query(query, max_rows=self._max_compute_rows)

    def fetch(self, query: DataQuery) -> DataPage[T]:
        sort_allow = self._sort_allow
        filter_allow = self._filter_allow
        projection_allow = self._projection_allow
        if query.allowlisted_sort_fields is not None:
            sort_allow = sort_allow & frozenset(query.allowlisted_sort_fields)
        if query.allowlisted_filter_fields is not None:
            filter_allow = filter_allow & frozenset(query.allowlisted_filter_fields)
        if query.allowlisted_projection_fields is not None:
            projection_allow = projection_allow & frozenset(query.allowlisted_projection_fields)
        q = DataQuery(
            offset=query.offset,
            limit=query.limit,
            cursor=query.cursor,
            sort=query.sort,
            filters=query.filters,
            projection=query.projection,
            search=query.search,
            locale=query.locale,
            allowlisted_sort_fields=sort_allow,
            allowlisted_filter_fields=filter_allow,
            allowlisted_projection_fields=projection_allow,
        ).validated(max_page_size=self._max_compute_rows)
        if q.projection and self._secret_fields.intersection(q.projection):
            raise error(
                "HED-DATA-0052",
                title="Secret Dask fields cannot be projected",
                explanation="ColumnSchema.secret fields are not returned by normal queries.",
                remediation=(
                    "Remove secret fields from projection or use an explicit privileged path."
                ),
            )
        if q.limit > self._max_compute_rows:
            raise error(
                "HED-DATA-0051",
                title="Dask page exceeds compute budget",
                explanation=f"limit {q.limit} exceeds max_compute_rows {self._max_compute_rows}.",
                remediation="Lower page size or raise an explicit budget.",
            )
        if q.offset + q.limit > self._max_compute_rows:
            raise error(
                "HED-DATA-0051",
                title="Dask page exceeds compute budget",
                explanation=(
                    f"offset+limit {q.offset + q.limit} exceeds "
                    f"max_compute_rows {self._max_compute_rows}."
                ),
                remediation="Lower offset/page size or raise an explicit budget.",
            )
        if q.search and not self._search_fields:
            raise error(
                "HED-DATA-0012",
                title="Dask search requires an allowlist",
                explanation="Deny-by-default: searchable fields must be allowlisted.",
                remediation="Set DaskDataSource.search_fields.",
            )
        frame: _DaskFrame = self._frame
        if q.sort:
            by = [name for name, _ in q.sort]
            ascending = [direction == "asc" for _, direction in q.sort]
            frame = frame.sort_values(by=by, ascending=ascending)
        for name, value in q.filters.items():
            column: Any = frame[name]
            frame = frame[column == value]
        if q.search:
            mask: Any = None
            for name in self._search_fields:
                column: Any = frame[name]
                candidate = column.astype(str).str.contains(
                    q.search, case=False, na=False, regex=False
                )
                mask = candidate if mask is None else mask | candidate
            if mask is not None:
                frame = frame[mask]
        if q.projection:
            frame = frame[list(q.projection)]
        shape0: Any = frame.shape[0]
        total = int(shape0.compute() if hasattr(shape0, "compute") else shape0)
        # Dask DataFrame.iloc does not support positional row slices; take a bounded
        # head window then slice in pandas (still capped by max_compute_rows).
        window = min(q.offset + q.limit, self._max_compute_rows, total)
        if window <= 0:
            records: list[dict[str, object]] = []
        else:
            head: Any = frame.head(window, npartitions=-1)
            if hasattr(head, "compute"):
                head = head.compute()
            raw_records = head.iloc[q.offset : q.offset + q.limit].to_dict(orient="records")
            records = [
                cast(dict[str, object], record) for record in cast(Sequence[object], raw_records)
            ]
        if len(records) > self._max_compute_rows:
            raise error(
                "HED-DATA-0051",
                title="Dask compute returned too many rows",
                explanation="Unbounded collection is forbidden.",
                remediation="Keep transforms server-side and page before compute.",
            )
        rows = [self._to_row(rec) for rec in records]
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
                    message="DaskDataSource is read-oriented; provide an app-owned apply bridge",
                ),
            ),
        )

    def load(self, query: DataQuery) -> DataPage[T]:
        return self.fetch(query)

    def fetch_with_plan(self, plan: TransformPlan) -> list[dict[str, object]]:
        """Apply an explicit plan against a bounded in-memory window.

        Fetches enough rows to honor offset+limit inside the plan without collecting
        the full partition set beyond ``max_compute_rows``.
        """
        offset = 0
        limit = plan.max_rows
        for step in plan.steps:
            if step.op == "offset" and isinstance(step.value, (int, float, str)):
                offset = max(0, int(step.value))
            elif step.op == "sample" and isinstance(step.value, (int, float, str)):
                limit = max(1, int(step.value))
        window = min(offset + limit, self._max_compute_rows)
        sample = self.fetch(DataQuery(offset=0, limit=window))
        mapped = [_row_mapping(row) for row in sample.rows]
        planned = apply_plan_in_memory(mapped, plan)
        return [{str(key): value for key, value in row.items()} for row in planned]
