"""Reference primitive: hedron-dialog."""

from __future__ import annotations

from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.registry import ElementFieldOwnership
from hedron_elements.markup import render_element_markup

ABI_VERSION = 1
TAG_NAME = "hedron-dialog"
ELEMENT_ID = "hedron-dialog"


class DialogProps(Props):
    title: str = "Dialog"
    open: bool = False


class Dialog(Component[DialogProps]):
    props_type = DialogProps
    logical_name = "Dialog"
    distribution = "hedron-elements"

    def __init__(self, title: str = "Dialog", *, open: bool = False, **kwargs: object) -> None:
        super().__init__(DialogProps(title=title, open=open, **kwargs))

    def render(self) -> NodeLike:
        return html.tag(TAG_NAME)(
            html.dialog(
                html.h2(self.props.title),
                html.div(**{"data-hedron-server-region": "content"}),
                open=self.props.open or None,
            ),
            **{
                "data-hedron-abi": str(ABI_VERSION),
                "data-hedron-element": ELEMENT_ID,
                "title": self.props.title,
            },
        )

    def render_markup(self) -> str:
        attrs = {"title": self.props.title}
        if self.props.open:
            attrs["open"] = "true"
        return render_element_markup(
            tag_name=TAG_NAME,
            abi_version=ABI_VERSION,
            element_id=ELEMENT_ID,
            attributes=attrs,
            server_content=self.props.title,
        )


DIALOG_OWNERSHIP: tuple[ElementFieldOwnership, ...] = (
    ElementFieldOwnership(name="open", mode="local", event="hedron-dialog-change"),
)

DIALOG_META = {
    "logical_id": ELEMENT_ID,
    "tag_name": TAG_NAME,
    "abi_version": ABI_VERSION,
    "module_asset_id": "hedron-elements:dialog.mjs",
    "attributes": ("title", "open"),
    "state_ownership": DIALOG_OWNERSHIP,
    "events": ("hedron-dialog-change",),
    "form_contract": None,
    "fallback": {"pre_upgrade": "native dialog visible", "js_off": "native dialog visible"},
}
