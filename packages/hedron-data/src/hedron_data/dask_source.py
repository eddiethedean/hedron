"""Bounded Dask/distributed data source adapter."""

from __future__ import annotations

import importlib
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Generic, TypeVar, cast

from hedron_core.diagnostics import error
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


class DaskDataSource(Generic[T]):
    """Page a Dask dataframe without collecting the full partition set."""

    def __init__(
        self,
        frame: object,
        *,
        schema: Sequence[ColumnSchema] = (),
        to_row: Callable[[Mapping[str, object]], T] | None = None,
        max_compute_rows: int = 500,
    ) -> None:
        require_dask()
        self._frame = frame
        self._schema = tuple(schema)

        def _default_row(row: Mapping[str, object]) -> T:
            return cast(T, dict(row))

        self._to_row = to_row or _default_row
        self._max_compute_rows = max_compute_rows

    def plan_for(self, query: DataQuery) -> TransformPlan:
        return plan_from_query(query, max_rows=self._max_compute_rows)

    def fetch(self, query: DataQuery) -> DataPage[T]:
        q = query.validated(max_page_size=self._max_compute_rows)
        if q.limit > self._max_compute_rows:
            raise error(
                "HED-DATA-0051",
                title="Dask page exceeds compute budget",
                explanation=f"limit {q.limit} exceeds max_compute_rows {self._max_compute_rows}.",
                remediation="Lower page size or raise an explicit budget.",
            )
        frame = self._frame
        if q.sort:
            by = [name for name, _ in q.sort]
            ascending = [direction == "asc" for _, direction in q.sort]
            frame = frame.sort_values(by=by, ascending=ascending)  # type: ignore[union-attr]
        for name, value in q.filters.items():
            frame = frame[frame[name] == value]  # type: ignore[index]
        if q.projection:
            frame = frame[list(q.projection)]  # type: ignore[index]
        total = int(frame.shape[0].compute())  # type: ignore[union-attr]
        page = frame.loc[q.offset : q.offset + q.limit - 1]  # type: ignore[union-attr]
        records = page.compute().to_dict(orient="records")  # type: ignore[union-attr]
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
        """Apply an explicit plan against a bounded in-memory sample only."""
        sample = self.fetch(DataQuery(limit=min(plan.max_rows, self._max_compute_rows)))
        rows = [cast(Mapping[str, object], row) for row in sample.rows]
        return apply_plan_in_memory(rows, plan)  # type: ignore[arg-type]
