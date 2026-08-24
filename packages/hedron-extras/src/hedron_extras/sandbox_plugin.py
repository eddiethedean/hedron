"""Opt-in Experimental browser-Python sandbox plugin (not Supported hedron[extras]).

Default discovery skips ``*_sandbox`` unless ``HEDRON_EXTRAS_SANDBOX`` is truthy
or the entry point is explicitly enabled. Import remains
``from hedron_extras.sandbox import BrowserPythonSandbox``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hedron_core.codes import HED_ASSET_MISSING
from hedron_core.diagnostics import error
from hedron_core.identifiers import content_digest
from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta
from hedron_core.registry import register_asset, register_browser_module, register_component
from hedron_extras.descriptor import sandbox_feature
from hedron_extras.sandbox import BrowserPythonSandbox

_ROOT = Path(__file__).resolve().parent

PLUGIN_META = PluginMeta(
    name="hedron_extras_sandbox",
    version="0.62.0",
    distribution="hedron-extras",
    hedron_version=">=0.62,<0.63",
    depends_on=("hedron_extras",),
    capabilities=PluginCapabilities(
        python=True,
        styles=False,
        assets=True,
        browser_js=True,
        explorer_panels=False,
    ),
)


def _register_module_asset(rel: str) -> tuple[str, Path]:
    path = _ROOT / rel
    if not path.is_file():
        raise error(
            HED_ASSET_MISSING,
            title="Extras sandbox asset missing",
            explanation=f"Declared hedron-extras asset {rel!r} was not found at {path}.",
            remediation="Reinstall hedron-extras or repair the package wheel.",
        )
    digest = content_digest(path.read_bytes())
    logical = f"hedron-extras:{rel.replace('/', '.')}"
    register_asset(
        logical_id=logical,
        kind="module",
        path=str(path),
        digest=digest,
        content_type="text/javascript",
        attributes={"type": "module"},
    )
    return logical, path


def register(ctx: PluginContext) -> None:
    rel = "assets/sandbox/bridge.js"
    asset_id, path = _register_module_asset(rel)
    register_browser_module(
        logical_id="hedron-extras:sandbox-bridge",
        tag_name="hedron-extras-sandbox",
        module_path=str(path),
        observed_attributes=("data-hedron-payload",),
        events=(),
        shadow_dom=False,
        htmx_lifecycle=True,
    )
    logical = (
        f"{BrowserPythonSandbox.distribution}:"
        f"{BrowserPythonSandbox.__module__}.{BrowserPythonSandbox.logical_name}"
    )
    register_component(
        logical_id=logical,
        name=BrowserPythonSandbox.logical_name or "BrowserPythonSandbox",
        module=BrowserPythonSandbox.__module__,
        distribution=BrowserPythonSandbox.distribution,
        props_model=BrowserPythonSandbox.props_type.__name__,
        browser_modules=(str(path),),
        accessibility_notes="See feature manifest a11y_notes.",
    )
    sandbox_feature(assets=(asset_id,)).register(ctx)


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]

# Satisfy type checkers; registration uses PLUGIN_META.
_: Any = PLUGIN_META
