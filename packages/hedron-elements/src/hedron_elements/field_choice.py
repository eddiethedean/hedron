"""Reference form element: hedron-field-choice."""

from __future__ import annotations

from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.registry import ElementFieldOwnership
from hedron_elements.form_contracts import FIELD_CHOICE_CONTRACT
from hedron_elements.markup import render_element_markup

ABI_VERSION = 1
TAG_NAME = "hedron-field-choice"
ELEMENT_ID = "hedron-field-choice"


class FieldChoiceProps(Props):
    name: str
    options: tuple[tuple[str, str], ...]
    value: tuple[str, ...] = ()
    choice_type: str = "checkbox"
    required: bool = False
    disabled: bool = False


class FieldChoice(Component[FieldChoiceProps]):
    props_type = FieldChoiceProps
    logical_name = "FieldChoice"
    distribution = "hedron-elements"

    def __init__(
        self,
        name: str,
        options: tuple[tuple[str, str], ...] | list[tuple[str, str]],
        *,
        value: tuple[str, ...] | list[str] = (),
        choice_type: str = "checkbox",
        required: bool = False,
        disabled: bool = False,
        **kwargs: object,
    ) -> None:
        super().__init__(
            FieldChoiceProps(
                name=name,
                options=tuple((str(v), str(label)) for v, label in options),
                value=tuple(str(v) for v in value),
                choice_type=choice_type,
                required=required,
                disabled=disabled,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        selected = set(self.props.value)
        inputs = []
        for val, label in self.props.options:
            inputs.append(
                html.label(
                    html.input(
                        type=self.props.choice_type,
                        name=self.props.name,
                        value=val,
                        checked=val in selected or None,
                        disabled=self.props.disabled or None,
                        required=self.props.required or None,
                    ),
                    " ",
                    label,
                )
            )
        return html.tag(TAG_NAME)(
            *inputs,
            **{
                "data-hedron-abi": str(ABI_VERSION),
                "data-hedron-element": ELEMENT_ID,
                "name": self.props.name,
                "choice-type": self.props.choice_type,
            },
        )

    def render_markup(self) -> str:
        attrs = {"name": self.props.name, "choice-type": self.props.choice_type}
        if self.props.required:
            attrs["required"] = "true"
        if self.props.disabled:
            attrs["disabled"] = "true"
        return render_element_markup(
            tag_name=TAG_NAME,
            abi_version=ABI_VERSION,
            element_id=ELEMENT_ID,
            attributes=attrs,
            server_content=self.props.name,
        )


FIELD_CHOICE_OWNERSHIP: tuple[ElementFieldOwnership, ...] = (
    ElementFieldOwnership(name="value", mode="controlled", event="hedron-field-change"),
)

FIELD_CHOICE_META = {
    "logical_id": ELEMENT_ID,
    "tag_name": TAG_NAME,
    "abi_version": ABI_VERSION,
    "module_asset_id": "hedron-elements:field-choice.mjs",
    "attributes": ("name", "choice-type", "required", "disabled"),
    "state_ownership": FIELD_CHOICE_OWNERSHIP,
    "events": ("hedron-field-change",),
    "form_contract": FIELD_CHOICE_CONTRACT,
    "fallback": {"pre_upgrade": "native inputs visible", "js_off": "native inputs visible"},
}
