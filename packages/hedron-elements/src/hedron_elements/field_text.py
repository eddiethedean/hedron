"""Reference form element: hedron-field-text."""

from __future__ import annotations

from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.registry import ElementFieldOwnership
from hedron_elements.form_contracts import FIELD_TEXT_CONTRACT
from hedron_elements.markup import render_element_markup

ABI_VERSION = 1
TAG_NAME = "hedron-field-text"
ELEMENT_ID = "hedron-field-text"


class FieldTextProps(Props):
    name: str
    value: str = ""
    label: str | None = None
    required: bool = False
    disabled: bool = False
    input_type: str = "text"


class FieldText(Component[FieldTextProps]):
    props_type = FieldTextProps
    logical_name = "FieldText"
    distribution = "hedron-elements"

    def __init__(
        self,
        name: str,
        *,
        value: str = "",
        label: str | None = None,
        required: bool = False,
        disabled: bool = False,
        input_type: str = "text",
        **kwargs: object,
    ) -> None:
        super().__init__(
            FieldTextProps(
                name=name,
                value=value,
                label=label,
                required=required,
                disabled=disabled,
                input_type=input_type,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs = {
            "data-hedron-abi": str(ABI_VERSION),
            "data-hedron-element": ELEMENT_ID,
            "name": self.props.name,
            "value": self.props.value,
        }
        if self.props.label:
            attrs["label"] = self.props.label
        if self.props.required:
            attrs["required"] = "true"
        if self.props.disabled:
            attrs["disabled"] = "true"
        if self.props.input_type != "text":
            attrs["input-type"] = self.props.input_type
        return html.tag(TAG_NAME)(
            html.input(
                type=self.props.input_type,
                name=self.props.name,
                value=self.props.value,
                required=self.props.required or None,
                disabled=self.props.disabled or None,
                **{"data-hedron-server-region": "control"},
            ),
            **attrs,
        )

    def render_markup(self) -> str:
        attrs: dict[str, str] = {
            "name": self.props.name,
            "value": self.props.value,
        }
        if self.props.label:
            attrs["label"] = self.props.label
        if self.props.required:
            attrs["required"] = "true"
        if self.props.disabled:
            attrs["disabled"] = "true"
        if self.props.input_type != "text":
            attrs["input-type"] = self.props.input_type
        return render_element_markup(
            tag_name=TAG_NAME,
            abi_version=ABI_VERSION,
            element_id=ELEMENT_ID,
            attributes=attrs,
            server_content=self.props.value,
        )


FIELD_TEXT_OWNERSHIP: tuple[ElementFieldOwnership, ...] = (
    ElementFieldOwnership(name="value", mode="controlled", event="hedron-field-change"),
    ElementFieldOwnership(name="invalid", mode="controlled"),
)

FIELD_TEXT_META = {
    "logical_id": ELEMENT_ID,
    "tag_name": TAG_NAME,
    "abi_version": ABI_VERSION,
    "module_asset_id": "hedron-elements:field-text.mjs",
    "attributes": ("name", "value", "label", "required", "disabled", "input-type"),
    "state_ownership": FIELD_TEXT_OWNERSHIP,
    "events": ("hedron-field-change",),
    "form_contract": FIELD_TEXT_CONTRACT,
    "fallback": {"pre_upgrade": "native input visible", "js_off": "native input visible"},
}
