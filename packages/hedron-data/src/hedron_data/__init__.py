"""hedron-data: DataTable, DataEditor, and data-source toolkit."""

from __future__ import annotations

from hedron_data.a11y_spatial import SpatialAlternative, spatial_alternatives_for
from hedron_data.advanced import (
    CellFormat,
    MergeRegion,
    TreeNode,
    evaluate_formula,
    flatten_tree,
    pivot_rows,
    rows_to_tree,
)
from hedron_data.aggrid import (
    AG_GRID_BACKEND,
    AGGridRowModel,
    aggrid_column_defs,
    ensure_aggrid_assets,
    infinite_block_request,
)
from hedron_data.collab import (
    CollaborativeConflict,
    EditProvenance,
    merge_changes,
    recover_pending,
)
from hedron_data.columns import Column, columns_from_model, resolve_columns, write_policy
from hedron_data.dask_source import DaskDataSource, require_dask
from hedron_data.django_queryset import (
    DjangoQuerySetDataSource,
    QueryBudgetExceeded,
    QueryDiagnostics,
)
from hedron_data.editor import DataEditor, conflict_actions, filter_writable_changes
from hedron_data.events import (
    GridCellEvent,
    GridDragEvent,
    GridEditEvent,
    GridEvent,
    GridPaginationEvent,
    GridSelectionEvent,
    GridViewportEvent,
    authorized_grid_event,
    validate_grid_event,
)
from hedron_data.memory import AsyncInMemoryDataSource, InMemoryDataSource
from hedron_data.normalize import normalize_rows
from hedron_data.plans import TransformPlan, TransformStep, apply_plan_in_memory, plan_from_query
from hedron_data.snowflake_source import SnowflakeDataSource, require_snowflake
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
from hedron_data.spreadsheet import (
    export_rows_ods,
    export_rows_xlsx,
    import_rows_ods,
    import_rows_xlsx,
)
from hedron_data.sqlalchemy_source import SQLAlchemyDataSource
from hedron_data.table import DataTable
from hedron_data.views import SavedView

__version__ = "0.34.0"

__all__ = [
    "AG_GRID_BACKEND",
    "AGGridRowModel",
    "AsyncDataEditorSource",
    "AsyncInMemoryDataSource",
    "AsyncVisualizationSource",
    "CellFormat",
    "CellUpdate",
    "CollaborativeConflict",
    "Column",
    "ColumnSchema",
    "Conflict",
    "DaskDataSource",
    "DataChanges",
    "DataEditor",
    "DataEditorSource",
    "DataPage",
    "DataQuery",
    "DataSaveResult",
    "DataTable",
    "DEFAULT_MAX_PAGE_SIZE",
    "DEFAULT_MAX_VIZ_PAYLOAD_BYTES",
    "DEFAULT_MAX_VIZ_ROWS",
    "DjangoQuerySetDataSource",
    "EditProvenance",
    "FieldError",
    "GridCellEvent",
    "GridDragEvent",
    "GridEditEvent",
    "GridEvent",
    "GridPaginationEvent",
    "GridSelectionEvent",
    "GridViewportEvent",
    "HARD_MAX_PAGE_SIZE",
    "InMemoryDataSource",
    "MergeRegion",
    "QueryBudgetExceeded",
    "QueryDiagnostics",
    "SQLAlchemyDataSource",
    "SavedView",
    "SnowflakeDataSource",
    "SpatialAlternative",
    "TransformPlan",
    "TransformStep",
    "TreeNode",
    "VisualizationSource",
    "__version__",
    "aggrid_column_defs",
    "apply_plan_in_memory",
    "authorized_grid_event",
    "columns_from_model",
    "conflict_actions",
    "ensure_aggrid_assets",
    "evaluate_formula",
    "export_rows_ods",
    "export_rows_xlsx",
    "filter_writable_changes",
    "flatten_tree",
    "import_rows_ods",
    "import_rows_xlsx",
    "infinite_block_request",
    "merge_changes",
    "normalize_rows",
    "pivot_rows",
    "plan_from_query",
    "recover_pending",
    "require_dask",
    "require_snowflake",
    "resolve_columns",
    "rows_to_tree",
    "spatial_alternatives_for",
    "validate_grid_event",
    "write_policy",
]
