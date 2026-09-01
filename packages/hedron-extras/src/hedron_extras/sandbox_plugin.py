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
from hedron_core.plugins import (
    PluginCapabilities,
    PluginContext,
    PluginDefinition,
    PluginMeta,
)
from hedron_extras.descriptor import sandbox_feature
from hedron_extras.sandbox import BrowserPythonSandbox

_ROOT = Path(__file__).resolve().parent
_SANDBOX_REL = "assets/sandbox/bridge.js"

PLUGIN_META = PluginMeta(
    name="hedron_extras_sandbox",
    version="1.0.6",
    distribution="hedron-extras",
    hedron_version=">=1.0,<2.0",
    depends_on=("hedron_extras",),
    capabilities=PluginCapabilities(
        python=True,
        styles=False,
        assets=True,
        browser_js=True,
        explorer_panels=False,
    ),
)


def _module_asset(rel: str) -> tuple[str, Path]:
    path = _ROOT / rel
    if not path.is_file():
        raise error(
            HED_ASSET_MISSING,
            title="Extras sandbox asset missing",
            explanation=f"Declared hedron-extras asset {rel!r} was not found at {path}.",
            remediation="Reinstall hedron-extras or repair the package wheel.",
        )
    logical = f"hedron-extras:{rel.replace('/', '.')}"
    return logical, path


def _register_module_asset(ctx: PluginContext, rel: str) -> tuple[str, Path]:
    logical, path = _module_asset(rel)
    ctx.register_asset(
        logical_id=logical,
        kind="module",
        path=str(path),
        digest=content_digest(path.read_bytes()),
        content_type="text/javascript",
        attributes={"type": "module"},
    )
    return logical, path


def _register_asset(ctx: PluginContext) -> None:
    _register_module_asset(ctx, _SANDBOX_REL)


def _register_component(ctx: PluginContext) -> None:
    _, path = _module_asset(_SANDBOX_REL)
    ctx.register_browser_module(
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
    ctx.register_component(
        logical_id=logical,
        name=BrowserPythonSandbox.logical_name or "BrowserPythonSandbox",
        module=BrowserPythonSandbox.__module__,
        distribution=BrowserPythonSandbox.distribution,
        props_model=BrowserPythonSandbox.props_type.__name__,
        browser_modules=(str(path),),
        accessibility_notes="See feature manifest a11y_notes.",
    )


def _register_feature(ctx: PluginContext) -> None:
    asset_id, _ = _module_asset(_SANDBOX_REL)
    sandbox_feature(assets=(asset_id,)).register(ctx)


PLUGIN = PluginDefinition.from_callbacks(
    PLUGIN_META,
    (
        ("asset", _register_asset),
        ("component", _register_component),
        ("feature", _register_feature),
    ),
)


def register(ctx: PluginContext) -> None:
    PLUGIN.register(ctx)


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]

# Satisfy type checkers; registration uses PLUGIN_META.
_: Any = PLUGIN_META
