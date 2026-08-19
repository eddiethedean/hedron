"""Reference form element: hedron-field-file."""

from __future__ import annotations

from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.registry import ElementFieldOwnership
from hedron_core.typing_aliases import HtmlAttrMap
from hedron_elements.form_contracts import FIELD_FILE_CONTRACT
from hedron_elements.markup import render_element_markup

ABI_VERSION = 1
TAG_NAME = "hedron-field-file"
ELEMENT_ID = "hedron-field-file"


class FieldFileProps(Props):
    name: str = "file"
    accept: str | None = None
    multiple: bool = False
    required: bool = False
    disabled: bool = False
    label: str = "Upload file"


class FieldFile(Component[FieldFileProps]):
    props_type = FieldFileProps
    logical_name = "FieldFile"
    distribution = "hedron-elements"

    def __init__(
        self,
        *,
        name: str = "file",
        accept: str | None = None,
        multiple: bool = False,
        required: bool = False,
        disabled: bool = False,
        label: str = "Upload file",
        **kwargs: object,
    ) -> None:
        super().__init__(
            FieldFileProps(
                name=name,
                accept=accept,
                multiple=multiple,
                required=required,
                disabled=disabled,
                label=label,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs: HtmlAttrMap = {
            "type": "file",
            "name": self.props.name,
            "required": self.props.required or None,
            "disabled": self.props.disabled or None,
            **{"data-hedron-server-region": "control"},
        }
        if self.props.accept:
            attrs["accept"] = self.props.accept
        if self.props.multiple:
            attrs["multiple"] = True
        return html.tag(TAG_NAME)(
            html.label(self.props.label, html.input(**attrs)),
            **{
                "data-hedron-abi": str(ABI_VERSION),
                "data-hedron-element": ELEMENT_ID,
                "name": self.props.name,
            },
        )

    def render_markup(self) -> str:
        return render_element_markup(
            tag_name=TAG_NAME,
            abi_version=ABI_VERSION,
            element_id=ELEMENT_ID,
            attributes={
                "name": self.props.name,
                **({"accept": self.props.accept} if self.props.accept else {}),
                **({"multiple": "true"} if self.props.multiple else {}),
                **({"required": "true"} if self.props.required else {}),
                **({"disabled": "true"} if self.props.disabled else {}),
            },
            server_content=self.props.label,
        )


FIELD_FILE_OWNERSHIP: tuple[ElementFieldOwnership, ...] = (
    ElementFieldOwnership(name="files", mode="local", event="hedron-field-change"),
)

FIELD_FILE_META = {
    "logical_id": ELEMENT_ID,
    "tag_name": TAG_NAME,
    "abi_version": ABI_VERSION,
    "module_asset_id": "hedron-elements:field-file.mjs",
    "attributes": ("name", "accept", "multiple", "required", "disabled"),
    "state_ownership": FIELD_FILE_OWNERSHIP,
    "events": ("hedron-field-change",),
    "form_contract": FIELD_FILE_CONTRACT,
    "fallback": {"pre_upgrade": "native file input visible", "js_off": "native file input visible"},
}
