"""Register hedron-elements plugin: ABI, assets, and 0.37 reference elements."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from hedron_core.identifiers import content_digest
from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta
from hedron_core.registry import (
    register_asset,
    register_browser_module,
    register_component,
    register_element_definition,
)
from hedron_elements.action_async import ACTION_ASYNC_META, ActionAsync
from hedron_elements.dialog import DIALOG_META, Dialog
from hedron_elements.disclosure import DISCLOSURE_META, Disclosure
from hedron_elements.example import (
    ABI_VERSION as EXAMPLE_ABI,
)
from hedron_elements.example import (
    ELEMENT_ID as EXAMPLE_ID,
)
from hedron_elements.example import (
    EXAMPLE_OWNERSHIP,
    Example,
)
from hedron_elements.example import (
    TAG_NAME as EXAMPLE_TAG,
)
from hedron_elements.field_choice import FIELD_CHOICE_META, FieldChoice
from hedron_elements.field_file import FIELD_FILE_META, FieldFile
from hedron_elements.field_text import FIELD_TEXT_META, FieldText

_ROOT = Path(__file__).resolve().parent
_STATIC = _ROOT / "static"

PLUGIN_META = PluginMeta(
    name="hedron_elements",
    version="0.60.1",
    distribution="hedron-elements",
    hedron_version=">=0.60,<0.61",
    capabilities=PluginCapabilities(
        python=True,
        styles=True,
        assets=True,
        browser_js=True,
        explorer_panels=False,
    ),
)

_ELEMENT_COMPONENTS: tuple[tuple[type, Mapping[str, Any]], ...] = (
    (Example, {"logical_id": EXAMPLE_ID, "tag_name": EXAMPLE_TAG, "abi_version": EXAMPLE_ABI}),
    (FieldText, FIELD_TEXT_META),
    (FieldChoice, FIELD_CHOICE_META),
    (FieldFile, FIELD_FILE_META),
    (Disclosure, DISCLOSURE_META),
    (Dialog, DIALOG_META),
    (ActionAsync, ACTION_ASYNC_META),
)

_MODULE_FILENAMES: dict[str, str] = {}

_STATIC_ASSETS: tuple[tuple[str, str, str], ...] = (
    ("hedron-elements:bridge.mjs", "hedron-bridge.mjs", "text/javascript"),
    ("hedron-elements:interaction-state.mjs", "interaction-state.mjs", "text/javascript"),
    ("hedron-elements:gesture-catalog.mjs", "gesture-catalog.mjs", "text/javascript"),
    ("hedron-elements:example.mjs", "hedron-example.mjs", "text/javascript"),
    ("hedron-elements:example.css", "hedron-example.css", "text/css"),
    ("hedron-elements:field-text.mjs", "hedron-field-text.mjs", "text/javascript"),
    ("hedron-elements:field-choice.mjs", "hedron-field-choice.mjs", "text/javascript"),
    ("hedron-elements:field-file.mjs", "hedron-field-file.mjs", "text/javascript"),
    ("hedron-elements:disclosure.mjs", "hedron-disclosure.mjs", "text/javascript"),
    ("hedron-elements:dialog.mjs", "hedron-dialog.mjs", "text/javascript"),
    ("hedron-elements:action-async.mjs", "hedron-action-async.mjs", "text/javascript"),
)


def _register_static_assets() -> None:
    for logical_id, filename, content_type in _STATIC_ASSETS:
        _MODULE_FILENAMES[logical_id] = filename
        path = _STATIC / filename
        if not path.is_file():
            continue
        register_asset(
            logical_id=logical_id,
            kind="module" if content_type.endswith("javascript") else "css",
            path=str(path),
            digest=content_digest(path.read_bytes()),
            content_type=content_type,
        )


def _register_component(component_type: type, meta: Mapping[str, Any]) -> None:
    logical = (
        f"{component_type.distribution}:{component_type.__module__}."
        f"{getattr(component_type, 'logical_name', component_type.__name__)}"
    )
    asset_id = str(meta["module_asset_id"])
    module_name = _MODULE_FILENAMES.get(asset_id, asset_id.split(":")[-1])
    register_component(
        logical_id=logical,
        name=getattr(component_type, "logical_name", component_type.__name__)
        or component_type.__name__,
        module=component_type.__module__,
        distribution=component_type.distribution,
        props_model=component_type.props_type.__name__,
        browser_modules=(str(_STATIC / module_name),),
        accessibility_notes="Progressive-enhancement Web Component with native fallback.",
    )


def _register_element(meta: Mapping[str, Any]) -> None:
    asset_id = str(meta["module_asset_id"])
    module_name = _MODULE_FILENAMES.get(asset_id, asset_id.split(":")[-1])
    module_path = _STATIC / module_name
    if not module_path.is_file():
        return
    register_browser_module(
        logical_id=f"hedron-elements:{meta['tag_name']}",
        tag_name=str(meta["tag_name"]),
        module_path=str(module_path),
        observed_attributes=tuple(meta.get("attributes", ())),
        events=tuple(meta.get("events", ())),
        shadow_dom=False,
        htmx_lifecycle=True,
    )
    register_element_definition(
        logical_id=str(meta["logical_id"]),
        tag_name=str(meta["tag_name"]),
        abi_version=int(meta["abi_version"]),
        module_asset_id=str(meta["module_asset_id"]),
        attributes=tuple(meta.get("attributes", ())),
        state_ownership=tuple(meta.get("state_ownership", ())),
        events=tuple(meta.get("events", ())),
        dom_policy="light",
        server_regions=("content", "control"),
        form_contract=meta.get("form_contract"),
        a11y_contract=dict(meta.get("a11y_contract", {})),
        style_contract={"tokens": "hedron-*"},
        resources=tuple(meta.get("resources", ("hedron-elements:bridge.mjs",))),
        lifecycle={
            "connect": "idempotent",
            "disconnect": "abort+dispose",
            "htmx": "beforeCleanupElement",
        },
        fallback=dict(meta.get("fallback", {})),
        first_party=True,
    )


def register(ctx: PluginContext) -> None:
    _register_static_assets()

    example_meta = {
        "logical_id": EXAMPLE_ID,
        "tag_name": EXAMPLE_TAG,
        "abi_version": EXAMPLE_ABI,
        "module_asset_id": "hedron-elements:example.mjs",
        "attributes": ("status", "data-hedron-abi", "data-hedron-element"),
        "state_ownership": EXAMPLE_OWNERSHIP,
        "events": ("hedron-example-change",),
        "form_contract": None,
        "resources": ("hedron-elements:bridge.mjs", "hedron-elements:example.css"),
        "fallback": {
            "pre_upgrade": "server content visible",
            "js_off": "server content visible",
            "module_failure": "retain server content",
        },
    }
    _register_component(Example, example_meta)
    _register_element(example_meta)

    for component_type, meta in _ELEMENT_COMPONENTS[1:]:
        _register_component(component_type, meta)
        _register_element(meta)

    ctx.register_diagnostic_owner("HED-ELEMENT-")
    ctx.register_feature(
        name="web_component_abi",
        stability="experimental",
        description="Form-associated elements, InteractionState, and primitive catalog (0.37).",
        http_fallback=True,
        security_notes=(
            "Custom-element events are untrusted; Shadow DOM is not a security boundary; "
            "CSRF/authz remain server-owned."
        ),
    )
    from hedron_core.catalog import SurfaceProjectionProvider

    ctx.register_projection_provider(
        SurfaceProjectionProvider(
            namespace="hedron.elements",
            provider="hedron-elements",
            provider_version=PLUGIN_META.version,
            surface="web_component_abi",
            limitations=(
                "opt-in schema-aware generate_form(enhance='elements'); native remains canonical",
            ),
        )
    )
    ctx.register_projection_provider(
        SurfaceProjectionProvider(
            namespace="hedron.elements.schema",
            provider="hedron-elements",
            provider_version=PLUGIN_META.version,
            surface="schema-aware-forms",
            limitations=("opt-in enhance=elements; native ActionHandle.form() remains canonical",),
        )
    )


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
