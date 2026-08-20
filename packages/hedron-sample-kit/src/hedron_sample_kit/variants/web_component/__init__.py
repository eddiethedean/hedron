"""Asset-backed Web Component variant with a server-rendered fallback."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hedron_core.component import Component
from hedron_core.html import html
from hedron_core.identifiers import content_digest
from hedron_core.models import Props
from hedron_core.plugins import PluginContext

VARIANT_ID = "web_component"
TAG_NAME = "sample-kit-callout"
SSR_FALLBACK_TEXT = "Sample kit callout (server-rendered fallback)"

_STATIC = Path(__file__).resolve().parent / "static"
_MODULE_PATH = _STATIC / f"{TAG_NAME}.mjs"
_STYLES_PATH = _STATIC / f"{TAG_NAME}.css"

MODULE_ASSET_ID = "hedron-sample-kit:web-component.module"
STYLES_ASSET_ID = "hedron-sample-kit:web-component.styles"
ELEMENT_ID = "hedron-sample-kit:web-component.element"

__all__ = [
    "ELEMENT_ID",
    "MODULE_ASSET_ID",
    "SSR_FALLBACK_TEXT",
    "STYLES_ASSET_ID",
    "TAG_NAME",
    "VARIANT_ID",
    "WebCallout",
    "WebCalloutProps",
    "register",
]


class WebCalloutProps(Props):
    message: str = SSR_FALLBACK_TEXT
    status: str = "info"


class WebCallout(Component[WebCalloutProps]):
    """Custom element wrapper whose light DOM stays readable without JavaScript."""

    props_type = WebCalloutProps
    logical_name = "WebCallout"
    distribution = "hedron-sample-kit"

    def __init__(
        self,
        message: str = SSR_FALLBACK_TEXT,
        status: str = "info",
        **kwargs: Any,
    ) -> None:
        super().__init__(WebCalloutProps(message=message, status=status, **kwargs))

    def render(self) -> Any:
        return html.tag(TAG_NAME)(
            html.span(self.props.message, class_="fallback"),
            status=self.props.status,
        )


def default() -> WebCallout:
    """Named example: enhanced callout with fallback text."""
    return WebCallout(message=SSR_FALLBACK_TEXT)


EXAMPLES = {"default": default}


def register(ctx: PluginContext) -> None:
    ctx.register_asset(
        logical_id=MODULE_ASSET_ID,
        kind="module",
        path=str(_MODULE_PATH),
        digest=content_digest(_MODULE_PATH.read_bytes()),
        content_type="text/javascript",
    )
    ctx.register_asset(
        logical_id=STYLES_ASSET_ID,
        kind="css",
        path=str(_STYLES_PATH),
        digest=content_digest(_STYLES_PATH.read_bytes()),
        content_type="text/css",
    )
    ctx.register_browser_module(
        logical_id="hedron-sample-kit:web-component.browser",
        tag_name=TAG_NAME,
        module_path=str(_MODULE_PATH),
        observed_attributes=("status",),
        events=(f"{TAG_NAME}-change",),
    )
    ctx.register_element_definition(
        logical_id=ELEMENT_ID,
        tag_name=TAG_NAME,
        abi_version=1,
        module_asset_id=MODULE_ASSET_ID,
        attributes=("status",),
        events=(f"{TAG_NAME}-change",),
        lifecycle={"connect": "idempotent", "disconnect": "dispose"},
        fallback={"js_off": SSR_FALLBACK_TEXT},
        resources=(STYLES_ASSET_ID,),
    )
    ctx.register_component(
        logical_id="hedron-sample-kit:web-component.WebCallout",
        name="WebCallout",
        module="hedron_sample_kit.variants.web_component",
        distribution="hedron-sample-kit",
        props_model="WebCalloutProps",
        styles_path=str(_STYLES_PATH),
        folder_path=str(Path(__file__).resolve().parent),
        asset_roots=(str(_STATIC),),
        browser_modules=(str(_MODULE_PATH),),
        examples=("default",),
    )
