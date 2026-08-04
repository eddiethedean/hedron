"""hedron-data: DataTable, DataEditor, and data-source toolkit."""

from __future__ import annotations

from hedron_data.aggrid import AG_GRID_BACKEND, ensure_aggrid_assets
from hedron_data.columns import Column, columns_from_model, resolve_columns
from hedron_data.editor import DataEditor, conflict_actions, filter_writable_changes
from hedron_data.memory import AsyncInMemoryDataSource, InMemoryDataSource
from hedron_data.normalize import normalize_rows
from hedron_data.sources import (
    DEFAULT_MAX_PAGE_SIZE,
    DEFAULT_MAX_VIZ_PAYLOAD_BYTES,
    DEFAULT_MAX_VIZ_ROWS,
    HARD_MAX_PAGE_SIZE,
    AsyncDataEditorSource,
    AsyncVisualizationSource,
    CellUpdate,
    ColumnSchema,
    Conflict,
    DataChanges,
    DataEditorSource,
    DataPage,
    DataQuery,
    DataSaveResult,
    FieldError,
    VisualizationSource,
)
from hedron_data.sqlalchemy_source import SQLAlchemyDataSource
from hedron_data.table import DataTable

__version__ = "0.9.0"

__all__ = [
    "AG_GRID_BACKEND",
    "DEFAULT_MAX_PAGE_SIZE",
    "DEFAULT_MAX_VIZ_PAYLOAD_BYTES",
    "DEFAULT_MAX_VIZ_ROWS",
    "HARD_MAX_PAGE_SIZE",
    "AsyncDataEditorSource",
    "AsyncInMemoryDataSource",
    "AsyncVisualizationSource",
    "CellUpdate",
    "Column",
    "ColumnSchema",
    "Conflict",
    "DataChanges",
    "DataEditor",
    "DataEditorSource",
    "DataPage",
    "DataQuery",
    "DataSaveResult",
    "DataTable",
    "FieldError",
    "InMemoryDataSource",
    "SQLAlchemyDataSource",
    "VisualizationSource",
    "__version__",
    "columns_from_model",
    "conflict_actions",
    "ensure_aggrid_assets",
    "filter_writable_changes",
    "normalize_rows",
    "resolve_columns",
]
