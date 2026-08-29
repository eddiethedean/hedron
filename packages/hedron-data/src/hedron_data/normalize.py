"""Normalize tabular inputs into list[dict] rows without implicit lazy collection."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import cast

from hedron_core.diagnostics import error
from hedron_core.models import Model
from hedron_core.security import redact_value
from hedron_core.typing_aliases import JsonValue

_MAX_INLINE_ROWS = 10_000


def _cell(value: object) -> JsonValue:
    return cast(JsonValue, redact_value(value))


def _row_to_mapping(row: object) -> dict[str, JsonValue]:
    if isinstance(row, Model):
        data = row.model_dump()
        return {k: _cell(v) for k, v in data.items()}
    if isinstance(row, Mapping):
        return {str(k): _cell(v) for k, v in row.items()}
    model_dump = getattr(row, "model_dump", None)
    if callable(model_dump):
        data = model_dump()
        if isinstance(data, Mapping):
            return {str(k): _cell(v) for k, v in data.items()}
    raise error(
        "HED-DATA-0001",
        title="Unsupported row type",
        explanation=f"Cannot normalize row of type {type(row).__name__}.",
        remediation="Pass mappings, Hedron models, or install dataframe extras.",
    )


def _refuse_lazy(obj: object) -> None:
    # Generators / iterators that are not materialized sequences.
    if hasattr(obj, "__iter__") and not isinstance(obj, (Sequence, Mapping, str, bytes)):
        # exclude known dataframe types handled below
        type_name = type(obj).__name__
        module = type(obj).__module__
        if type_name in {"DataFrame", "Table", "RecordBatch"} and module.split(".")[0] in {
            "pandas",
            "polars",
            "pyarrow",
            "narwhals",
        }:
            return
        if type_name.endswith("QuerySet") or "lazy" in type_name.lower():
            raise error(
                "HED-DATA-0002",
                title="Implicit lazy collection refused",
                explanation=(f"Refusing to implicitly collect lazy source of type {type_name}."),
                remediation="Materialize a bounded page via DataEditorSource.fetch().",
            )


def _from_narwhals(obj: object, *, max_rows: int) -> list[dict[str, JsonValue]]:
    try:
        import narwhals as nw  # type: ignore[import-not-found]
    except ImportError as exc:
        raise error(
            "HED-DATA-0003",
            title="Dataframe extra missing",
            explanation="Narwhals is required to normalize Pandas/Polars/PyArrow inputs.",
            remediation='Install with: pip install "hedron-data[dataframes]"',
        ) from exc
    frame = nw.from_native(obj)  # type: ignore[arg-type]
    native = frame.to_dict(as_series=False)
    if not native:
        return []
    keys = list(native.keys())
    length = len(next(iter(native.values())))
    if length > max_rows:
        raise error(
            "HED-DATA-0004",
            title="Inline dataset too large",
            explanation=f"Refusing to inline {length} rows (max {max_rows}).",
            remediation="Use a paged DataEditorSource instead of passing the full frame.",
        )
    return [{k: cast(JsonValue, native[k][i]) for k in keys} for i in range(length)]


def normalize_rows(data: object, *, max_rows: int = _MAX_INLINE_ROWS) -> list[dict[str, JsonValue]]:
    """Normalize supported tabular inputs into list[dict[str, JsonValue]]."""
    if data is None:
        return []
    _refuse_lazy(data)
    type_name = type(data).__name__
    module = getattr(type(data), "__module__", "")
    if type_name == "DataFrame" or (
        module.startswith(("pandas.", "polars.", "pyarrow.")) and hasattr(data, "columns")
    ):
        return _from_narwhals(data, max_rows=max_rows)
    if isinstance(data, Mapping) and not isinstance(data, Model):
        if not data:
            return []
        # column-oriented dict of sequences
        if all(isinstance(v, Sequence) and not isinstance(v, (str, bytes)) for v in data.values()):
            keys = list(data.keys())
            lengths = [len(data[k]) for k in keys]
            if not lengths:
                return []
            length = lengths[0]
            if any(length != col_len for col_len in lengths):
                raise error(
                    "HED-DATA-0005",
                    title="Column-oriented lengths mismatch",
                    explanation=(
                        "All column sequences must share the same length; "
                        f"got {dict(zip((str(k) for k in keys), lengths, strict=True))}."
                    ),
                    remediation="Align column arrays or pass list[dict] rows instead.",
                )
            if length > max_rows:
                raise error(
                    "HED-DATA-0004",
                    title="Inline dataset too large",
                    explanation=f"Refusing to inline {length} rows (max {max_rows}).",
                    remediation="Use a paged DataEditorSource.",
                )
            if length == 0:
                return []
            return [{str(k): _cell(data[k][i]) for k in keys} for i in range(length)]
        return [_row_to_mapping(data)]
    if isinstance(data, Sequence) and not isinstance(data, (str, bytes)):
        if len(data) > max_rows:
            raise error(
                "HED-DATA-0004",
                title="Inline dataset too large",
                explanation=f"Refusing to inline {len(data)} rows (max {max_rows}).",
                remediation="Use a paged DataEditorSource.",
            )
        return [_row_to_mapping(row) for row in data]
    if isinstance(data, Model):
        return [_row_to_mapping(data)]
    raise error(
        "HED-DATA-0001",
        title="Unsupported tabular input",
        explanation=f"Cannot normalize type {type(data).__name__}.",
        remediation="Pass list[dict], Hedron models, or optional dataframe extras.",
    )
