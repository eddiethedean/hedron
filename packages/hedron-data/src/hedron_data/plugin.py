"""Register hedron-data browser module and components."""

from __future__ import annotations

from pathlib import Path

from hedron_core.identifiers import content_digest
from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta
from hedron_core.registry import register_asset, register_browser_module, register_component
from hedron_data.editor import DataEditor
from hedron_data.table import DataTable

_ROOT = Path(__file__).resolve().parent
_JS = _ROOT / "assets" / "tabulator" / "editor.js"
_CSS = _ROOT / "assets" / "tabulator" / "editor.css"

PLUGIN_META = PluginMeta(
    name="hedron_data",
    version="0.26.1",
    distribution="hedron-data",
    hedron_version=">=0.26,<0.27",
    capabilities=PluginCapabilities(
        python=True,
        styles=True,
        assets=True,
        browser_js=True,
        explorer_panels=True,
    ),
)


def register(ctx: PluginContext) -> None:
    for cls in (DataTable, DataEditor):
        logical = (
            f"{cls.distribution}:{cls.__module__}.{getattr(cls, 'logical_name', cls.__name__)}"
        )
        register_component(
            logical_id=logical,
            name=getattr(cls, "logical_name", cls.__name__) or cls.__name__,
            module=cls.__module__,
            distribution=cls.distribution,
            props_model=getattr(cls, "props_type", type(None)).__name__,
            browser_modules=(str(_JS),) if cls is DataEditor and _JS.is_file() else (),
            accessibility_notes="Native table semantics with keyboard-editable grid host.",
        )

    if _JS.is_file():
        digest = content_digest(_JS.read_bytes())
        register_asset(
            logical_id="hedron-data:tabulator.editor.js",
            kind="js",
            path=str(_JS),
            digest=digest,
            content_type="text/javascript",
        )
        register_browser_module(
            logical_id="hedron-data:tabulator-editor",
            tag_name="hedron-data-editor",
            module_path=str(_JS),
            observed_attributes=("data-hedron-payload",),
            events=("hedron-data-conflict",),
            shadow_dom=False,
            htmx_lifecycle=True,
        )
    if _CSS.is_file():
        digest = content_digest(_CSS.read_bytes())
        register_asset(
            logical_id="hedron-data:tabulator.editor.css",
            kind="css",
            path=str(_CSS),
            digest=digest,
            content_type="text/css",
        )

    ctx.register_explorer_panel(
        panel_id="hedron-data-schema",
        title="Data schema",
        description="DataTable/DataEditor schema and writable-field policy",
        path="/hedron-explorer/data",
    )
    ctx.register_diagnostic_owner("HED-DATA-")


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
