"""Reference primitive: hedron-disclosure."""

from __future__ import annotations

from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.registry import ElementFieldOwnership
from hedron_elements.markup import render_element_markup

ABI_VERSION = 1
TAG_NAME = "hedron-disclosure"
ELEMENT_ID = "hedron-disclosure"


class DisclosureProps(Props):
    summary: str = "Details"
    open: bool = False


class Disclosure(Component[DisclosureProps]):
    props_type = DisclosureProps
    logical_name = "Disclosure"
    distribution = "hedron-elements"

    def __init__(self, summary: str = "Details", *, open: bool = False, **kwargs: object) -> None:
        super().__init__(DisclosureProps(summary=summary, open=open, **kwargs))

    def render(self) -> NodeLike:
        return html.tag(TAG_NAME)(
            html.details(
                html.summary(self.props.summary),
                html.div(**{"data-hedron-server-region": "content"}),
                open=self.props.open or None,
            ),
            **{
                "data-hedron-abi": str(ABI_VERSION),
                "data-hedron-element": ELEMENT_ID,
                "summary": self.props.summary,
            },
        )

    def render_markup(self) -> str:
        return render_element_markup(
            tag_name=TAG_NAME,
            abi_version=ABI_VERSION,
            element_id=ELEMENT_ID,
            attributes={"summary": self.props.summary},
            server_content=self.props.summary,
        )


DISCLOSURE_OWNERSHIP: tuple[ElementFieldOwnership, ...] = (
    ElementFieldOwnership(name="open", mode="local", event="hedron-disclosure-change"),
)

DISCLOSURE_META = {
    "logical_id": ELEMENT_ID,
    "tag_name": TAG_NAME,
    "abi_version": ABI_VERSION,
    "module_asset_id": "hedron-elements:disclosure.mjs",
    "attributes": ("summary", "open"),
    "state_ownership": DISCLOSURE_OWNERSHIP,
    "events": ("hedron-disclosure-change",),
    "form_contract": None,
    "fallback": {"pre_upgrade": "native details visible", "js_off": "native details visible"},
}
