"""Register hedron-data browser module, ABI element, and components."""

from __future__ import annotations

from pathlib import Path

from hedron_core.identifiers import content_digest
from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta
from hedron_core.registry import (
    ElementFieldOwnership,
    register_asset,
    register_browser_module,
    register_component,
    register_element_definition,
)
from hedron_data.editor import DATA_EDITOR_EVENTS, DataEditor
from hedron_data.table import DataTable

_ROOT = Path(__file__).resolve().parent
_JS = _ROOT / "assets" / "tabulator" / "editor.js"
_CSS = _ROOT / "assets" / "tabulator" / "editor.css"

PLUGIN_META = PluginMeta(
    name="hedron_data",
    version="0.40.0",
    distribution="hedron-data",
    hedron_version=">=0.40,<0.41",
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
            observed_attributes=("data-hedron-payload", "data-hedron-abi", "data-hedron-element"),
            events=DATA_EDITOR_EVENTS,
            shadow_dom=False,
            htmx_lifecycle=True,
        )
        register_element_definition(
            logical_id="hedron-data-editor",
            tag_name="hedron-data-editor",
            abi_version=1,
            module_asset_id="hedron-data:tabulator.editor.js",
            attributes=(
                "data-hedron-payload",
                "data-hedron-abi",
                "data-hedron-element",
                "data-hedron-editor",
                "data-hedron-module",
            ),
            state_ownership=(
                ElementFieldOwnership(
                    name="payload",
                    mode="controlled",
                    reflection="attribute",
                    incoming_update="replace",
                    persistence="none",
                    event="hedron-data-cell-edit",
                ),
                ElementFieldOwnership(
                    name="selection",
                    mode="local",
                    reflection="none",
                    incoming_update="ignore",
                    persistence="none",
                    event="hedron-data-selection-change",
                ),
                ElementFieldOwnership(
                    name="optimistic",
                    mode="local",
                    reflection="none",
                    incoming_update="ignore",
                    persistence="none",
                    event="hedron-data-optimistic",
                ),
            ),
            events=DATA_EDITOR_EVENTS,
            dom_policy="light",
            server_regions=("fallback",),
            a11y_contract={
                "role": "grid",
                "name_from": "aria-label",
                "keyboard": "cell-navigation",
            },
            style_contract={"tokens": "--hedron-data-*"},
            resources=("hedron-data:tabulator.editor.js", "hedron-data:tabulator.editor.css"),
            lifecycle={
                "connect": "idempotent",
                "disconnect": "abort+dispose",
                "htmx": "beforeCleanupElement",
            },
            fallback={
                "table": "semantic",
                "summary": "caption",
                "export": "authorized_csv",
            },
            first_party=True,
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
