"""AG Grid Community adapter boundary for DataEditor (Tabulator remains default)."""

from __future__ import annotations

from pathlib import Path

from hedron_core.diagnostics import error
from hedron_core.identifiers import content_digest
from hedron_core.registry import register_asset, register_browser_module
from hedron_core.typing_aliases import JsonObject

_ROOT = Path(__file__).resolve().parent
_HOST = _ROOT / "assets" / "aggrid" / "host.js"

__all__ = ["AG_GRID_BACKEND", "ensure_aggrid_assets", "require_aggrid_extra"]

AG_GRID_BACKEND = "aggrid-community"


def require_aggrid_extra() -> None:
    # Community assets are vendored as a host shim; apps may supply ag-grid-community JS.
    if not _HOST.is_file():
        raise error(
            "HED-DATA-0020",
            title="AG Grid host asset missing",
            explanation="hedron-data[aggrid] host asset is not packaged.",
            remediation='Reinstall hedron-data or pip install "hedron-data[aggrid]"',
        )


def ensure_aggrid_assets() -> JsonObject:
    """Register the AG Grid host module; does not change DataEditor's public API."""
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
        observed_attributes=("data-hedron-payload",),
        events=("hedron-data-conflict",),
        shadow_dom=False,
        htmx_lifecycle=True,
    )
    return {
        "backend": AG_GRID_BACKEND,
        "host": "hedron-data:aggrid.host.js",
        "note": "Application API remains DataEditor; backend options are adapter-namespaced.",
    }
