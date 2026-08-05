"""AG Grid Community adapter boundary for DataEditor (Tabulator remains default)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from hedron_core.diagnostics import error
from hedron_core.identifiers import content_digest
from hedron_core.registry import register_asset, register_browser_module
from hedron_core.typing_aliases import JsonObject, JsonValue
from hedron_data.sources import ColumnSchema, DataQuery

_ROOT = Path(__file__).resolve().parent
_HOST = _ROOT / "assets" / "aggrid" / "host.js"

__all__ = [
    "AG_GRID_BACKEND",
    "AGGridRowModel",
    "aggrid_column_defs",
    "ensure_aggrid_assets",
    "infinite_block_request",
    "require_aggrid_extra",
]

AG_GRID_BACKEND = "aggrid-community"
AGGridRowModel = Literal["clientSide", "infinite"]


def require_aggrid_extra() -> None:
    # Community assets are vendored as a host shim; apps may supply ag-grid-community JS.
    if not _HOST.is_file():
        raise error(
            "HED-DATA-0020",
            title="AG Grid host asset missing",
            explanation="hedron-data[aggrid] host asset is not packaged.",
            remediation='Reinstall hedron-data or pip install "hedron-data[aggrid]"',
        )


def aggrid_column_defs(schema: Sequence[ColumnSchema]) -> list[dict[str, JsonValue]]:
    defs: list[dict[str, JsonValue]] = []
    for col in schema:
        defs.append(
            {
                "field": col.name,
                "headerName": col.label,
                "editable": bool(
                    col.writable is not False and not col.read_only and not col.secret
                ),
                "hide": col.hidden,
                "sortable": col.sortable,
                "filter": col.filterable,
                "width": col.width,
                "cellDataType": col.display or col.editor,
            }
        )
    return defs


def infinite_block_request(query: DataQuery, *, block_size: int, start_row: int) -> DataQuery:
    if block_size < 1:
        raise ValueError("block_size must be >= 1")
    if start_row < 0:
        raise ValueError("start_row must be >= 0")
    return DataQuery(
        offset=start_row,
        limit=block_size,
        cursor=query.cursor,
        sort=query.sort,
        filters=query.filters,
        projection=query.projection,
        search=query.search,
        locale=query.locale,
        allowlisted_sort_fields=query.allowlisted_sort_fields,
        allowlisted_filter_fields=query.allowlisted_filter_fields,
    ).validated(max_page_size=max(block_size, 1))


def ensure_aggrid_assets(*, row_model: AGGridRowModel = "clientSide") -> JsonObject:
    """Register the AG Grid host module; Community clientSide/infinite only."""
    if row_model not in {"clientSide", "infinite"}:
        raise ValueError(f"Unsupported AG Grid row model {row_model!r}")
    require_aggrid_extra()
    digest = content_digest(_HOST.read_bytes())
    register_asset(
        logical_id="hedron-data:aggrid.host.js",
        kind="js",
        path=str(_HOST),
        digest=digest,
        content_type="text/javascript",
    )
    register_browser_module(
        logical_id="hedron-data:aggrid-editor",
        tag_name="hedron-data-aggrid",
        module_path=str(_HOST),
        observed_attributes=("data-hedron-payload", "data-row-model"),
        events=(
            "hedron-data-conflict",
            "hedron-data-selection",
            "hedron-data-viewport",
            "hedron-data-pagination",
            "hedron-data-edit",
        ),
        shadow_dom=False,
        htmx_lifecycle=True,
    )
    return {
        "backend": AG_GRID_BACKEND,
        "host": "hedron-data:aggrid.host.js",
        "rowModel": row_model,
        "note": "Application API remains DataEditor; Enterprise features are out of scope.",
    }
