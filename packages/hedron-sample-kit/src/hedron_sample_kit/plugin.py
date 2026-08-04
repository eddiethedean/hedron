"""Register the sample kit plugin."""

from __future__ import annotations

from pathlib import Path

from hedron_core.identifiers import content_digest
from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta
from hedron_core.registry import register_asset

_ROOT = Path(__file__).resolve().parent
_COMPONENT = _ROOT / "components" / "Callout"
_MARK = _COMPONENT / "mark.txt"

PLUGIN_META = PluginMeta(
    name="sample_kit",
    version="0.10.0",
    distribution="hedron-sample-kit",
    hedron_version=">=0.10,<0.11",
    capabilities=PluginCapabilities(
        python=True,
        styles=True,
        assets=True,
        explorer_panels=True,
    ),
)


def register(ctx: PluginContext) -> None:
    folder = _COMPONENT
    ctx.register_component(
        logical_id="hedron-sample-kit:callout.Callout",
        name="Callout",
        module="hedron_sample_kit.components.Callout",
        distribution="hedron-sample-kit",
        props_model="CalloutProps",
        styles_path=str(folder / "styles.css"),
        folder_path=str(folder),
        asset_roots=(str(folder),),
        examples=("default",),
    )
    if _MARK.is_file():
        digest = content_digest(_MARK.read_bytes())
        register_asset(
            logical_id="hedron-sample-kit:callout.mark",
            kind="file",
            path=str(_MARK),
            digest=digest,
            content_type="text/plain",
        )
    ctx.register_explorer_panel(
        panel_id="sample-kit-callout",
        title="Sample Callout",
        description="Demo panel contributed by hedron-sample-kit",
        path="/hedron-explorer/packages",
    )
    ctx.register_diagnostic_owner("HED-SAMPLE-")


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
