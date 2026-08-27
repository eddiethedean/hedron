"""Third-party-shaped element plugin using only PluginContext registration."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta

PLUGIN_META = PluginMeta(
    name="element_author_plugin",
    version="0.1.0",
    distribution="element-author-plugin",
    hedron_version=">=0.67,<0.68",
    capabilities=PluginCapabilities(browser_js=True, styles=True, assets=True),
)

_STATIC = Path(__file__).parent / "static"
_TAG_NAME = "ext-author-probe"
_MODULE_ID = "element-author-plugin:author-probe.mjs"
_CSS_ID = "element-author-plugin:author-probe.css"
LOGICAL_ID = "element-author-plugin:author-probe"


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def register(ctx: PluginContext) -> None:
    module = _STATIC / "ext-author-probe.mjs"
    styles = _STATIC / "ext-author-probe.css"
    ctx.register_asset(
        logical_id=_MODULE_ID,
        kind="module",
        path=str(module),
        digest=_digest(module),
        content_type="text/javascript",
    )
    ctx.register_asset(
        logical_id=_CSS_ID,
        kind="css",
        path=str(styles),
        digest=_digest(styles),
        content_type="text/css",
    )
    ctx.register_browser_module(
        logical_id="element-author-plugin:author-probe-browser",
        tag_name=_TAG_NAME,
        module_path=str(module),
        observed_attributes=("status",),
        events=("ext-author-probe-change",),
    )
    ctx.register_element_definition(
        logical_id=LOGICAL_ID,
        tag_name=_TAG_NAME,
        abi_version=1,
        module_asset_id=_MODULE_ID,
        attributes=("status",),
        events=("ext-author-probe-change",),
        lifecycle={"connect": "idempotent", "disconnect": "dispose"},
        fallback={"js_off": "server content remains visible"},
        a11y_contract={},
        resources=(_CSS_ID,),
        parts=("status",),
        slots={"default": "Fallback content"},
        tokens=("--ext-author-probe-color",),
    )
    ctx.register_diagnostic_owner("HED-AUTHOR-PLUGIN-")


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
