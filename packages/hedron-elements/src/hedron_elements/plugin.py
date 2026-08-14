"""Register hedron-elements plugin: ABI, assets, Example component."""

from __future__ import annotations

from pathlib import Path

from hedron_core.identifiers import content_digest
from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta
from hedron_core.registry import (
    register_asset,
    register_browser_module,
    register_component,
    register_element_definition,
)
from hedron_elements.example import (
    ABI_VERSION,
    ELEMENT_ID,
    EXAMPLE_OWNERSHIP,
    TAG_NAME,
    Example,
)

_ROOT = Path(__file__).resolve().parent
_BRIDGE = _ROOT / "static" / "hedron-bridge.mjs"
_JS = _ROOT / "static" / "hedron-example.mjs"
_CSS = _ROOT / "static" / "hedron-example.css"

PLUGIN_META = PluginMeta(
    name="hedron_elements",
    version="0.36.0",
    distribution="hedron-elements",
    hedron_version=">=0.36,<0.37",
    capabilities=PluginCapabilities(
        python=True,
        styles=True,
        assets=True,
        browser_js=True,
        explorer_panels=False,
    ),
)


def register(ctx: PluginContext) -> None:
    logical = (
        f"{Example.distribution}:{Example.__module__}."
        f"{getattr(Example, 'logical_name', Example.__name__)}"
    )
    register_component(
        logical_id=logical,
        name=getattr(Example, "logical_name", Example.__name__) or Example.__name__,
        module=Example.__module__,
        distribution=Example.distribution,
        props_model=Example.props_type.__name__,
        browser_modules=(str(_JS),) if _JS.is_file() else (),
        accessibility_notes=(
            "Light-DOM status region with progressive-enhancement toggle; "
            "usable before upgrade and after module failure."
        ),
    )

    if _BRIDGE.is_file():
        digest = content_digest(_BRIDGE.read_bytes())
        register_asset(
            logical_id="hedron-elements:bridge.mjs",
            kind="module",
            path=str(_BRIDGE),
            digest=digest,
            content_type="text/javascript",
        )
    if _JS.is_file():
        digest = content_digest(_JS.read_bytes())
        register_asset(
            logical_id="hedron-elements:example.mjs",
            kind="module",
            path=str(_JS),
            digest=digest,
            content_type="text/javascript",
        )
        register_browser_module(
            logical_id="hedron-elements:example",
            tag_name=TAG_NAME,
            module_path=str(_JS),
            observed_attributes=("status", "data-hedron-abi", "data-hedron-element"),
            events=("hedron-example-change",),
            shadow_dom=False,
            htmx_lifecycle=True,
        )
        register_element_definition(
            logical_id=ELEMENT_ID,
            tag_name=TAG_NAME,
            abi_version=ABI_VERSION,
            module_asset_id="hedron-elements:example.mjs",
            attributes=("status", "data-hedron-abi", "data-hedron-element"),
            state_ownership=EXAMPLE_OWNERSHIP,
            events=("hedron-example-change",),
            dom_policy="light",
            server_regions=("content",),
            form_contract=None,
            a11y_contract={
                "role": "group",
                "name": "Example status",
                "keyboard": "button toggle",
            },
            style_contract={"tokens": "hedron-*"},
            resources=("hedron-elements:bridge.mjs", "hedron-elements:example.css"),
            lifecycle={
                "connect": "idempotent",
                "disconnect": "abort+dispose",
                "htmx": "beforeCleanupElement",
            },
            fallback={
                "pre_upgrade": "server content visible",
                "js_off": "server content visible",
                "module_failure": "retain server content",
            },
            first_party=True,
        )
    if _CSS.is_file():
        digest = content_digest(_CSS.read_bytes())
        register_asset(
            logical_id="hedron-elements:example.css",
            kind="css",
            path=str(_CSS),
            digest=digest,
            content_type="text/css",
        )

    ctx.register_diagnostic_owner("HED-ELEMENT-")
    ctx.register_feature(
        name="web_component_abi",
        stability="experimental",
        description="Versioned element ABI, SSR fallback, and HTMX lifecycle foundation.",
        http_fallback=True,
        security_notes=(
            "Custom-element events are untrusted; Shadow DOM is not a security boundary; "
            "CSRF/authz remain server-owned."
        ),
    )


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
