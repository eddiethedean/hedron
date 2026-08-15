"""Bounded Auto data inspection."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, cast

from hedron_core.auto.spec import DataIntelligenceReport
from hedron_core.data import DataSource, is_lazy_source
from hedron_core.diagnostics import error

_MAX_INSPECT_ROWS = 200
_MAX_INSPECT_COLS = 50


def _rows_from_datasource(value: DataSource) -> list[Mapping[str, object]]:
    return [dict(row) for row in value.inspect_rows(max_rows=_MAX_INSPECT_ROWS)]


def _rows_from_columnar(value: object) -> list[Mapping[str, object]] | None:
    """Duck-type pandas/polars-like tables without importing those packages."""
    head_fn = getattr(value, "head", None)
    if not callable(head_fn) or getattr(value, "columns", None) is None:
        return None
    sample = head_fn(_MAX_INSPECT_ROWS)
    to_dicts = getattr(sample, "to_dicts", None)
    if callable(to_dicts):
        raw = to_dicts()
        if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
            return [dict(row) for row in raw if isinstance(row, Mapping)]
    to_dict = getattr(sample, "to_dict", None)
    if callable(to_dict):
        try:
            records = to_dict("records")
        except TypeError:
            records = to_dict()
        if isinstance(records, list):
            return [dict(row) for row in records if isinstance(row, Mapping)]
    return None


def inspect_data(value: object) -> DataIntelligenceReport:
    """Bounded schema/size/cardinality inspection; refuses unbounded lazy collect."""
    notes: list[str] = []
    rows: list[Mapping[str, object]] = []
    if isinstance(value, DataSource):
        try:
            rows = _rows_from_datasource(value)
        except Exception as exc:  # noqa: BLE001
            notes.append(f"datasource inspect skipped: {exc}")
    elif isinstance(value, Mapping) and not hasattr(value, "model_dump"):
        # single mapping or column-oriented
        if value and all(
            isinstance(v, Sequence) and not isinstance(v, (str, bytes)) for v in value.values()
        ):
            keys = list(value.keys())[:_MAX_INSPECT_COLS]
            length = len(next(iter(value.values())))
            if length > _MAX_INSPECT_ROWS:
                notes.append(f"truncated rows to {_MAX_INSPECT_ROWS}")
            n = min(length, _MAX_INSPECT_ROWS)
            rows = [{str(k): value[k][i] for k in keys} for i in range(n)]
        else:
            rows = [cast(Mapping[str, object], value)]
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        if hasattr(value, "__len__") and len(value) > _MAX_INSPECT_ROWS:
            notes.append(f"truncated rows to {_MAX_INSPECT_ROWS}")
        sample = list(value[:_MAX_INSPECT_ROWS])
        for item in sample:
            if isinstance(item, Mapping):
                rows.append(cast(Mapping[str, object], item))
            elif hasattr(item, "model_dump"):
                rows.append(item.model_dump())
    elif hasattr(value, "__iter__") and not isinstance(value, (str, bytes, Mapping)):
        if is_lazy_source(value):
            raise error(
                "HED-AUTO-0002",
                title="Implicit lazy collection refused",
                explanation=f"Auto inspection will not collect lazy type {type(value).__name__}.",
                remediation="Pass a bounded page or materialized rows.",
            )
        columnar = _rows_from_columnar(value)
        if columnar is not None:
            rows = columnar
        else:
            notes.append(f"unrecognized iterable {type(value).__name__}")

    columns: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for k in row:
            if k not in seen and len(columns) < _MAX_INSPECT_COLS:
                seen.add(str(k))
                columns.append(str(k))
    cardinality: dict[str, int] = {}
    datetime_cols: list[str] = []
    geo_cols: list[str] = []
    for col in columns:
        values: list[Any] = [row.get(col) for row in rows]
        cardinality[col] = len({repr(v) for v in values})
        name = col.lower()
        if "date" in name or "time" in name:
            datetime_cols.append(col)
        if name in {"lat", "lon", "lng", "latitude", "longitude", "geo"}:
            geo_cols.append(col)
    return DataIntelligenceReport(
        row_count=len(rows) if rows else None,
        columns=tuple(columns),
        cardinality=cardinality,
        datetime_columns=tuple(datetime_cols),
        geospatial_columns=tuple(geo_cols),
        bounded=True,
        notes=tuple(notes),
    )
