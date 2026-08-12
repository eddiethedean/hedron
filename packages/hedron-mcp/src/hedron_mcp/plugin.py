"""Register hedron-mcp FeatureManifest (optional plugin)."""

from __future__ import annotations

from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta

PLUGIN_META = PluginMeta(
    name="hedron_mcp",
    version="0.1.0",
    distribution="hedron-mcp",
    hedron_version=">=0.31,<0.32",
    capabilities=PluginCapabilities(
        python=True,
        styles=False,
        assets=False,
        browser_js=False,
        explorer_panels=False,
        routes=True,
    ),
)


def register(ctx: PluginContext) -> None:
    ctx.register_feature(
        name="mcp_projection",
        stability="experimental",
        description=(
            "Deny-by-default MCP Streamable HTTP projection; disabled and empty "
            "until explicit resource/tool registration."
        ),
        http_fallback=True,
        security_notes=(
            "Disabled empty by default; principal-bounded authz; never auto-exposes "
            "routes or exceeds authenticated principal."
        ),
    )
    ctx.register_diagnostic_owner("HED-MCP-")


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
