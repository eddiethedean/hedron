"""Register hedron-gradio FeatureManifest (optional plugin)."""

from __future__ import annotations

from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta

PLUGIN_META = PluginMeta(
    name="hedron_gradio",
    version="0.2.1",
    distribution="hedron-gradio",
    hedron_version=">=0.63,<0.64",
    capabilities=PluginCapabilities(
        python=True,
        styles=False,
        assets=False,
        browser_js=False,
        explorer_panels=False,
    ),
)


def register(ctx: PluginContext) -> None:
    ctx.register_feature(
        name="gradio_client",
        stability="beta",
        description=(
            "Optional Gradio client protocol adapter for endpoint discovery, "
            "predict/job/stream, and file transport; disabled by default."
        ),
        http_fallback=True,
        security_notes=(
            "Disabled by default; credentials are never recorded; share tunnels "
            "and raw JS injection remain deliberate non-parity."
        ),
    )
    ctx.register_diagnostic_owner("HED-GRADIO-")
    from hedron_core.catalog import SurfaceProjectionProvider

    ctx.register_projection_provider(
        SurfaceProjectionProvider(
            namespace="hedron.gradio",
            provider="hedron-gradio",
            provider_version=PLUGIN_META.version,
            surface="GradioClientAdapter",
            limitations=("disabled by default; catalog presence is not exposure",),
        )
    )
    ctx.register_projection_provider(
        SurfaceProjectionProvider(
            namespace="hedron.gradio.workflow",
            provider="hedron-gradio",
            provider_version=PLUGIN_META.version,
            surface="RemoteWorkflow",
            limitations=("allowlisted adapter/endpoint; catalog presence is not exposure",),
        )
    )


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
