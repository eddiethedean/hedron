"""Register hedron-maps components, assets, and Explorer panel."""

from __future__ import annotations

from pathlib import Path

from hedron_core.catalog import SurfaceProjectionProvider
from hedron_core.identifiers import content_digest
from hedron_core.plugins import (
    PluginCapabilities,
    PluginContext,
    PluginDefinition,
    PluginMeta,
)
from hedron_core.registry import ElementFieldOwnership
from hedron_maps.element import Map
from hedron_maps.pins import assert_pins_present

_ROOT = Path(__file__).resolve().parent
_MAP_MODULE = _ROOT / "static" / "hedron-map.mjs"
_MAP_CSS = _ROOT / "static" / "hedron-map.css"
_ASSETS = _ROOT / "assets" / "maplibre"

PLUGIN_META = PluginMeta(
    name="hedron_maps",
    version="0.1.4",
    distribution="hedron-maps",
    hedron_version=">=1.0,<2.0",
    capabilities=PluginCapabilities(
        python=True,
        styles=True,
        assets=True,
        browser_js=True,
        explorer_panels=True,
    ),
)


def _register_component(ctx: PluginContext) -> None:
    assert_pins_present()
    ctx.register_component(
        logical_id=f"{Map.distribution}:{Map.__module__}.{Map.logical_name}",
        name=Map.logical_name or Map.__name__,
        module=Map.__module__,
        distribution=Map.distribution,
        props_model=Map.props_type.__name__,
        accessibility_notes=(
            "Maps require title and description or a reviewed decorative disposition; "
            "semantic table alternatives stay in .hedron-map-alternative."
        ),
    )


def _register_map_element(ctx: PluginContext) -> None:
    if _MAP_MODULE.is_file():
        ctx.register_asset(
            logical_id="hedron-maps:hedron-map.mjs",
            kind="js",
            path=str(_MAP_MODULE),
            digest=content_digest(_MAP_MODULE.read_bytes()),
            content_type="text/javascript",
        )
        ctx.register_browser_module(
            logical_id="hedron-maps:hedron-map",
            tag_name="hedron-map",
            module_path=str(_MAP_MODULE),
            observed_attributes=("data-hedron-payload", "data-hedron-abi"),
            events=(
                "hedron-map-feature-selected",
                "hedron-map-feature-activated",
                "hedron-map-viewport-changed",
                "hedron-map-layer-visibility-changed",
                "hedron-map-map-loaded",
                "hedron-map-map-failed",
            ),
            shadow_dom=False,
            htmx_lifecycle=True,
        )
        ctx.register_element_definition(
            logical_id="hedron-map",
            tag_name="hedron-map",
            abi_version=1,
            module_asset_id="hedron-maps:hedron-map.mjs",
            attributes=("data-hedron-payload", "data-hedron-abi", "data-hedron-element"),
            state_ownership=(
                ElementFieldOwnership(
                    name="payload",
                    mode="controlled",
                    reflection="attribute",
                    incoming_update="replace",
                    persistence="none",
                    event="hedron-map-feature-selected",
                ),
            ),
            events=(
                "hedron-map-feature-selected",
                "hedron-map-feature-activated",
                "hedron-map-viewport-changed",
                "hedron-map-layer-visibility-changed",
                "hedron-map-map-loaded",
                "hedron-map-map-failed",
            ),
            dom_policy="light",
            server_regions=("content",),
            a11y_contract={
                "role": "region",
                "name_from": "aria-label",
                "keyboard": "cooperative-gestures",
            },
            style_contract={"tokens": "--hedron-map-*"},
            resources=("hedron-maps:hedron-map.mjs", "hedron-maps:hedron-map.css"),
            lifecycle={
                "connect": "idempotent",
                "disconnect": "abort+dispose",
                "htmx": "beforeCleanupElement",
            },
            fallback={"figure": "semantic", "table": "bounded"},
            first_party=True,
        )
    if _MAP_CSS.is_file():
        ctx.register_asset(
            logical_id="hedron-maps:hedron-map.css",
            kind="css",
            path=str(_MAP_CSS),
            digest=content_digest(_MAP_CSS.read_bytes()),
            content_type="text/css",
        )


def _register_maplibre_assets(ctx: PluginContext) -> None:
    for filename, logical, kind, ctype in (
        ("maplibre-gl-csp.js", "hedron-maps:maplibre.runtime.js", "js", "text/javascript"),
        ("maplibre-gl-csp-worker.js", "hedron-maps:maplibre.worker.js", "js", "text/javascript"),
        ("maplibre-gl.css", "hedron-maps:maplibre.css", "css", "text/css"),
        ("LICENSE.txt", "hedron-maps:maplibre.license", "txt", "text/plain"),
    ):
        path = _ASSETS / filename
        if path.is_file():
            ctx.register_asset(
                logical_id=logical,
                kind=kind,
                path=str(path),
                digest=content_digest(path.read_bytes()),
                content_type=ctype,
            )


def _register_catalog(ctx: PluginContext) -> None:
    ctx.register_explorer_provider(
        panel_id="hedron-maps",
        title="Maps",
        description="Map plans, origins, attribution, CSP, fallback, and event schemas",
        path="/hedron-explorer/maps",
        capabilities=("html",),
    )
    ctx.register_diagnostic_owner("HED-MAP-SPEC-")
    ctx.register_diagnostic_owner("HED-MAP-SOURCE-")
    ctx.register_diagnostic_owner("HED-MAP-POLICY-")
    ctx.register_diagnostic_owner("HED-MAP-STYLE-")
    ctx.register_diagnostic_owner("HED-MAP-OFFLINE-")
    ctx.register_diagnostic_owner("HED-MAP-RUNTIME-")
    ctx.register_diagnostic_owner("HED-MAP-EVENT-")
    ctx.register_projection_provider(
        SurfaceProjectionProvider(
            namespace="hedron.maps",
            provider="hedron-maps",
            provider_version=PLUGIN_META.version,
            surface="Map/compile_map",
            limitations=("OSM default only on hedron_maps.Map; core Map is unchanged",),
        )
    )
    ctx.register_projection_provider(
        SurfaceProjectionProvider(
            namespace="hedron.maps.interaction",
            provider="hedron-maps",
            provider_version=PLUGIN_META.version,
            surface="MapInteraction",
            limitations=("Supported events are closed; ChartInteraction is not reused",),
        )
    )


PLUGIN = PluginDefinition.from_callbacks(
    PLUGIN_META,
    (
        ("component", _register_component),
        ("map-element", _register_map_element),
        ("maplibre-assets", _register_maplibre_assets),
        ("catalog", _register_catalog),
    ),
)


def register(ctx: PluginContext) -> None:
    PLUGIN.register(ctx)


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
