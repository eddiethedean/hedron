"""Register the sample kit plugin."""

from __future__ import annotations

from pathlib import Path

from hedron_core.identifiers import content_digest
from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta
from hedron_core.registry import register_asset
from hedron_sample_kit.variants import register_variants

_ROOT = Path(__file__).resolve().parent
_COMPONENT = _ROOT / "components" / "Callout"
_MARK = _COMPONENT / "mark.txt"

PLUGIN_META = PluginMeta(
    name="sample_kit",
    version="0.2.1",
    distribution="hedron-sample-kit",
    hedron_version=">=0.65,<0.66",
    capabilities=PluginCapabilities(
        python=True,
        styles=True,
        assets=True,
        browser_js=True,
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
    ctx.register_explorer_provider(
        panel_id="sample-kit-callout",
        title="Sample Callout",
        description="Demo panel contributed by hedron-sample-kit",
        path="/hedron-explorer/packages",
        capabilities=("html",),
    )
    ctx.register_diagnostic_owner("HED-SAMPLE-")
    from hedron_core.catalog import SurfaceProjectionProvider

    ctx.register_projection_provider(
        SurfaceProjectionProvider(
            namespace="hedron.sample-kit",
            provider="hedron-sample-kit",
            provider_version=PLUGIN_META.version,
            surface="Callout",
            limitations=("third-party-shaped; no privileged registry mutation",),
            disposition="native_consumer",
        )
    )
    from hedron_core.bundles import FeatureBundle
    from hedron_core.catalog import PackageProjection, ProjectionCapability

    ctx.register_feature_bundle(
        FeatureBundle(
            logical_id="hedron-sample-kit:callout-feature",
            provider="hedron-sample-kit",
            provider_version=PLUGIN_META.version,
            projections=(
                PackageProjection(
                    namespace="hedron.sample-kit.feature",
                    provider="hedron-sample-kit",
                    provider_version=PLUGIN_META.version,
                    capabilities=(
                        ProjectionCapability(name="CalloutFeature", support="supported"),
                    ),
                    data={"third_party": True, "privileged": False},
                    limitations=("public plugin APIs only",),
                ),
            ),
        )
    )
    register_variants(ctx)


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
