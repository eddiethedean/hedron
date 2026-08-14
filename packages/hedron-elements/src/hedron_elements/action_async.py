"""Reference InteractionState element: hedron-action-async."""

from __future__ import annotations

from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.registry import ElementFieldOwnership
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrMap
from hedron_elements.markup import render_element_markup

ABI_VERSION = 1
TAG_NAME = "hedron-action-async"
ELEMENT_ID = "hedron-action-async"


class ActionAsyncProps(Props):
    label: str = "Run"
    hx_post: SafeUrl | None = None


class ActionAsync(Component[ActionAsyncProps]):
    props_type = ActionAsyncProps
    logical_name = "ActionAsync"
    distribution = "hedron-elements"

    def __init__(
        self,
        label: str = "Run",
        *,
        hx_post: SafeUrl | str | None = None,
        **kwargs: object,
    ) -> None:
        url = (
            hx_post
            if isinstance(hx_post, SafeUrl) or hx_post is None
            else SafeUrl.parse(str(hx_post), purpose=UrlPurpose.NAVIGATION)
        )
        super().__init__(ActionAsyncProps(label=label, hx_post=url, **kwargs))

    def render(self) -> NodeLike:
        btn_attrs: HtmlAttrMap = {"type": "button", "data-hedron-server-region": "control"}
        tag_attrs: HtmlAttrMap = {
            "data-hedron-abi": str(ABI_VERSION),
            "data-hedron-element": ELEMENT_ID,
        }
        if self.props.hx_post is not None:
            btn_attrs["hx-post"] = self.props.hx_post
            tag_attrs["hx-post"] = str(self.props.hx_post)
        return html.tag(TAG_NAME)(html.button(self.props.label, **btn_attrs), **tag_attrs)

    def render_markup(self) -> str:
        attrs = {"label": self.props.label}
        if self.props.hx_post is not None:
            attrs["hx-post"] = str(self.props.hx_post)
        return render_element_markup(
            tag_name=TAG_NAME,
            abi_version=ABI_VERSION,
            element_id=ELEMENT_ID,
            attributes=attrs,
            server_content=self.props.label,
        )


ACTION_ASYNC_OWNERSHIP: tuple[ElementFieldOwnership, ...] = (
    ElementFieldOwnership(name="state", mode="controlled", event="hedron-action-change"),
)

ACTION_ASYNC_META = {
    "logical_id": ELEMENT_ID,
    "tag_name": TAG_NAME,
    "abi_version": ABI_VERSION,
    "module_asset_id": "hedron-elements:action-async.mjs",
    "attributes": ("label", "hx-post", "hx-target"),
    "state_ownership": ACTION_ASYNC_OWNERSHIP,
    "events": ("hedron-action-change",),
    "form_contract": None,
    "resources": (
        "hedron-elements:bridge.mjs",
        "hedron-elements:interaction-state.mjs",
    ),
    "fallback": {"pre_upgrade": "button visible", "js_off": "button visible"},
}
