"""Register the sample kit plugin."""

from __future__ import annotations

from pathlib import Path

from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta

_ROOT = Path(__file__).resolve().parent
_COMPONENT = _ROOT / "components" / "Callout"

PLUGIN_META = PluginMeta(
    name="sample_kit",
    version="0.4.0",
    distribution="hedron-sample-kit",
    hedron_version=">=0.4,<0.5",
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
        hdn_source=str(folder / "template.hdn"),
        styles_path=str(folder / "styles.css"),
        folder_path=str(folder),
        asset_roots=(str(folder),),
        examples=("default",),
    )
    ctx.register_explorer_panel(
        panel_id="sample-kit-callout",
        title="Sample Callout",
        description="Demo panel contributed by hedron-sample-kit",
        path="/hedron-explorer/packages",
    )
    ctx.register_diagnostic_owner("HED-SAMPLE-")


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
