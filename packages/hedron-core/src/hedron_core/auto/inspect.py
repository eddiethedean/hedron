"""Bounded Auto data inspection."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Protocol, TypeGuard, cast, runtime_checkable

from hedron_core.auto.spec import DataIntelligenceReport
from hedron_core.data import DataSource, is_lazy_source
from hedron_core.diagnostics import error

_MAX_INSPECT_ROWS = 200
_MAX_INSPECT_COLS = 50


def _is_object_sequence(value: object) -> TypeGuard[Sequence[object]]:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


@runtime_checkable
class _ModelDump(Protocol):
    def model_dump(self) -> Mapping[str, object]: ...


def _rows_from_datasource(value: DataSource) -> list[Mapping[str, object]]:
    return [dict(row) for row in value.inspect_rows(max_rows=_MAX_INSPECT_ROWS)]


def _rows_from_columnar(value: object) -> list[Mapping[str, object]] | None:
    """Duck-type pandas/polars-like tables without importing those packages."""
    head_fn: object = getattr(value, "head", None)
    if not callable(head_fn) or getattr(value, "columns", None) is None:
        return None
    sample: object = head_fn(_MAX_INSPECT_ROWS)
    to_dicts: object = getattr(sample, "to_dicts", None)
    if callable(to_dicts):
        raw: object = to_dicts()
        if _is_object_sequence(raw):
            return [
                {str(key): item for key, item in cast(Mapping[object, object], row).items()}
                for row in raw
                if isinstance(row, Mapping)
            ]
    to_dict: object = getattr(sample, "to_dict", None)
    if callable(to_dict):
        try:
            records: object = to_dict("records")
        except TypeError:
            records = to_dict()
        if _is_object_sequence(records):
            return [
                {str(key): item for key, item in cast(Mapping[object, object], row).items()}
                for row in records
                if isinstance(row, Mapping)
            ]
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
    elif isinstance(value, Mapping) and not isinstance(value, _ModelDump):
        mapping = cast(Mapping[object, object], value)
        # single mapping or column-oriented
        if mapping and all(_is_object_sequence(item) for item in mapping.values()):
            column_sequences = {
                key: item for key, item in mapping.items() if _is_object_sequence(item)
            }
            keys = list(column_sequences)[:_MAX_INSPECT_COLS]
            lengths = [len(item) for item in column_sequences.values()]
            if any(col_len != lengths[0] for col_len in lengths):
                raise error(
                    "HED-DATA-0005",
                    title="Column-oriented lengths mismatch",
                    explanation=(
                        "All column sequences must share the same length; "
                        f"got {dict(zip((str(k) for k in mapping), lengths, strict=True))}."
                    ),
                    remediation="Align column arrays or pass list[dict] rows instead.",
                )
            length = lengths[0]
            if length > _MAX_INSPECT_ROWS:
                notes.append(f"truncated rows to {_MAX_INSPECT_ROWS}")
            n = min(length, _MAX_INSPECT_ROWS)
            rows = [{str(key): column_sequences[key][i] for key in keys} for i in range(n)]
        else:
            rows = [{str(key): item for key, item in mapping.items()}]
    elif _is_object_sequence(value):
        if len(value) > _MAX_INSPECT_ROWS:
            notes.append(f"truncated rows to {_MAX_INSPECT_ROWS}")
        sample = list(value[:_MAX_INSPECT_ROWS])
        for item in sample:
            if isinstance(item, Mapping):
                mapping = cast(Mapping[object, object], item)
                rows.append({str(key): child for key, child in mapping.items()})
            elif isinstance(item, _ModelDump):
                rows.append(item.model_dump())
    elif isinstance(value, Iterable) and not isinstance(value, (str, bytes, Mapping)):
        iterable_value = cast(Iterable[object], value)
        if is_lazy_source(iterable_value):
            raise error(
                "HED-AUTO-0002",
                title="Implicit lazy collection refused",
                explanation=(
                    f"Auto inspection will not collect lazy type {type(iterable_value).__name__}."
                ),
                remediation="Pass a bounded page or materialized rows.",
            )
        columnar = _rows_from_columnar(iterable_value)
        if columnar is not None:
            rows = columnar
        else:
            notes.append(f"unrecognized iterable {type(iterable_value).__name__}")

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
        values: list[object] = [row.get(col) for row in rows]
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
