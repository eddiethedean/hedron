"""Register hedron-notebook FeatureManifest (optional plugin)."""

from __future__ import annotations

from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta

PLUGIN_META = PluginMeta(
    name="hedron_notebook",
    version="0.1.0",
    distribution="hedron-notebook",
    hedron_version=">=0.50,<0.51",
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
        name="notebook_preview",
        stability="experimental",
        description=(
            "Server-side notebook preview helper (iframe / external link); "
            "localhost-oriented; not a Supported production server."
        ),
        http_fallback=True,
        a11y_notes="Iframe and external-link modes must remain keyboard-reachable.",
        security_notes=(
            "Random session token; warn on non-loopback hosts; never weakens "
            "CSRF/authz of the previewed app."
        ),
    )
    ctx.register_diagnostic_owner("HED-NOTEBOOK-")


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
