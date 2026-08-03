"""Normalize tabular inputs into list[dict] rows without implicit lazy collection."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from hedron_core.diagnostics import error
from hedron_core.models import Model
from hedron_core.security import Secret

_MAX_INLINE_ROWS = 10_000


def _row_to_mapping(row: Any) -> dict[str, Any]:
    if isinstance(row, Model):
        data = row.model_dump()
        return {k: (v.reveal() if isinstance(v, Secret) else v) for k, v in data.items()}
    if isinstance(row, Mapping):
        return {str(k): v for k, v in row.items()}
    if hasattr(row, "model_dump") and callable(row.model_dump):
        data = row.model_dump()
        if isinstance(data, Mapping):
            return {str(k): v for k, v in data.items()}
    raise error(
        "HED-DATA-0001",
        title="Unsupported row type",
        explanation=f"Cannot normalize row of type {type(row).__name__}.",
        remediation="Pass mappings, Hedron models, or install dataframe extras.",
    )


def _refuse_lazy(obj: Any) -> None:
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


def _from_narwhals(obj: Any) -> list[dict[str, Any]]:
    try:
        import narwhals as nw  # type: ignore[import-not-found]
    except ImportError as exc:
        raise error(
            "HED-DATA-0003",
            title="Dataframe extra missing",
            explanation="Narwhals is required to normalize Pandas/Polars/PyArrow inputs.",
            remediation='Install with: pip install "hedron-data[dataframes]"',
        ) from exc
    frame = nw.from_native(obj)
    native = frame.to_dict(as_series=False)
    if not native:
        return []
    keys = list(native.keys())
    length = len(next(iter(native.values())))
    if length > _MAX_INLINE_ROWS:
        raise error(
            "HED-DATA-0004",
            title="Inline dataset too large",
            explanation=f"Refusing to inline {length} rows (max {_MAX_INLINE_ROWS}).",
            remediation="Use a paged DataEditorSource instead of passing the full frame.",
        )
    return [{k: native[k][i] for k in keys} for i in range(length)]


def normalize_rows(data: Any, *, max_rows: int = _MAX_INLINE_ROWS) -> list[dict[str, Any]]:
    """Normalize supported tabular inputs into list[dict[str, Any]]."""
    if data is None:
        return []
    _refuse_lazy(data)
    type_name = type(data).__name__
    module = getattr(type(data), "__module__", "")
    if type_name == "DataFrame" or (
        module.startswith(("pandas.", "polars.", "pyarrow.")) and hasattr(data, "columns")
    ):
        return _from_narwhals(data)
    if isinstance(data, Mapping) and not isinstance(data, Model):
        # column-oriented dict of sequences
        if data and all(
            isinstance(v, Sequence) and not isinstance(v, (str, bytes)) for v in data.values()
        ):
            keys = list(data.keys())
            length = len(next(iter(data.values())))
            if length > max_rows:
                raise error(
                    "HED-DATA-0004",
                    title="Inline dataset too large",
                    explanation=f"Refusing to inline {length} rows (max {max_rows}).",
                    remediation="Use a paged DataEditorSource.",
                )
            return [{str(k): data[k][i] for k in keys} for i in range(length)]
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
